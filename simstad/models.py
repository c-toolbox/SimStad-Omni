import os
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from colorfield.fields import ColorField
from .utils import (
    generate_minimap,
    generate_thumbnail,
    generate_video_minimap,
    generate_video_thumbnail,
    ensure_image_size,
)


# A VisualCity installation
class City(models.Model):
    class Meta:
        verbose_name = "City exhibit"
        verbose_name_plural = "   City exhibits"
        ordering = ["key"]

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique identifier for the city",
    )

    name = models.CharField(
        max_length=64,
        help_text="Name of the city",
    )

    service = models.ForeignKey(
        "communication.Service",
        on_delete=models.SET_NULL,
        null=True,
        help_text="WebSocket service the city exhibit uses",
    )

    min_x = models.FloatField(
        default=130000, help_text="Minimum X coordinate (SWEREF 99 TM)"
    )
    min_y = models.FloatField(
        default=6400000, help_text="Minimum Y coordinate (SWEREF 99 TM)"
    )
    max_x = models.FloatField(
        default=140000, help_text="Maximum X coordinate (SWEREF 99 TM)"
    )
    max_y = models.FloatField(
        default=6500000, help_text="Maximum Y coordinate (SWEREF 99 TM)"
    )

    default_blocks_video = models.CharField(
        max_length=255,
        blank=True,
        help_text="Default Blocks video that plays when no data is shown",
    )

    def __str__(self):
        return self.key


# Specifically chosen collections to be displayed in a City exhibition
class FeaturedCollection(models.Model):
    city = models.ForeignKey(
        "City",
        on_delete=models.CASCADE,
        related_name="featured_collections",
    )
    collection = models.ForeignKey(
        "Collection",
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Collections featured on the exhibition start page",
    )
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order"]
        unique_together = [["city", "collection"]]

    def __str__(self):
        return f"{self.city.key} → {self.collection.key}"


# A collection of scenarios that follow a theme
class Collection(models.Model):
    class Meta:
        verbose_name = "Collection"
        verbose_name_plural = "   Collections"
        ordering = ["key"]

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique identifier for the collection",
    )

    name = models.CharField(
        max_length=64,
        help_text="Name of the collection",
    )

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="collections",
        help_text="The city the collection belongs to",
    )

    blocks_video = models.CharField(
        max_length=255,
        blank=True,
        help_text="Blocks video associated with the collection",
    )

    image = models.ImageField(
        upload_to="collections/",
        help_text="Image file for the collection",
    )

    scenarios = models.ManyToManyField(
        "Scenario",
        through="CollectionScenario",
        related_name="collections",
    )

    def __str__(self):
        return self.key


class CollectionScenario(models.Model):
    class Meta:
        unique_together = ("collection", "scenario")
        ordering = ["order"]

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    scenario = models.ForeignKey("Scenario", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, editable=True, db_index=True)

    def __str__(self):
        return self.scenario.key


class Scenario(models.Model):
    class Meta:
        verbose_name = "Scenario"
        verbose_name_plural = "   Scenarios"
        ordering = ["key"]

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique identifier for the scenario",
    )

    name = models.CharField(
        max_length=64,
        help_text="Name of the scenario",
    )

    short_name = models.CharField(
        max_length=32,
        blank=True,
        default="",
        help_text="Optional short name of the scenario, used for tabs in the UI",
    )

    description = models.TextField(
        help_text="Description of the scenario",
    )

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="scenarios",
        help_text="The city the collection belongs to",
    )

    rasters = models.ManyToManyField(
        "Raster",
        through="Layer",
        through_fields=("scenario", "raster"),
        related_name="scenarios",
    )

    legend = models.ForeignKey(
        "Legend",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Legend associated with the scenario. Provide either a legend or a legend image, not both.",
    )

    legend_image = models.ImageField(
        upload_to="legends/",
        null=True,
        blank=True,
        help_text="Image file for the legend. Provide either a legend or a legend image, not both.",
    )

    legend_image_source = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="Source information for the legend image.",
    )

    LAYER_DISPLAY_MODES = [
        ("stacked", "Stacked"),
        ("sequential", "Sequential"),
    ]

    layer_display_mode = models.CharField(
        max_length=16,
        choices=LAYER_DISPLAY_MODES,
        default="stacked",
        help_text="Determine whether layers are stacked or shown sequentially",
    )

    def __str__(self):
        return self.key


