from PIL import Image
from moviepy.editor import VideoFileClip
from django.core.exceptions import ValidationError


# Photoshop the full raster image into a 256x256 thumbnail
def generate_thumbnail(image_path):
    with Image.open(image_path) as image:
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

        final_image = scaled_image.copy()
    return final_image


# Photoshop the full raster image into a 730x548 minimap
def generate_minimap(image_path):
    with Image.open(image_path) as image:
        # Cropped image of above dimension
        new_width = 730
        new_height = int(730 * (3849 / 5120))
        scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        final_image = scaled_image.copy()
    return final_image


# Checks that the uploaded image is of a particular size
def ensure_image_size(image_path):
    if image_path:
        img = Image.open(image_path)
        width, height = img.size

        if width != 128 or height != 64:
            raise ValidationError(
                f"Image must be exactly 128×64 px, but is {width}×{height}."
            )


# Generates a 256x256 thumbnail for a video
def generate_video_thumbnail(video_path):
    with VideoFileClip(video_path) as clip:
        frame = clip.get_frame(clip.duration / 2)
        image = Image.fromarray(frame)

        # Same crop logic as your image thumbnail
        width, height = image.size
        new_size = min(width, height)
        cx, cy = width / 2, height / 2

        left = round(cx - new_size / 2)
        top = round(cy - new_size / 2)
        right = round(cx + new_size / 2)
        bottom = round(cy + new_size / 2)

        cropped_image = image.crop((left, top, right, bottom))
        scaled_image = cropped_image.resize((256, 256), Image.Resampling.LANCZOS)

        return scaled_image


# Generate a 730x548 minimap for a video
def generate_video_minimap(video_path):
    with VideoFileClip(video_path) as clip:
        frame = clip.get_frame(clip.duration / 2)
        image = Image.fromarray(frame)

        new_width = 730
        aspect_ratio = image.height / image.width
        new_height = int(new_width * aspect_ratio)
        scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return scaled_image
