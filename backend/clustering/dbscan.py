from sklearn.cluster import DBSCAN
import numpy as np
import os

def dbscan(
    embeddings: np.ndarray,
    min_samples: int = 5,
    eps: float = 0.7,
    metric: str = 'cosine'
) -> np.ndarray:
    # Im using cosine distance, since embeddings are a vector representation of the face
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric=metric).fit(embeddings)
    return clustering.labels_

            
    
    
if __name__ == "__main__":
    from data.load import Meta, parse_info
    import cv2
    # parse embeddings
    meta = parse_info("assets/embeddings")
    # cluster the embeddings
    import pdb; pdb.set_trace()
    labels = dbscan(meta.get_embeddings())
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
        # if label == -1 "use undefined"
        if label == -1:
            label = "undefined"
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
    
    print("Drawing bboxs for undefined labels, wait 1 minute")
    # create bbox image for every undefined label
    for idx, res in enumerate(labels_dict.get(-1, [])):
        img_path, bbox = res
        img_name = img_path.split("/")[-1]
        img = cv2.imread(img_path)
        x1, y1, x2, y2 = bbox.astype(int)
        img_bbox = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.imwrite(f"data/clusters/undefined/{idx}_{img_name}", cv2.resize(img_bbox, (640, 640)))