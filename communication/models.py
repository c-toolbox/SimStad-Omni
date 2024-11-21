import random, re, uuid, os
from io import BytesIO
from django.db import models
from django.core.files.base import ContentFile
from .utils import generate_thumbnail


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
    created_on = models.DateTimeField(auto_now_add=True)

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


class Installation(models.Model):
    id = models.CharField(
        max_length=32,
        unique=True,
        primary_key=True,
        help_text="Unique identifier for the installation",
    )

    name = models.CharField(
        max_length=32,
        help_text="Name of the installation",
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the installation was created",
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Service associated with the installation",
    )


class Raster(models.Model):
    id = models.CharField(
        max_length=32,
        unique=True,
        primary_key=True,
        help_text="Unique identifier for the raster",
    )

    name = models.CharField(
        max_length=32,
        help_text="Name of the raster",
    )

    installation = models.ForeignKey(
        Installation,
        on_delete=models.SET_NULL,
        null=True,
        help_text="The installation the raster belongs to",
    )

    group = models.CharField(
        max_length=255,
        help_text="Group to which the raster belongs",
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the raster was created",
    )

    change_time = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the raster was last modified",
    )

    image = models.ImageField(
        upload_to="rasters/", help_text="Image file for the raster"
    )

    minimap = models.ImageField(
        upload_to="minimaps/",
        null=True,
        blank=True,
        help_text="Minimap image for the raster",
    )

    thumbnail = models.ImageField(
        upload_to="thumbnails/",
        null=True,
        blank=True,
        help_text="Thumbnail image for the raster",
    )

    def save(self, *args, **kwargs):
        # Save the model first to ensure `self.image` has a path
        super().save(*args, **kwargs)

        if self.image:
            # Generate the thumbnail
            thumbnail = generate_thumbnail(self.image.path)

            # Ensure the thumbnails directory exists
            thumbnail_dir = os.path.join(
                os.path.dirname(self.image.path), "..", "thumbnails"
            )
            os.makedirs(thumbnail_dir, exist_ok=True)

            # Define the thumbnail path
            base_name = os.path.basename(self.image.name)
            thumbnail_path = os.path.join(thumbnail_dir, base_name)

            thumbnail.save(thumbnail_path, format="PNG")

            # Update the model's thumbnail field
            self.thumbnail.name = os.path.join("thumbnails", base_name)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name
