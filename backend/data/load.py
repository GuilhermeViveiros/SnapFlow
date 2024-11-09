from dataclasses import dataclass
import numpy as np
import os
from typing import List
import logging

@dataclass
class VideoMetadata:
    video_path: str
    video_name: str
    video_id: str
    video_id_path: str
    embeddings: List[np.ndarray]

@dataclass
class ImageMetadata:
    embedding: np.ndarray
    embedding_path: str
    img_name: str
    img_path: str
    bbox: List[int]

@dataclass
class Meta:
    metadata: List[ImageMetadata]
    
    # iterate over the metadata
    def __iter__(self):
        for meta in self.metadata:
            yield meta

    # get embeddings
    def get_embeddings(self) -> List[np.ndarray]:
        return np.array([meta.embedding for meta in self.metadata])

    # get bbox
    def get_bbox(self) -> List[List[int]]:
        return [meta.bbox for meta in self.metadata]
    
    # get image paths
    def get_image_paths(self) -> List[str]:
        return [meta.img_path for meta in self.metadata]

def parse_info(folder: str) -> Meta:
    res = []
    for file in os.listdir(folder):
        # check if file is a numpy file
        if not file.endswith(".npy"):
            logging.info(f"Skipping {file} because it is not a numpy file")
            continue
        try:
            meta = np.load(os.path.join(folder, file), allow_pickle=True)
        except EOFError:
            print(f"Error: The file {file} is empty or corrupted.")
            continue
        bboxs, embeddings = meta.item().get('bbox'), meta.item().get('embeddings')
        emb_path = os.path.join(folder, file)
        img_folder = folder.replace("embeddings", "images")
        img_name = file.split(".npy")[0]
        for emb, bbox in zip(embeddings, bboxs):
            res.append(ImageMetadata(emb, emb_path, img_name, os.path.join(img_folder, img_name), bbox))
    return Meta(res)

if __name__ == "__main__":
    embeddings = parse_info("data/embeddings")
    print(embeddings)