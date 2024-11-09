import cv2
import numpy as np
import os   
from typing import List, Tuple
import logging
import insightface
from dataclasses import dataclass
from insightface.app import FaceAnalysis
import pyheif
from PIL import Image
import torch
import ffmpeg
#from insightface.app import Face

logger = logging.getLogger("snapflow")


# Function to open and convert HEIC to numpy array
def open_heic_image(heic_file_path) -> np.ndarray:
    heif_file = pyheif.read(heic_file_path)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    # convert to numpy array
    return np.array(image)
    
# load image
def load_image(image: str, folder: str) -> np.ndarray:
    # if image is a HEIC, convert it to JPEG
    if image.endswith(".HEIC"):
        img = open_heic_image(os.path.join(folder, image))
    else:
        img = cv2.imread(os.path.join(folder, image))
    return img

# use a face detection model (insightface, buffalo_l) to extract the face embeddings
def extract_face_embeddings_from_image(app: FaceAnalysis, img: np.ndarray) -> List[np.ndarray]:
    # get the faces
    faces = app.get(img)
    return faces

# since we are using a vector database, we need to convert every image to a vector representation
def extract_face_embeddings_from_folder(folder: str, out_folder: str, draw: bool = False) -> None:
    # load the model
    app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    # prepare the model
    app.prepare(ctx_id=0, det_size=(640, 640))
    # get the images
    images = os.listdir(folder)
    #  support types
    image_extensions = [".jpg", ".jpeg", ".png", ".HEIC"]
    # process the images in batches
    for _, image in enumerate(images):
        if not any(image.endswith(ext) for ext in image_extensions):
            logger.info(f"Skipping {image} because it is not an image")
            continue

        _img = load_image(image, folder)
        # extract the face embeddings
        faces = extract_face_embeddings_from_image(app, _img)
        # save bbox and embeddings to a numpy file
        # if no faces are detected, save an empty array
        if len(faces) == 0:
            np.save(os.path.join(out_folder, image + '.npy'), {'faces': []})
        else:
            np.save(os.path.join(out_folder, image + '.npy'), {'faces': faces})
        # if draw, save the image
        if draw:
            # draw the faces on the image
            rimg = app.draw_on(_img, res)
            # save the image
            cv2.imwrite(os.path.join(out_folder, image) + '.jpg', rimg)

# extract the face given bbox
def extract_face_from_image(file_path: str, bbox: List[int], save_path: str, margin: float = 0.2) -> np.ndarray:
    # load the image
    if os.path.exists(file_path):
        img = cv2.imread(file_path)
    else:
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    # extract the face with increased margin
    x1, y1, x2, y2 = bbox.astype(int)
    height, width = img.shape[:2]
    
    # Calculate margin in pixels
    margin_x = int((x2 - x1) * margin)
    margin_y = int((y2 - y1) * margin)
    
    # Adjust coordinates with margin, ensuring they stay within image bounds
    x1 = max(0, x1 - margin_x)
    y1 = max(0, y1 - margin_y)
    x2 = min(width, x2 + margin_x)
    y2 = min(height, y2 + margin_y)
    
    # extract the face
    face = img[y1:y2, x1:x2]
    
    if save_path:
        # save the face
        cv2.imwrite(save_path, face)
    
    return face
    
if __name__ == "__main__":
    # extract the face embeddings
    extract_face_embeddings_from_folder("data/images", "data/embeddings")