class Layer(models.Model):
    class Meta:
        ordering = ["order"]
        verbose_name = "Layer"
        verbose_name_plural = "Layers"

    # Layer Type (Discriminator)
    LAYER_TYPE_CHOICES = [
        ("image", "Image"),
        ("flow", "Flow"),
        ("movie", "Movie"),
        ("color", "Color"),
        ("ndi", "NDI"),
    ]

    type = models.CharField(
        max_length=16,
        choices=LAYER_TYPE_CHOICES,
        default="image",
        db_index=True,
        help_text="Layer type",
    )

    scenario = models.ForeignKey(
        "Scenario",
        on_delete=models.CASCADE,
        related_name="layers",
        help_text="The scenario this layer belongs to.",
    )

    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Rendering order within the scenario.",
    )

    opacity = models.FloatField(
        default=1.0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Transparency",
    )

    emission = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        help_text="Self-illumination",
    )

    # Crop Fields (Discriminated by crop_type)
    CROP_CHOICES = [
        ("none", "No Crop"),
        ("slice", "Slice Crop"),
        ("circle", "Circle Crop"),
    ]

    crop_type = models.CharField(
        max_length=10,
        choices=CROP_CHOICES,
        default="none",
        help_text="Cropping",
    )

    # Slice Crop
    crop_min_u = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    crop_max_u = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    crop_min_v = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    crop_max_v = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )

    # Circle Crop
    crop_center_u = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    crop_center_v = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    crop_radius = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )

    # Image Layer Fields
    raster = models.ForeignKey(
        "Raster",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="layers",
        help_text="Raster image used by image layers.",
    )

    # Flow Layer Fields
    flow_texture = models.ForeignKey(
        "Raster",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="flow_layers",
        help_text="Secondary raster used as texture for flow layers.",
    )
    flow_scale = models.FloatField(null=True, blank=True, default=1.0)
    flow_speed = models.FloatField(null=True, blank=True, default=1.0)

    # Movie Layer Fields
    movie_speed = models.FloatField(
        null=True,
        blank=True,
        default=1.0,
        help_text="Playback speed of the movie layer.",
    )

    # Color Layer Fields
    color = ColorField(
        default="#FFFFFF",
        null=True,
        blank=True,
        help_text="Solid color for color layers.",
    )

    # NDI Layer Fields
    ndi_stream = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="NDI stream name.",
    )
    ndi_machine = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="Optional NDI machine name.",
    )

    def get_crop_data(self):
        if self.crop_type == "slice":
            return {
                "type": "slice",
                "slice": {
                    "min_u": self.crop_min_u,
                    "max_u": self.crop_max_u,
                    "min_v": self.crop_min_v,
                    "max_v": self.crop_max_v,
                },
            }
        elif self.crop_type == "circle":
            return {
                "type": "circle",
                "circle": {
                    "u": self.crop_center_u,
                    "v": self.crop_center_v,
                    "radius": self.crop_radius,
                },
            }
        return None

    RASTER_REQUIRED_TYPES = {"image", "flow", "movie"}

    def clean(self):
        if self.type in {"image", "flow", "movie"} and not self.raster:
            raise ValidationError(
                {"raster": f"{self.type.capitalize()} layers require a raster."}
            )

        if self.type == "flow" and not self.flow_texture:
            raise ValidationError(
                {"flow_texture": "Flow layers require a flow texture raster."}
            )
        if self.type == "flow" and self.flow_texture.media_type != "image":
            raise ValidationError(
                {
                    "flow_texture": "Flow texture must reference a raster of type 'image'."
                }
            )

        if self.type == "ndi" and not self.ndi_stream:
            raise ValidationError({"ndi_stream": "NDI layers require a stream name."})

        if self.raster:
            if self.type == "image" and self.raster.media_type != "image":
                raise ValidationError(
                    {"raster": "Image layers must reference a raster of type 'image'."}
                )

            if self.type == "flow" and self.raster.media_type != "image":
                raise ValidationError(
                    {"raster": "Flow layers must reference a raster of type 'image'."}
                )

            if self.type == "movie" and self.raster.media_type != "video":
                raise ValidationError(
                    {"raster": "Movie layers must reference a raster of type 'video'."}
                )

    @property
    def name(self):
        if self.type in ["image", "flow", "movie"]:
            return self.raster.key
        if self.type == "color":
            return self.color
        if self.type == "ndi":
            return self.ndi_stream
        return f"{self.scenario.key} - {self.raster.key}"

    def __str__(self):
        return f"{self.type} - {self.name}"


