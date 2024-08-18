import cv2
import numpy as np
import os   
import logging
import insightface
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image
import pyheif
from PIL import Image



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



# convert heic to jpeg
def convert_heic_to_jpeg(folder, out_folder) -> None:
    # get the images
    images = os.listdir(folder)
    #  support types
    image_extensions = [".HEIC"]
    # process the images in batches
    for _, image in enumerate(images):
        if not any(image.endswith(ext) for ext in image_extensions):
            print(f"Skipping {image} because it is not an HEIC image")
            continue

        # open the image
        img = open_heic_image(os.path.join(folder, image))
        # save the image in rgb format
        cv2.imwrite(os.path.join(out_folder, image.replace(".HEIC", ".jpg")), cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        #import pdb; pdb.set_trace()
    

    
if __name__ == "__main__":
    convert_heic_to_jpeg("data/images", "data/images")

