from PIL import Image
import numpy as np


#  Loads the image and converts it to a numpy array
def loadImage(filename: str) -> np.ndarray:
    img = Image.open(filename)
    arr = np.array(img.convert("RGB"))
    img.close()
    return arr


# get portion of image inside the coordinates
def getImagePortion(image: np.ndarray, coordinates: np.ndarray) -> np.ndarray:
    [x1, y1, x2, y2] = coordinates

    return image[int(y1) : int(y2), int(x1) : int(x2)]


# Save image array to a file
def saveImage(image: np.ndarray, filename: str) -> None:
    img = Image.fromarray(image)
    img.save(filename)


def getMostCommonColor(image: np.ndarray):
    flat = image.reshape(-1, 3)  # Flatten the image array
    unique_colors, counts = np.unique(
        flat, axis=0, return_counts=True
    )  # Get unique colors and their counts
    try:
        ind = np.argmax(counts)  # Get the index of the most common color
        return unique_colors[ind].tolist()  # Return the most common color as a list
    except IndexError:  # Handle case where the image may be empty
        return [255, 255, 255]  # Default to white if no colors are found
