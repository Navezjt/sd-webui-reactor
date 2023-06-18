from typing import List, Union, Dict, Set, Tuple

from transformers import AutoFeatureExtractor
import torch
from PIL import Image, ImageFilter
import numpy as np

def numpy_to_pil(images: np.ndarray) -> List[Image.Image]:
    if images.ndim == 3:
        images = images[None, ...]
    images = (images * 255).round().astype("uint8")
    pil_images = [Image.fromarray(image) for image in images]

    return pil_images


def check_image(x_image: np.ndarray) -> Tuple[np.ndarray, List[bool]]:
    global safety_feature_extractor, safety_checker
    return x_image, False


def check_batch(x: torch.Tensor) -> torch.Tensor:
    x_samples_ddim_numpy = x.cpu().permute(0, 2, 3, 1).numpy()
    x_checked_image = x_samples_ddim_numpy
    x = torch.from_numpy(x_checked_image).permute(0, 3, 1, 2)
    return x


def convert_to_sd(img: Image) -> Image:
    return img
