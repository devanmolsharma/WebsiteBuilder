import json
from .functions.CodeTypes.HtmlWithTailwindCssDjango import writeCode
from .functions.imageFunctions import loadImage
from .functions.detection import detectPageElements
from .functions.layoutDetection import findChildren
import os


def parseImage(imageUrl: str, outputPath: str, resourcesPath: str):
    # load the image
    img = loadImage(imageUrl)
    size = img.shape
    # break it into "Media", "Text" and "SolidColor" objects
    elements = detectPageElements(img, "./weights/websites_yolo.pt", 0.1)

    nestedData = findChildren(
        [*elements["Media"], *elements["Text"], *elements["SolidColor"]],
        img,
        resourcesPath,
    )

    json.dump(nestedData, open(resourcesPath + "/layout.json", "w"))

    writeCode(outputPath, nestedData, size)
    # create assets zip
    os.system(f"zip -r {resourcesPath}/assets.zip {resourcesPath}")
