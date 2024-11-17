from typing import Any
import numpy as np
from transformers import BlipProcessor, BlipForConditionalGeneration

processor: Any = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)


# get caption of the image
def getCaption(image: np.ndarray) -> str:
    text = "a screenshot of "  # this helps to steer caption in correct direction
    inputs = processor(image, text, return_tensors="pt")

    out = model.generate(**inputs)
    return (
        processor.decode(out[0], skip_special_tokens=True)
        .replace("a screenshot of ", "")
        .replace("'", "")
        .replace('"', "")
        + f" {round(np.random.uniform(0, 1), 2)}"
    )  # add random seed to caption
