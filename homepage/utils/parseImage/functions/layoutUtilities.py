from typing import Any
import numpy as np


# Function to calculate the average gap between elements in a sorted list based on positions.
def getGap(sortedList: list, index1: int = 2, index2: int = 0):
    gapTotal = 0
    for i in range(len(sortedList) - 1):
        el1 = sortedList[i]
        el2 = sortedList[i + 1]
        e2_1 = el1["position"][
            index1
        ]  # Get the position of x2 (or y2 for columns) of element 1
        e1_2 = el2["position"][
            index2
        ]  # Get the position of x1 (or y1 for columns) of element 2
        gap = abs(e1_2 - e2_1)  # Calculate the gap between two adjacent elements
        if gap > 0:
            gapTotal += gap
    return gapTotal / len(sortedList)  # Return the average gap


# Function to group elements into Flexbox rows based on their relative positions.
def groupElementsIntoFlexRow(
    children: list[dict[str, Any]], shape: Any, THRESHOLD=0.02
):
    # Create a copy of the list of children
    childList = [child for child in children]
    (h, w, _) = shape  # Unpack the height and width from the shape

    if len(childList) == 0:
        return []

    # Recursively group child components within each element
    for i, child in enumerate(childList):
        if child["type"] == "Flexbox":
            continue
        if len(child["childComponents"]) > 0:
            childList[i]["childComponents"] = groupElementsIntoFlexRow(
                child["childComponents"], shape, THRESHOLD
            )

    flexBoxes = []  # To store flexbox row groups

    # Loop through each child and check if it can be part of a flexbox row
    for child in children:
        [x1, y1, x2, y2] = child[
            "position"
        ]  # Extract the position of the child element
        flexBox: dict = {"childComponents": []}
        count = 0
        flexChildren = []
        MIN_DIFF = x2 - x1  # Minimum width of the child element
        height = y2 - y1  # Height of the child element

        for otherChild in childList:
            [cx1, cy1, cx2, cy2] = otherChild["position"]
            cheight = cy2 - cy1  # Calculate height of the other child

            # Check if the other child's height is within tolerance and aligned on the same row
            if np.abs(height - cheight) > 0.02:
                continue
            if np.abs(y1 - cy1) < THRESHOLD and np.abs(cx1 - x1) > MIN_DIFF:
                # Check if the other child is positioned to the right or left of the current child
                if cx1 > x2:
                    count += 1
                    flexChildren.append(otherChild)
                elif x1 > cx2:
                    count += 1
                    flexChildren.append(otherChild)

        # If more than one child is aligned in a row, group them into a flexbox
        if count > 1:
            for child in flexChildren:
                child["isFlex"] = True  # Mark as part of a flexbox
                childList.remove(child)  # Remove the child from the original list
            flexBox["childComponents"] = flexChildren
            flexBox["type"] = "Flexbox"
            flexBox["id"] = f"fb{flexChildren[0]["id"]}"
            flexBox["orientation"] = "row"  # Set the orientation to row

            # Sort the child components by their x1 position to arrange them in a row
            sortedList = sorted(
                flexBox["childComponents"], key=lambda x: x["position"][0]
            )
            first = sortedList[0]["position"]  # Get the first element's position
            last = sortedList[-1]["position"]  # Get the last element's position

            # Define the flexbox position and gap between children
            flexBox["position"] = [first[0], first[1], last[2], last[3]]
            flexBox["gap"] = getGap(sortedList, 2, 0)
            flexBox["childComponents"].sort(key=lambda x: x["position"][0])
            flexBoxes.append(flexBox)

    return [
        *flexBoxes,
        *childList,
    ]  # Return both flexboxes and remaining ungrouped elements


# Function to group elements into Flexbox columns based on their relative positions.
def groupElementsIntoFlexCol(
    children: list[dict[str, Any]], shape: Any, THRESHOLD=0.02
):
    # Create a copy of the list of children
    childList = [child for child in children]
    (h, w, _) = shape  # Unpack the height and width from the shape

    if len(childList) == 0:
        return []

    # Recursively group child components within each element
    for i, child in enumerate(childList):
        if child["type"] == "Flexbox":
            continue
        if len(child["childComponents"]) > 0:
            childList[i]["childComponents"] = groupElementsIntoFlexCol(
                child["childComponents"], shape
            )

    flexBoxes = []  # To store flexbox column groups

    # Loop through each child and check if it can be part of a flexbox column
    for child in children:
        [x1, y1, x2, y2] = child[
            "position"
        ]  # Extract the position of the child element
        flexBox: dict = {"childComponents": []}
        count = 0
        flexChildren = []
        MIN_DIFF = y2 - y1  # Minimum height of the child element
        width = x2 - x1  # Width of the child element

        for otherChild in childList:
            [cx1, cy1, cx2, cy2] = otherChild["position"]
            cwidth = cx2 - cx1  # Calculate width of the other child

            # Check if the other child's width is within tolerance and aligned in the same column
            if np.abs(width - cwidth) > 0.02:
                continue
            if np.abs(cx1 - x1) < THRESHOLD and np.abs(cy1 - y1) > MIN_DIFF:
                # Check if the other child is positioned above or below the current child
                if cy1 > y2:
                    count += 1
                    flexChildren.append(otherChild)
                elif y1 > cy2:
                    count += 1
                    flexChildren.append(otherChild)

        # If more than one child is aligned in a column, group them into a flexbox
        if count > 1:
            for child in flexChildren:
                child["isFlex"] = True  # Mark as part of a flexbox
                childList.remove(child)  # Remove the child from the original list
            flexBox["childComponents"] = flexChildren
            flexBox["type"] = "Flexbox"
            flexBox["orientation"] = "column"  # Set the orientation to column
            flexBox["id"] = f"fb{flexChildren[0]["id"]}"

            # Sort the child components by their y1 position to arrange them in a column
            sortedList = sorted(
                flexBox["childComponents"], key=lambda x: x["position"][1]
            )
            first = sortedList[0]["position"]  # Get the first element's position
            last = sortedList[-1]["position"]  # Get the last element's position

            # Define the flexbox position and gap between children
            flexBox["gap"] = getGap(sortedList, 3, 1)
            flexBox["position"] = [first[0], first[1], last[2], last[3]]
            flexBox["childComponents"].sort(key=lambda x: x["position"][1])
            flexBoxes.append(flexBox)

    return [
        *flexBoxes,
        *childList,
    ]


from typing import Any, List


def sortElementsByPosition(children: List[dict[str, Any]]):
    for i, child in enumerate(children):
        if len(child["childComponents"]) > 0:
            children[i]["childComponents"] = sortElementsByPosition(
                child["childComponents"]
            )
    return sorted(
        children,
        key=lambda child: (child["position"][1], child["position"][0]),
    )
