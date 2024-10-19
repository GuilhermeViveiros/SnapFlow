import cv2
import numpy as np
import os   
import logging
import insightface
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image
import pyheif
from PIL import Image
import ffmpeg


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
    

# convert MOV to mp4
def convert_mov_to_mp4(input_folder: str, output_folder: str):
    """
    Convert MOV files in the input folder to MP4 format and save them in the output folder.

    Args:
        input_folder (str): Path to the folder containing MOV files.
        output_folder (str): Path to the folder where MP4 files will be saved.

    Returns:
        None
    """
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get all MOV files in the input folder
    mov_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.MOV') or f.lower().endswith('.mov')]
    
    for mov_file in mov_files:
        input_path = os.path.join(input_folder, mov_file)
        output_path = os.path.join(output_folder, os.path.splitext(mov_file)[0] + '.mp4')

        try:
            (
                ffmpeg
                .input(input_path)
                .output(output_path, vcodec='libx264', acodec='aac')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            print(f"Successfully converted {input_path} to {output_path}")
        except ffmpeg.Error as e:
            print(f"Error converting {input_path} to {output_path}: {e.stderr.decode()}")
    
    
if __name__ == "__main__":
    # convert_heic_to_jpeg("data/images", "data/images")
    convert_mov_to_mp4("data/images/", "data/images")

