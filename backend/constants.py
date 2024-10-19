import os

# Database
DATABASE_URL = 'sqlite:///snapflow.db'  # Replace with your actual database URL

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'backend/assets', 'images')

# Image processing
SUPPORTED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".PNG"]

# Face analysis
FACE_DETECTION_SIZE = (640, 640)

# Other constants can be added here as neededuu