def upload_raster(instance, filename):
    base, ext = os.path.splitext(filename)
    new_filename = f"{instance.key}{ext.lower()}"
    return f"rasters/{new_filename}"

def upload_video(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"videos/{instance.key}{ext}"


class Raster(models.Model):
    class Meta:
        verbose_name = "Raster"
        verbose_name_plural = "  Rasters"
        ordering = ["key"]

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(
        max_length=64,
        unique=True,
        help_text="Unique identifier for the raster",
    )

    name = models.CharField(
        max_length=64,
        help_text="Name of the raster",
    )

    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description about the raster — what data it contains, its source, etc.",
    )

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        help_text="The city the raster belongs to",
        related_name="rasters",
    )

    tags = models.ManyToManyField(
        "Tag",
        related_name="rasters",
        blank=True,
        help_text="Tags associated with the raster.",
    )

    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    media_type = models.CharField(
        max_length=8,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
        db_index=True,
    )

    video = models.FileField(
        upload_to=upload_video,
        null=True,
        blank=True,
        help_text="MP4 video file (only for video rasters)",
    )

    image = models.ImageField(upload_to=upload_raster, null=True, blank=True)
    minimap = models.ImageField(upload_to="minimaps/", null=True, blank=True)
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_key = self.key
        self._old_image = self.image

    def clean(self):
        if self.media_type == self.MediaType.IMAGE:
            if not self.image:
                raise ValidationError({"image": "Image rasters require an image file."})
            if self.video:
                raise ValidationError({"video": "Image rasters cannot have a video."})

        if self.media_type == self.MediaType.VIDEO:
            if not self.video:
                raise ValidationError({"video": "Video rasters require a video file."})
            if self.image:
                raise ValidationError({"image": "Video rasters cannot have an image."})

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        key_changed = self.key != self._old_key and self._old_key

        super().save(*args, **kwargs)

        if self.media_type == self.MediaType.IMAGE:
            self._handle_image(key_changed, is_new)

        elif self.media_type == self.MediaType.VIDEO:
            self._handle_video(key_changed, is_new)

        self._old_key = self.key

    def _handle_image(self, key_changed, is_new):
        if not self.image:
            return

        image_changed = self.image != self._old_image and self._old_image
        self._old_image = self.image

        if is_new or image_changed or key_changed:
            if key_changed and not image_changed:
                self.rename_image()

            self.generate_minimap()
            self.generate_thumbnail()

            super().save(update_fields=["image", "minimap", "thumbnail"])

    def _handle_video(self, key_changed, is_new):
        if not self.video:
            return

        if key_changed:
            self.rename_video()

        self.generate_video_thumbnail()
        self.generate_video_minimap()

        super().save(update_fields=["video", "thumbnail", "minimap"])

    def rename_image(self):
        os.rename(self.image.path, self.get_output_path("rasters"))
        self.image.name = self.get_output_relpath("rasters")

    def rename_video(self):
        os.rename(self.video.path, self.get_output_path("videos"))
        self.video.name = self.get_output_relpath("videos")

    def generate_minimap(self):
        print("--- generate_minimap")
        minimap = generate_minimap(self.media.path)
        path = self.get_output_path("minimaps")
        minimap.save(path, format="PNG")
        self.minimap.name = self.get_output_relpath("minimaps")

    def generate_thumbnail(self):
        thumbnail = generate_thumbnail(self.media.path)
        path = self.get_output_path("thumbnails")
        thumbnail.save(path, format="PNG")
        self.thumbnail.name = self.get_output_relpath("thumbnails")

    def generate_video_thumbnail(self):
        thumbnail = generate_video_thumbnail(self.media.path)
        thumbnail_path = self.get_output_path("thumbnails").replace(".mp4", ".png")
        thumbnail.save(thumbnail_path, format="PNG")
        self.thumbnail.name = self.get_output_relpath("thumbnails").replace(
            ".mp4", ".png"
        )

    def generate_video_minimap(self):
        minimap = generate_video_minimap(self.media.path)
        minimap_path = self.get_output_path("minimaps").replace(".mp4", ".png")
        minimap.save(minimap_path, format="PNG")
        self.minimap.name = self.get_output_relpath("minimaps").replace(".mp4", ".png")


    def get_output_path(self, folder):
        ext = self.get_extension()
        path = self.media.path
        folder_path = os.path.abspath(os.path.join(os.path.dirname(path), "..", folder))
        os.makedirs(folder_path, exist_ok=True)
        return os.path.join(folder_path, f"{self.key}{ext}")

    def get_output_relpath(self, folder):
        ext = self.get_extension()
        return os.path.join(folder, f"{self.key}{ext}")

    def get_extension(self):
        return os.path.splitext(self.media.name)[1].lower()

    @property
    def media(self):
        print("--- media type", self.media_type)
        if self.media_type == "image":
            return self.image
        elif self.media_type == "video":
            return self.video
        else:
            raise Exception("Unintended behavior")

    def __str__(self):
        return self.key


