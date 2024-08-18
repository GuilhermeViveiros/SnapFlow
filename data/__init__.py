# init folder, images, embeddings, output if not exists
import os

if not os.path.exists("data/images"):
    os.makedirs("data/images")
if not os.path.exists("data/embeddings"):
    os.makedirs("data/embeddings")
if not os.path.exists("data/output"):
    os.makedirs("data/output")