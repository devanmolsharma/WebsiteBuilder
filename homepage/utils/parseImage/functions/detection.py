from typing import Any
import yolov9
import numpy as np
from onnxtr.models import ocr_predictor
from .imageFunctions import getImagePortion, getMostCommonColor
from .nlp import getCaption


# this function returns various elements in the image
def detectPageElements(
    image: np.ndarray, modelPath: str, score_threshold=0.1, smallImagePadding=20
) -> dict[str, list[dict[str, Any]]]:

    # Load the yolo model
    model = yolov9.load(
        modelPath,
        device="cpu",
    )

    # model parameters
    model.conf = score_threshold  # NMS confidence threshold
    model.iou = 0.2  # NMS IoU threshold
    model.classes = None

    res = model(image)
    predictions = res.pred[0]

    final: dict = {"Media": [], "SolidColor": [], "Text": []}
    final["Text"] = detectText(image)

    # item [0-3] are x1, y1, x2, y2
    # item [4] is score
    # item [5] is class predicted
    for item in predictions:
        if item[5] == 0:
            [x1, y1, x2, y2] = item[:4]
            h = y2 - y1
            w = x2 - x1
            if h > 150 or w > 150:
                cropped_img = getImagePortion(image, np.array([x1, y1, x2, y2]))
            else:
                # add some padding around the image if its very small
                cropped_img = getImagePortion(
                    image,
                    np.array(
                        [
                            np.max([x1 - smallImagePadding, 1]),
                            np.max([y1 - smallImagePadding, 1]),
                            x2 + smallImagePadding,
                            y2 + smallImagePadding,
                        ]
                    ),
                )

            final["Media"].insert(
                0,
                {
                    "type": "Media",
                    "image": cropped_img,  # get portion of image where the class is found
                    "description": getCaption(cropped_img),  # caption the image
                    "position": item[:4],
                },
            )  # insert appropriate data to the final array
        else:
            final["SolidColor"].insert(
                0,
                {
                    "type": "SolidColor",
                    "color": getMostCommonColor(
                        getImagePortion(image, item[:4])
                    ),  # get color of portion of image where the class is found
                    "position": item[:4],
                },
            )  # insert appropriate data to the final array

    return final


# this detects text from the image
def detectText(image: np.ndarray, confidence=0.01):
    [h, w, c] = image.shape

    model = ocr_predictor(
        det_arch="db_mobilenet_v3_large",  # detection architecture
        reco_arch="vitstr_base",  # recognition architecture
        det_bs=2,  # detection batch size
        reco_bs=512,  # recognition batch size
        symmetric_pad=False,
    )
    # Analyze
    result = model([image])
    lines = result.export()["pages"][0]["blocks"][0]["lines"]
    finalLines = []

    # get details for each line
    for line in lines:
        ((x1, y1), (x2, y2)) = line["geometry"]
        lineText = " ".join([wordObj["value"] for wordObj in line["words"]])
        size = len(lineText)
        lfontSize = (x2 - x1) / size
        groupWords = True  # do all words belong to a single line

        for i in range(len(line["words"]) - 1):
            ((_, _), (tx2, _ty11)) = line["words"][i]["geometry"]
            ((_tx1, _), (_, _ty21)) = line["words"][i + 1]["geometry"]

            # If gap between the words is larger than the font size, they are most probably not in a line
            if (
                (((_tx1 - tx2)) - lfontSize) > 0.03
                or ((_tx1 - tx2)) > 0.05
                or (abs(_ty11 - _ty21)) > 0.02
            ):
                groupWords = False

        if groupWords:
            position = np.array([x1 * w, y1 * h, x2 * w, y2 * h])
            if len(lineText) <= 2:
                continue
            finalLines.append(
                {
                    "type": "Text",
                    "position": position,
                    "color": detectTextColor(image, position),
                    "text": lineText,
                    "fontSize": float(lfontSize) * 1.5,
                }
            )

        else:
            for wordObj in line["words"]:
                ((wx1, wy1), (wx2, wy2)) = wordObj["geometry"]
                position = np.array([wx1 * w, wy1 * h, wx2 * w, wy2 * h])
                value = wordObj["value"]
                size = len(value)
                wfontSize = (wx2 - wx1) / size
                if len(value) <= 2:
                    continue
                finalLines.append(
                    {
                        "type": "Text",
                        "position": position,
                        "color": detectTextColor(image, position),
                        "text": value,
                        "fontSize": float(wfontSize) * 1.5,
                    }
                )

    return finalLines


def detectTextColor(img: np.ndarray, pos: np.ndarray):
    x1, y1, x2, y2 = pos

    # Add boundary checks to avoid out-of-bounds error
    x1 = max(0, x1 - 3)
    y1 = max(0, y1 - 3)
    x2 = min(img.shape[1], x2 + 3)
    y2 = min(img.shape[0], y2 + 3)

    # Extract the image portion
    imgPortion = img[int(y1) : int(y2), int(x1) : int(x2)]

    # Reshape the image to a 2D array of pixels
    pixels = imgPortion.reshape(-1, 3)

    # Round pixel values to the nearest 10
    pixels = (np.round(pixels / 10) * 10).astype(int)

    # Count the occurrences of each unique rounded pixel-RGB combination
    unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)

    # Find the most frequent color (background color)
    most_frequent_color_index = np.argmax(counts)
    background_color = unique_colors[most_frequent_color_index]

    # Compute contrast for each unique color with the background color
    contrast = np.linalg.norm(unique_colors - background_color, axis=1)

    # Find the color that contrasts the most with the background (likely text color)
    most_contrasting_color_index = np.argmax(contrast)

    # Return the most contrasting color (likely text color)
    return unique_colors[most_contrasting_color_index].tolist()
