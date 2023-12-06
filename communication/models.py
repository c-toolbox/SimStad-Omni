import random, re, uuid
from django.db import models


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
    def visitor_count(self):
        return self.visitor_set.count()

    @property
    def host_group(self):
        return "host_" + safe_string(self.title)

    @property
    def client_group(self):
        return "client_" + safe_string(self.title)

    @property
    def guest_group(self):
        return "guest_" + safe_string(self.title)


class Visitor(models.Model):
    # Creation date
    created_on = models.DateTimeField(auto_now_add=True)

    # Service that was visited
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