class Tag(models.Model):
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique identifier for the tag",
    )

    name = models.CharField(
        max_length=32,
        unique=True,
        help_text="Name of the tag",
    )

    def __str__(self):
        return self.key


class Legend(models.Model):
    class Meta:
        verbose_name = "Legend"
        verbose_name_plural = " Legends"
        ordering = ["key"]

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(
        max_length=64,
        unique=True,
        help_text="Unique identifier for the legend",
    )

    title = models.CharField(max_length=64)

    def __str__(self):
        return self.key


class LegendSymbol(models.Model):
    class Meta:
        verbose_name = "Symbol"
        verbose_name_plural = " Symbols"
        ordering = ["key"]

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(max_length=32)

    image = models.ImageField(upload_to="legendsymbols/")

    def clean(self):
        super().clean()
        ensure_image_size(self.image)

    def __str__(self):
        return self.key


class LegendEntry(models.Model):
    class Meta:
        verbose_name = "Legend entry"
        verbose_name_plural = " Legend entries"
        ordering = ["order"]

    legend = models.ForeignKey(Legend, on_delete=models.CASCADE, related_name="entries")
    text = models.CharField(max_length=64)
    color = ColorField(default="#FFFFFF")
    symbol = models.ForeignKey(LegendSymbol, on_delete=models.PROTECT)
    order = models.PositiveIntegerField(default=0, editable=True, db_index=True)

    def __str__(self):
        return self.text


class SequenceLabel(models.Model):
    class Meta:
        verbose_name = "Sequence label"
        verbose_name_plural = " Sequence labels"
        ordering = ["order"]

    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="sequence_labels")
    text = models.CharField(max_length=64)
    order = models.PositiveIntegerField(default=0, editable=True, db_index=True)

    def __str__(self):
        return self.text


# Localized strings for UI text that doesn't belong to any specific object
class LocalizedString(models.Model):
    class Meta:
        verbose_name = "Localize String"
        verbose_name_plural = "Localized Strings"
        ordering = ["key"]

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(
        max_length=128,
        unique=True,
        help_text="Unique identifier for the localized string",
    )

    text = models.TextField(help_text="The localized text")

    def __str__(self):
        return self.key
