from typing import Any
import numpy as np
from .layoutUtilities import (
    groupElementsIntoFlexCol,
    groupElementsIntoFlexRow,
    sortElementsByPosition,
)
from .imageFunctions import getMostCommonColor, saveImage
from .inpainting import inpaint, getBg


def findChildren(
    elements: list[dict[str, Any]],
    image: np.ndarray,
    resourcesPath: str,
    flexLoopCount: int = 5,
):
    # Add an error threshold as the bounding boxes are not precise
    ERROR_THRESHOLD = 20  # in px;

    # Add an id to each element for identification purposes
    for i, element in enumerate(elements):
        element["id"] = i
        element["position"] = element["position"].tolist()

    for i, element in enumerate(elements):
        parentPos = element["position"]
        element["children"] = []
        # get all elements that are within the boundaries of this element
        #  those elements are its children
        for other_element in elements:
            if element["id"] == other_element["id"]:
                continue
            childPos = other_element["position"]
            if isOneComponentInsideOther(parentPos, childPos, ERROR_THRESHOLD):
                element["children"].append(other_element["id"])

    # Do mutations needed for media elements
    elements = processMediaElements(elements, resourcesPath)
    # Shed duplicate parents
    elements = shedDuplicateParents(elements)
    # pprint(elements)
    elements = normaliseSize(elements, list(image.shape))

    nestedElements = convertToNestedMap(elements)
    nestedElements = setPostionsToRelative(nestedElements)

    for i in range(flexLoopCount):
        # group elements in flex rows and columns
        nestedElements = groupElementsIntoFlexRow(nestedElements, image.shape)
        nestedElements = groupElementsIntoFlexCol(nestedElements, image.shape)

    # Sort by position
    nestedElements = sortElementsByPosition(nestedElements)

    return {
        "type": "SolidColor",
        "childComponents": nestedElements,
        "position": [0, 0, 1, 1],
        "color": getMostCommonColor(image),
        "id": "-1",
    }


# check if one element is inside another element
def isOneComponentInsideOther(parentPosition, otherPosition, errorThreshold) -> bool:
    [x1, y1, x2, y2] = parentPosition
    [x1_c, y1_c, x2_c, y2_c] = otherPosition

    # Case 1: Expanding both sides horizontally (x-axis)
    if (
        x1 <= (x1_c + errorThreshold)
        and x2 >= (x2_c - errorThreshold)
        and y1 <= y1_c
        and y2 >= y2_c
    ):
        return True

    # Case 2: Expanding both sides vertically (y-axis)
    if (
        x1 <= x1_c
        and x2 >= x2_c
        and y1 <= (y1_c + errorThreshold)
        and y2 >= (y2_c - errorThreshold)
    ):
        return True

    # Case 3: Expanding top and left (upper-left diagonal)
    if (
        x1 <= (x1_c + errorThreshold)
        and x2 >= x2_c
        and y1 <= (y1_c + errorThreshold)
        and y2 >= y2_c
    ):
        return True

    # Case 4: Expanding bottom and right (lower-right diagonal)
    if (
        x1 <= x1_c
        and x2 >= (x2_c - errorThreshold)
        and y1 <= y1_c
        and y2 >= (y2_c - errorThreshold)
    ):
        return True

    # Case 5: Expanding top and right (upper-right diagonal)
    if (
        x1 <= x1_c
        and x2 >= (x2_c - errorThreshold)
        and y1 <= (y1_c + errorThreshold)
        and y2 >= y2_c
    ):
        return True

    # Case 6: Expanding bottom and left (lower-left diagonal)
    if (
        x1 <= (x1_c + errorThreshold)
        and x2 >= x2_c
        and y1 <= y1_c
        and y2 >= (y2_c - errorThreshold)
    ):
        return True

    return False


