import os
from db.models import Base, Person, Photo, Cluster
import json
from data.process import extract_face_embeddings_from_image, load_image
from clustering.dbscan import dbscan
import numpy as np
from constants import DATABASE_URL, ASSETS_DIR, SUPPORTED_IMAGE_EXTENSIONS, FACE_DETECTION_SIZE
import pickle
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
            cluster_objects[label] = new_cluster
    return cluster_objects

def populate_db(sample_photos_dir:str=ASSETS_DIR):
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
        
        # Initialize embeddings list and filename mapping
        all_embeddings = []
        embedding_to_filename = {}
        
        # Collect all embeddings
        for filename in os.listdir(sample_photos_dir):
            if not any(filename.endswith(ext) for ext in SUPPORTED_IMAGE_EXTENSIONS):
                print(f"Skipping {filename} because it is not an image")
                continue
            
            # Load and process the image
            img = load_image(filename, sample_photos_dir)
            faces = extract_face_embeddings_from_image(app, img)
            
            for face in faces:
                all_embeddings.append(face.embedding)
                embedding_to_filename[tuple(face.embedding)] = filename

        # DBSCAN clustering
        all_embeddings_array = np.array(all_embeddings)
        cluster_labels = dbscan(all_embeddings_array)
        
        # Populate db with DBSCAN Clustering
        cluster_objects = populate_clusters(db, cluster_labels=cluster_labels, all_embeddings=all_embeddings_array)

        # Dictionary to store person objects
        person_objects = {}

        # Group embeddings by label
        label_to_embeddings = {}
        for embedding, label in zip(all_embeddings, cluster_labels):
            if label not in label_to_embeddings:
                label_to_embeddings[label] = []
            label_to_embeddings[label].append(embedding)
        
        # Process embeddings and create Person objects
        for label, embeddings in label_to_embeddings.items():
            new_person = Person(
                embeddings=pickle.dumps(embeddings)  # Serialize the embeddings
            )
            if label != -1:
                new_person.cluster = cluster_objects[label]
            # get an associated image filename
            new_person.filename = embedding_to_filename[tuple(embeddings[0])]
            db.add(new_person)
            for emb in embeddings:
                person_objects[tuple(emb)] = new_person

        # Create Photo objects and associate with Person objects
        for filename in os.listdir(sample_photos_dir):
            if not any(filename.endswith(ext) for ext in SUPPORTED_IMAGE_EXTENSIONS):
                continue
            
            # Read the image file and convert to binary
            # with open(os.path.join(sample_photos_dir, filename), "rb") as image_file:
            #    image_binary = image_file.read()
            
            new_photo = Photo(
                filename=filename,
                file_path=os.path.join(sample_photos_dir, filename),
                # photo_data=image_binary
            )
            db.add(new_photo)

            # Find all embeddings associated with this filename
            photo_embeddings = [
                emb for emb, fname in embedding_to_filename.items() if fname == filename
            ]
            
            # Associate the photo with the corresponding persons
            for emb in photo_embeddings:
                person = person_objects[emb]
                person.photos.append(new_photo)  # Use the relationship defined in the model

            # print(f"Processed {filename}")

        db.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_db()