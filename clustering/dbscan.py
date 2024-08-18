from sklearn.cluster import DBSCAN
import numpy as np
import os

def dsbcan(
    embeddings: np.ndarray,
    min_samples: int = 5,
    eps: float = 0.6,
    metric: str = 'cosine'
) -> np.ndarray:
    # Im using cosine distance, since embeddings are a vector representation of the face
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric=metric).fit(embeddings)
    return clustering.labels_ + 1

            
    
    
if __name__ == "__main__":
    from data.load import Meta, parse_info
    import cv2
    # parse embeddings
    meta = parse_info("data/embeddings")
    # cluster the embeddings
    labels = dsbcan(meta.get_embeddings())
    # get bboxs
    bboxs = meta.get_bbox()
    # get image paths
    img_paths = meta.get_image_paths()
    # for each label, print the number of elements
    for label in np.unique(labels):
        print(f"Label: {label}, Count: {np.sum(labels == label)}")
    
    labels_dict = {} 
    for label, bbox, img_path in zip(labels, bboxs, img_paths):
        if '.HEIC' in img_path:
            img_path = img_path.replace('.HEIC', '.jpg')
        labels_dict.setdefault(label, []).append((img_path, bbox))
        # print(f"Label: {label}, Path: {img_path}")

    # create folders for each label and copy the images to the folder
    for idx, (label, res) in enumerate(labels_dict.items()):
        print("Operating on label: ", label, "Count: ", len(res))
        os.makedirs(f"data/clusters/{label}", exist_ok=True)
        # copy the images to the folder
        for img_path, _ in res:
            os.system(f"cp {img_path} data/clusters/{label}")
    
    # create an associated image for each cluster
    for label, res in labels_dict.items():
        # randomly pick one image from the cluster
        idx = np.random.randint(0, len(res))
        img_path, bbox = res[idx]
        # extract the bbox from image
        img = cv2.imread(img_path)
        x1, y1, x2, y2 = bbox.astype(int)
        cv2.imwrite(f"data/clusters/{label}/0.jpg",cv2.resize(img[y1:y2, x1:x2], (640, 640)))
        