# This function makes sure that each chld has only one parent
#  if there are multiple parents, closest one is kept and rest of them are "shed out"
def shedDuplicateParents(elements: list[dict[str, Any]]):
    # For each chld count number of parents
    for child in elements:
        parents = []
        # get all parents
        for parent in elements:
            if child["id"] in parent["children"]:
                parents.append(parent)

        if len(parents):
            # get number of children of each parent
            children = [len(parent["children"]) for parent in parents]
            # The parent with hte least children is the true  parent of this child
            trueParent = parents[np.argmin(children)]

            # for rest of the parents, remove this child from their list
            for el in elements:
                for parent in parents:
                    if el["id"] == parent["id"]:
                        if parent["id"] != trueParent["id"]:
                            el["children"].remove(child["id"])

    return elements


def convertToNestedMap(elements: list[dict[str, Any]]):
    childrenIds = []

    # get all elements which are child of other elements
    for element in elements:
        element["childComponents"] = []
        for childId in element["children"]:
            element["childComponents"].append(elements[childId])
            childrenIds.append(childId)

    newElements = []
    # keep the elements which are not a child
    for element in elements:
        if element["id"] not in childrenIds:
            del element["children"]
            newElements.append(element)

    return newElements


# Do mutations needed for the media elements
def processMediaElements(elements: list[dict[str, Any]], resourcesPath: str):
    for i, element in enumerate(elements):
        if element["type"] != "Media":
            continue

        img = element["image"]  # np.ndarray of image pixels
        imShape = img.shape

        # take the background mask, and if the image is small,uses it to remove background
        if imShape[0] < 150 and imShape[1] < 150:
            mask = getBg(img)
            img = np.concat(
                [img, mask.reshape([img.shape[0], img.shape[1], 1])], axis=-1
            )

        # inpaint positions whre other lements are present
        elif len(element["children"]) != 0:
            positions = []
            parentPos = element["position"]
            # get all positions whre children are present
            for childId in element["children"]:
                child = elements[childId]
                childPos = child["position"]
                positions.append(getRelativePosition(parentPos, childPos, 5))

            # remove children from the source image
            img = inpaint(img, positions)

        # Save image to storage
        saveImage(img, f'{resourcesPath}/{element["description"].replace(' ','_')}.png')
        # remove image pixels from object as it's no longer needed
        del elements[i]["image"]
        # Add image location to the object
        elements[i]["image_url"] = f'{element["description"].replace(' ','_')}.png'
    return elements


# converts the child's position to relative to the parent's position
def getRelativePosition(parentPos: list[int], childPos: list[int], expandChildBy=0):
    [px1, py1, px2, py2] = parentPos
    [cx1, cy1, cx2, cy2] = childPos
    h = cy2 - cy1
    w = cx2 - cx1

    return [
        min([max([cx1 - px1 - expandChildBy, 0]), px2 - w]),
        min([max([cy1 - py1 - expandChildBy, 0]), py2 - h]),
        min([max([cx2 - px1 + expandChildBy, 0]), px2]),
        min([max([cy2 - py1 + expandChildBy, 0]), py2]),
    ]


# this function normalizes the positions of the elements between 0 and 1.
def normaliseSize(elements: list[dict[str, Any]], imageSize: list[int]):
    for i in range(0, len(elements)):
        elements[i]["position"] = roundPosition(
            normailsePosition(elements[i]["position"], imageSize)
        )
    return elements


def setPostionsToRelative(
    elements: list[dict[str, Any]], basePostition: list[int] = [0, 0, 1, 1]
):
    for i in range(len(elements)):
        elements[i]["childComponents"] = setPostionsToRelative(
            elements[i]["childComponents"], elements[i]["position"]
        )

        elements[i]["position"] = getRelativePosition(
            basePostition, elements[i]["position"]
        )
    return elements


# takes in a position and normalises it between 0 and 1
def normailsePosition(position: list[int], imageSize: list[int]):
    [px1, py1, px2, py2] = position
    [image_height, image_width, _] = imageSize
    ratio = image_height / image_width

    return [
        px1 / image_width,
        py1 * ratio / image_height,
        px2 / image_width,
        py2 * ratio / image_height,
    ]


def roundPosition(position: list[float], precision: int = 3):
    return np.round(position, precision).tolist()
