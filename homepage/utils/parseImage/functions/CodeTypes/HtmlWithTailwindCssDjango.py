import math
from typing import Any


def writeCode(outfile: str, data: dict[str, Any], shape: Any):
    code = jsonToCode(data, shape)

    with open(outfile, "w") as file:
        file.write(
            f"""
                <!DOCTYPE html>
    <html lang="en">
    <head>
    {'{% load static %}'}
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
        <link href="{"{% static 'output.css' %}"}" rel="stylesheet">
            
    </head>
    <body>
        {code}
    </body>
    </html>
                
                """
        )


def getCode(data: dict[str, Any], shape: Any):
    code = jsonToCode(data, shape)

    return f"""
                <!DOCTYPE html>
    <html lang="en">
    <head>
    {'{% load static %}'}
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
        <link href="{"{% static 'output.css' %}"}" rel="stylesheet">
            
    </head>
    <body>
        {code}
    </body>
    </html>
                
                """


def rgb_to_hex(color: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])


def jsonToCode(json: dict[str, Any], shape: Any) -> str:
    type = json["type"]
    [x1, y1, x2, y2] = json["position"]
    children = json.get("childComponents", [])
    isFlex = json.get("isFlex", False)

    # Recursively handle child components
    child_components_code = "".join([jsonToCode(child, shape) for child in children])

    # Calculate position and size in vw
    top = math.floor(y1 * 1000) / 10
    left = math.floor(x1 * 1000) / 10
    w = math.floor((x2 - x1) * 1000) / 10
    h = math.floor((y2 - y1) * 1000) / 10

    position_class = f"top-[{top}vw] left-[{left}vw]" if not isFlex else ""
    size_class = f"w-[{w}vw] h-[{h}vw]"

    # Handle each case based on type
    match type:
        case "Media":
            return (
                f'<div class="{"relative" if isFlex else f"absolute {position_class}"} {size_class}">'
                f"{child_components_code}"
                "{% load static %}"
                f'<img src="{{% static \'{json["image_url"]}\' %}}" alt="{json.get("description", "")}" class="w-full h-full object-cover" />'
                "</div>"
            )

        case "SolidColor":
            w_float = x2 - x1
            h_float = y2 - y1
            elType, shouldClose = approximateElementType(
                json["color"], h_float, w_float, child_components_code
            )
            color = rgb_to_hex(json["color"])
            return (
                f'{'<div>' if not shouldClose else ''}<{elType} class="{"relative" if isFlex else f"absolute {position_class}"} {size_class} rounded-md '
                f'bg-[{color}]">'
                f"{child_components_code}"
                + ("</div>" if not shouldClose else f"</{elType}>")
            )

        case "Text":
            color = rgb_to_hex(json["color"])
            font_size = json.get("fontSize", 16)  # Default font size if not specified
            text = json.get("text", "")

            # Optimized font size class for common sizes
            font_size_class = (
                f"text-[{int(font_size * 1000) / 10}vw]"
                if font_size != 16
                else "text-base"
            )
            return (
                f'<div class="{"relative" if isFlex else f"absolute {position_class}"} {size_class} '
                f'flex text-[{color}] {font_size_class}">'
                f"{text}"  # {child_components_code}
                "</div>"
            )

        case "Flexbox":
            orientation = json.get("orientation", "row")  # Default to row
            gap = int(json.get("gap", 0.1) * 100)

            # Simplify the flex class
            flex_direction = "flex-row" if orientation == "row" else "flex-col"
            return (
                f'<div class="{"relative" if isFlex else f"absolute {position_class}"} {size_class} items-center '
                f'flex {flex_direction} gap-[{gap}vw]">'
                f"{child_components_code}</div>"
            )

    # Default return for unknown types
    return ""


# returns element type and if it requires a closing tag
def approximateElementType(color: list[int], h: float, w: float, childCode: str):
    (r, g, b) = color

    if (
        h < 0.04
        and w < 0.6
        and (
            (r > 200 and g > 200 and b > 200)
            or childCode.find("search") != -1
            or childCode.find("input") != -1
        )
    ):
        return "input type='text'", False

    if h < 0.2 and w <= 0.35:
        return "button", True

    return "div", True
