import cv2
import numpy as np
from rembg import remove


def inpaint(img: np.ndarray, postions: list):
    # create a mask with the same height and width as the image, with 3 channels
    mask = np.zeros([img.shape[0], img.shape[1], 3], dtype=np.uint8)

    for item in postions:
        [x1, y1, x2, y2] = item
        mask[int(y1) : int(y2), int(x1) : int(x2)] = (
            255  # This masks the top-left 10x10 region
        )

    # Apply inpainting to the image using the mask
    final = cv2.inpaint(
        img, cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY), 20, cv2.INPAINT_TELEA
    )
    return final


def getBg(img: np.ndarray) -> np.ndarray:
    return np.array(remove(img,only_mask=True))
