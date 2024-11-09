import os
from data.utils import extract_info_from_embedding_meta, get_metadata_path
from db.models import Base, Person, Photo, Cluster
import json
from data.process import extract_face_from_image
from clustering.dbscan import dbscan
import numpy as np
from constants import DATABASE_URL, ASSETS_DIR, SUPPORTED_IMAGE_EXTENSIONS, FACE_DETECTION_SIZE
import pickle
import random
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from insightface.app import FaceAnalysis


# Create database engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create database tables
Base.metadata.create_all(bind=engine)

def populate_clusters(db: Session, cluster_labels: np.ndarray, all_embeddings: np.ndarray):
    cluster_objects = {}
    for label in np.unique(cluster_labels):
        if label != -1:  # Ignore noise points
            cluster_mask = cluster_labels == label
            centroid = np.mean(all_embeddings[cluster_mask], axis=0)
            new_cluster = Cluster(centroid=centroid.tolist())
            db.add(new_cluster)
            db.flush()  # This will assign an ID to the new cluster
            cluster_objects[label] = {
                'cluster': new_cluster,
                'embeddings': all_embeddings[cluster_mask]
            }
    return cluster_objects

def populate_db(sample_photos_dir: str = ASSETS_DIR, embeddings_dir: str = "assets/embeddings"):
    """
    Populates the database with photo and person data from the given directory.
    It assumes the embeddings are already extracted and in the assets/embeddings directory.

    This function performs the following steps:
    1. Initializes the database session and face analysis model.
    2. Clears existing data from the database.
    3. Processes images in the given directory to extract face embeddings.
    4. Performs DBSCAN clustering on the extracted embeddings.
    5. Populates the database with cluster, person, and photo information.

    Args:
        sample_photos_dir (str): Path to the directory containing sample photos.
                                 Defaults to ASSETS_DIR.

    Returns:
        None
    """
    # Create database engine and session
    db = SessionLocal()

    # Initialize FaceAnalysis
    app = FaceAnalysis(providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=FACE_DETECTION_SIZE)
    
    try:
        # Clear existing data
        db.query(Photo).delete()
        db.query(Person).delete()
        db.query(Cluster).delete()
        db.commit()
        
        all_embeddings = []
        embedding_to_photo = {}
        
        # Collect all embeddings
        for filename in os.listdir(sample_photos_dir):
            if not any(filename.endswith(ext) for ext in SUPPORTED_IMAGE_EXTENSIONS):
                print(f"Skipping {filename} because it is not an image")
                continue
            
            # create an associated photo
            new_photo = Photo(
                filename=filename,
                file_path=os.path.join(sample_photos_dir, filename),
            )
            db.add(new_photo)

            # load the metadata associated with the img
            try:
                metadata = get_metadata_path(filename)
                meta = extract_info_from_embedding_meta(metadata)
            except EOFError:
                print(f"Error: The embedding associated with file {filename} is empty or corrupted.")
                continue
            except FileNotFoundError:
                print(f"Error: The embedding associated with file {filename} does not exist. Ignoring...")
                continue
            except Exception as e:
                raise Exception(f"Error: {e}")

            # get embeddings 
            bboxs, embeddings = meta.item().get('bbox'), meta.item().get('embeddings')
            
            for bbox, embedding in zip(bboxs, embeddings):
                all_embeddings.append(embedding)
                embedding_to_photo[tuple(embedding)] = {
                    'photo': new_photo,
                    'bbox': bbox
                }

        # DBSCAN clustering
        all_embeddings_array = np.array(all_embeddings)
        cluster_labels = dbscan(all_embeddings_array)
        
        # Populate db with DBSCAN Clustering
        cluster_objects = populate_clusters(db, cluster_labels=cluster_labels, all_embeddings=all_embeddings_array)
        
        # Process embeddings and create Person objects
        for label, meta in cluster_objects.items():
            # get the filename associated with the random embedding
            random_embedding = random.choice(meta['embeddings'])
            photo, bbox = embedding_to_photo[tuple(random_embedding)].values()
            # extract the face
            os.makedirs(f"data/clusters/{label}", exist_ok=True)
            img_crop_path = f"data/clusters/{label}/{photo.filename}"
            _ = extract_face_from_image(
                file_path=photo.file_path,
                bbox=bbox,
                save_path=img_crop_path
            )
            
            # create a new person
            new_person = Person(
                cluster_id=label,
                embeddings=pickle.dumps(meta['embeddings']),
                file_path="/"+img_crop_path,
                photos = [
                    embedding_to_photo[tuple(emb)]['photo'] for emb in meta['embeddings']
                ]
            )
            db.add(new_person)
            
        db.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_db()
