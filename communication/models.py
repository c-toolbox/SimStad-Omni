import random, re, uuid
from django.db import models


def generate_code():
    chars = list("ABCDEFGHIJKLMNOPQRSTUVXYZ")
    size = 4
    while True:
        random.shuffle(chars)
        code = "".join(chars[:size])
        if not Session.objects.filter(code=code).exists():
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

    # TODO: Add a field for the host to set the number of guests allowed

    # TODO: Add a field for only allowing certain dns or ip addresses

    def add_session(self):
        group_key = safe_string(self.title)
        session = Session(service=self, group_key=group_key)
        session.save()
        return session

    @property
    def session_count(self):
        return self.session_set.count()

    def __str__(self):
        return self.title


class Session(models.Model):
    # Creation date
    created_on = models.DateTimeField(auto_now_add=True)

    # Service that the session is connected to
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    # Group key for the session
    group_key = models.CharField(
        max_length=32,
        help_text="A group key name used for websocket channels",
    )

    # Unique code for visitors to join via
    code = models.CharField(
        max_length=8,
        null=True,
        default=generate_code,
        help_text="The public code for guests to connect via. A new code is generated everytime the host connects to a service.",
    )

    # Number of guests connected
    guest_count = models.IntegerField(
        default=0,
        help_text="The number of guests that are connected to this session",
    )

    @property
    def host_group(self):
        return f"host_{self.group_key}_{self.code}"

    @property
    def client_group(self):
        return f"client_{self.group_key}_{self.code}"

    @property
    def guest_group(self):
        return f"guest_{self.group_key}_{self.code}"

    def __str__(self):
        return f"{self.group_key} ({self.code})"
