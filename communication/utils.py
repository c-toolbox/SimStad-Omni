import uuid
from PIL import Image


def is_uuid(text):
    try:
        uuid.UUID(str(text))
        return True
    except ValueError:
        return False


def explain_websocket_code(code):
    close_codes = {
        1000: "Successful operation / regular socket shutdown",
        1001: "Client is leaving (browser tab closing)",
        1002: "Endpoint received a malformed frame",
        1003: "Endpoint received an unsupported frame (e.g. binary-only endpoint received text frame)",
        1004: "Reserved",
        1005: "Expected close status, received none",
        1006: "No close code frame has been receieved",
        1007: "Endpoint received inconsistent message (e.g. malformed UTF-8)",
        1008: "Generic code used for situations other than 1003 and 1009",
        1009: "Endpoint won't process large frame",
        1010: "Client wanted an extension which server did not negotiate",
        1011: "Internal server error while operating",
        1012: "Server/service is restarting",
        1013: "Temporary server condition forced blocking client's request",
        1014: "Server acting as gateway received an invalid response",
        1015: "Transport Layer Security handshake failure",
        4000: "Kicked by new host",
    }
    if code in close_codes:
        return close_codes[code]
    return f"Unknown: {code}"


# Photoshop the full raster image into a 256x256 thumbnail
def generate_thumbnail(image_path):
    image = Image.open(image_path)

    # Setting the points for cropped image
    width, height = image.size
    new_size = min(width, height)
    cx = width / 2
    cy = height / 2

    left = round(cx - new_size / 2)
    top = round(cy - new_size / 2)
    right = round(cx + new_size / 2)
    bottom = round(cy + new_size / 2)

    # Cropped image of above dimension
    cropped_image = image.crop((left, top, right, bottom))
    scaled_image = cropped_image.resize((256, 256), Image.Resampling.LANCZOS)

    return scaled_image


# Photoshop the full raster image into a 730x548 minimap
def generate_minimap(image_path):
    image = Image.open(image_path)

    # Setting the points for cropped image
    width, height = image.size

    # Cropped image of above dimension
    new_width = 730
    new_height = int(730 * (3849 / 5120))
    scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return scaled_image
