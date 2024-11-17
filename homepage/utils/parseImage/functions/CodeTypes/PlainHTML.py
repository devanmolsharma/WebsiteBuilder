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
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
        <link href="./output.css" rel="stylesheet">
            
    </head>
    <body>
        {code}
    </body>
    </html>
                
                """
        )


def rgb_to_hex(color: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])


def jsonToCode(json: dict[str, Any], shape: Any) -> str:
    type = json["type"]
    children = json.get("childComponents", [])

    # Recursively handle child components
    child_components_code = "".join([jsonToCode(child, shape) for child in children])

    # Handle each case based on type
    match type:
        case "Media":
            return (
                f"<div id={json['id']}>"
                f"{child_components_code}"
                f'<img src="./{json["image_url"]}" />'
                "</div>"
            )

        case "SolidColor":
            color = rgb_to_hex(json["color"])
            return (
                f'<div id={json['id']} style="background-color: {color};">'
                f"{child_components_code}</div>"
            )

        case "Text":
            color = rgb_to_hex(json["color"])
            text = json.get("text", "")

            return (
                f'<div id={json['id']} style="color: {color};">'
                f"{text}{child_components_code}</div>"
            )

        case "Flexbox":
            return f"<div id={json['id']}>" f"{child_components_code}</div>"

    # Default return for unknown types
    return ""
