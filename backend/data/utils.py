import torch
import numpy as np
import os
from data.load import ImageMetadata

# select the device for computation
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(f"using device: {device}")

if device.type == "cuda":
    # use bfloat16 for the entire notebook
    torch.autocast("cuda", dtype=torch.bfloat16).__enter__()
    # turn on tfloat32 for Ampere GPUs (https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices)
    if torch.cuda.get_device_properties(0).major >= 8:
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
elif device.type == "mps":
    print(
        "\nSupport for MPS devices is preliminary. SAM 2 is trained with CUDA and might "
        "give numerically different outputs and sometimes degraded performance on MPS. "
        "See e.g. https://github.com/pytorch/pytorch/issues/84936 for a discussion."
    )

def extract_info_from_embedding_meta(embedding_file: str) -> ImageMetadata:
    meta = np.load(embedding_file, allow_pickle=True)
    return meta

def get_metadata_path(filename: str) -> str:
    # replace the extension with .npy if it exists
    if not filename.endswith(".npy"):
        filename = filename + ".npy"
    if not os.path.exists(os.path.join("assets/embeddings", filename)):
        raise FileNotFoundError(f"The file {filename} does not exist in the embeddings directory.")
    return os.path.join("assets/embeddings", filename)