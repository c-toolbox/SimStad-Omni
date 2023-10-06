import random, re, uuid
from django.db import models


# Generate new token - "xxxx-xxxx-xxxx-xxxx"
def generate_token():
    return str(uuid.uuid4())


def safe_string(text):
    return re.sub(r"[^\w\d-]", "_", text).lower()


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

    allow_public_visitors = models.BooleanField(
        default=False,
        help_text="If enabled, the service will be accessible through a public code or link. A new code will be generated everytime the host connects.",
    )

    def __str__(self):
        return self.title

    @property
    def visitor_count(self):
        return self.visitor_set.count()

    @property
    def host_group(self):
        return "server_" + safe_string(self.title)

    @property
    def client_group(self):
        return "client_" + safe_string(self.title)


class Visitor(models.Model):
    # Creation date
    created_on = models.DateTimeField(auto_now_add=True)

    # Unique code for each session
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
