# SnapFlow

<p align="center">
  <img src="snapflow.png" alt="SnapFlow">
</p>

SnapFlow aims to sync photos in real-time not only between devices but between users


SnapFlow aims to level up Photos by providing intelligent photo organization, real-time syncing, and seamless sharing not only between devices but between users. 

## Features

- Intelligent photo organization and labeling
- Automatic person identification and labeling
- Photo sharing between users
- Local database storage for photos and metadata
- Real-time photo syncing between devices


## How It Works

1. Aggregate different persons from the photos and ask the user to label them
2. For any subsequent photo, if the identified targets are already labeled, SnapFlow will sync between users

The following sections describe the features of SnapFlow in detail

### Data Population

At the current stage, data population in SnapFlow is a manual process that requires several steps:

1. Place your photos in the `assets` directory
2. Run the face detection and embedding extraction scripts to generate embeddings
3. Execute the database population script which:
   - Processes each image and its associated embeddings
   - Performs DBSCAN clustering to group similar faces together
   - Creates Person entries in the database for each unique cluster
   - Associates photos with the identified persons
   - Extracts and saves face crops for each person

The database population process analyzes face embeddings across all photos to identify unique individuals. It uses DBSCAN clustering to group similar faces together, creating a Person entry for each cluster. This allows SnapFlow to maintain consistent person identification across the photo collection.

Note: In future versions, this process will be automated and happen in real-time as photos are added to the system. For now, the manual population step is required to set up the initial database.


To populate the database with photo and person data, you need to run the `populate_db.py` script. This script processes images, extracts face embeddings, performs clustering, and stores the information in the database. Note that this process is not real-time and needs to be executed manually.


Before populating the database, you need to generate face embeddings for your photos. This is done using the `process.py` script which detects faces and extracts embeddings for each face found.

To run the script, use the following command:

```bash
cd backend
python data/process.py
```

Now you can populate the database with the following command:

```bash
python populate_db.py
```

## Running the Backend

To run the backend, use the following command:

```bash
python main.py
```

## Running the Frontend

To run the frontend, use the following command:

```bash
cd snapflow
yarn start
```

SnapFlow will be available at `http://localhost:8000` and will display the user interface for managing and viewing your photo collection. You can interact with the application to organize and label your photos.

# Future Work

- Real-time face detection and embedding extraction
- Real-time photo addition & photo labeling
- Expand to video processing
- Real-time photo syncing between devices
- Photo sharing between users

Contributions and feedback are welcome! If you have any ideas or suggestions for improving SnapFlow, please feel free to contribute to the project.

