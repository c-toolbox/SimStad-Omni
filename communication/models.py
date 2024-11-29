import random, re, uuid, os
from django.db import models
from adminsortable.models import SortableMixin
from colorfield.fields import ColorField
from .utils import generate_minimap, generate_thumbnail


def generate_code():
    chars = list("ABCDEFGHIJKLMNOPQRSTUVXYZ")
    size = 4
    while True:
        random.shuffle(chars)
        code = "".join(chars[:size])
        if not Service.objects.filter(public_code=code).exists():
            return code


def safe_string(text):
    return re.sub(r"[^A-Za-z\d-]", "_", text).lower()


class Service(models.Model):
    # Creation date
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    # Title describing the service
    title = models.CharField(
        max_length=32,
        unique=True,
        default="",
        blank=False,
        help_text="Name of the service",
    )

    # Unique token for each service
    host_token = models.UUIDField(
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Token used to access this service as a host. Use this in the main application in the exhibit.",
    )

    # Unique token for each service
    client_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Token used to access this service as a client. Use this in the user interface display, if any",
    )

    # Boolean for public code generation
    allow_public_code = models.BooleanField(
        default=False,
        help_text="If enabled, the service will be accessible through a public code or link. A new code is generated everytime the host connects.",
    )

    # Boolean for multiple hosts
    allow_multiple_hosts = models.BooleanField(
        default=False,
        help_text="If enabled, the service allows multiple hosts to be connected at the same time. Otherwise, a new host kicks the older ones.",
    )

    # Unique code for visitors to join via
    public_code = models.CharField(
        max_length=8,
        null=True,
        default=None,
        help_text="The public code for guests to connect via. A new code is generated everytime the host connects.",
    )

    def generate_code(self):
        self.public_code = generate_code()
        self.save()
        return self.public_code

    def clear_code(self):
        self.public_code = None
        self.save()

    def __str__(self):
        return self.title

    @property
    def host_group(self):
        return "host_" + safe_string(self.title)

    @property
    def client_group(self):
        return "client_" + safe_string(self.title)

    @property
    def guest_group(self):
        return "guest_" + safe_string(self.title)


# A VisualCity installation
class City(models.Model):
    class Meta:
        verbose_name = "City exhibit"
        verbose_name_plural = "City exhibits"

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique identifier for the city",
    )

    name = models.CharField(
        max_length=32,
        help_text="Name of the city",
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        help_text="WebSocket service the city exhibit uses",
    )

    def __str__(self):
        return self.name


# A collection of scenarios that follow a theme
class Collection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique identifier for the collection",
    )

    name = models.CharField(
        max_length=32,
        help_text="Name of the collection",
    )

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        help_text="The city the collection belongs to",
    )

    blocks_video = models.CharField(
        max_length=255,
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
        return self.name


class CollectionScenario(SortableMixin):
    class Meta:
        unique_together = ("collection", "scenario")
        ordering = ["order"]

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    scenario = models.ForeignKey("Scenario", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        return self.scenario.key
        # return f"{self.collection.key}_{self.scenario.key}"


class Scenario(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique identifier for the scenario",
    )

    name = models.CharField(
        max_length=32,
        help_text="Name of the scenario",
    )

    description = models.TextField(
        help_text="Description of the scenario",
    )

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        help_text="The city the collection belongs to",
    )

    rasters = models.ManyToManyField(
        "Raster",
        through="ScenarioRaster",
        related_name="scenarios",
    )

    # Legend: LegendTitle+LegendColors, LegendImage, LegendSource
    # Interaction: None, Buttons, Slider

    # class YearInSchool(models.TextChoices):
    #     FRESHMAN = 'FR', _('Freshman')
    #     SOPHOMORE = 'SO', _('Sophomore')
    #     JUNIOR = 'JR', _('Junior')
    #     SENIOR = 'SR', _('Senior')
    #     GRADUATE = 'GR', _('Graduate')

    # year_in_school = models.CharField(
    #     max_length=2,
    #     choices=YearInSchool.choices,
    #     default=YearInSchool.FRESHMAN,
    # )

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

    def __str__(self):
        return self.name


class ScenarioRaster(SortableMixin):
    class Meta:
        unique_together = ("scenario", "raster")
        ordering = ["order"]

    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    raster = models.ForeignKey("Raster", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        return self.raster.key
        # return f"{self.scenario.key}_{self.raster.key}"


class Raster(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    key = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique identifier for the raster",
    )

    name = models.CharField(
        max_length=32,
        help_text="Name of the raster",
    )

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        help_text="The city the raster belongs to",
    )

    tags = models.ManyToManyField(
        "Tag",
        related_name="rasters",
        blank=True,
        help_text="Tags associated with the raster",
    )

    image = models.ImageField(upload_to="rasters/")
    minimap = models.ImageField(upload_to="minimaps/", null=True, blank=True)
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_image = self.image

    def save(self, *args, **kwargs):
        # Save the model first to ensure `self.image` has a path
        super().save(*args, **kwargs)

        if self.image and (not self.minimap or self.image != self._old_image):
            self.generate_minimap()
            self.generate_thumbnail()
            super().save(*args, **kwargs)

    def generate_minimap(self):
        minimap = generate_minimap(self.image.path)

        # Ensure the minimaps directory exists
        minimap_dir = os.path.join(os.path.dirname(self.image.path), "..", "minimaps")
        os.makedirs(minimap_dir, exist_ok=True)

        base_name = os.path.basename(self.image.name)
        minimap_path = os.path.join(minimap_dir, base_name)

        minimap.save(minimap_path, format="PNG")

        # Update the model's minimap field
        self.minimap.name = os.path.join("minimaps", base_name)

    def generate_thumbnail(self):
        thumbnail = generate_thumbnail(self.image.path)

        # Ensure the thumbnails directory exists
        thumbnail_dir = os.path.join(
            os.path.dirname(self.image.path), "..", "thumbnails"
        )
        os.makedirs(thumbnail_dir, exist_ok=True)

        base_name = os.path.basename(self.image.name)
        thumbnail_path = os.path.join(thumbnail_dir, base_name)

        thumbnail.save(thumbnail_path, format="PNG")

        # Update the model's thumbnail field
        self.thumbnail.name = os.path.join("thumbnails", base_name)

    def __str__(self):
        return self.name


class Tag(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    name = models.CharField(
        max_length=32,
        unique=True,
        help_text="Name of the tag",
    )

    def __str__(self):
        return self.name


class Legend(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title


class LegendEntry(SortableMixin):
    class Meta:
        ordering = ["order"]

    legend = models.ForeignKey(Legend, on_delete=models.CASCADE, related_name="entries")
    text = models.CharField(max_length=64)
    color = ColorField(default="#FFFFFF")
    TYPE_CHOICES = [
        ("rect", "Rectangle"),
        ("circle", "Circle"),
        ("line", "Line"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="rect")
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        return self.text
