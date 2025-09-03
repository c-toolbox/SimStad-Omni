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
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = " Services"

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

    SESSION_MODES = [
        ("SS", "Kick existing hosts"),  # Single host, single session
        ("MS", "Join existing session"),  # Multiple hosts, single session
        ("SM", "Create new session"),  # Single host, multiple sessions
    ]

    # Session mode
    session_mode = models.CharField(
        max_length=2,
        choices=SESSION_MODES,
        default="SS",
        help_text="Specifies how hosts and sessions are handled when a new host joins.<ul><li>- For exhibits with multiple hosts or multiple projectors, use 'Join existing session'.</li><li>- For exhibits that operate independently, use 'Create new session'.</li><li>- For unique exhibits, use 'Kick existing hosts'.</li></ul>",
    )

    # Boolean for public code generation
    allow_public_code = models.BooleanField(
        default=False,
        help_text="If enabled, the service will be accessible through a public code or link. A new code is generated everytime the host connects. Enable this for exhibits where you want visitors to join in.",
    )

    # TODO: Add a field for the host to set the number of guests allowed

    # TODO: Add a field for only allowing certain dns or ip addresses

    def add_session(self):
        group_key = safe_string(self.title)
        session = Session(service=self, group_key=group_key)
        session.save()
        return session

    @property
    def live_session_count(self):
        return self.session_set.count()

    @property
    def times_used(self):
        return self.session_set.count() + self.session_log_set.count()

    @property
    def should_kick_host(self):
        return self.session_mode == "SS"

    @property
    def never_delete_session(self):
        return self.session_mode == "MS"

    @property
    def always_new_session(self):
        return self.session_mode == "SM"

    def __str__(self):
        return self.title


class Session(models.Model):
    class Meta:
        verbose_name = "Live session"
        verbose_name_plural = "Live sessions"

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

    # Create session log before deletion
    def create_log(self, client_count, message_count):
        SessionLog.objects.create(
            service=self.service,
            started_at=self.created_on,
            client_count=client_count,
            message_count=message_count,
        )

    @property
    def host_service_group(self):
        return f"host_{self.group_key}"

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


class SessionLog(models.Model):
    class Meta:
        verbose_name = "Session log"
        verbose_name_plural = "Session logs"

    # Service that the session is connected to
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    # Start time
    started_at = models.DateTimeField()

    # End time
    ended_at = models.DateTimeField(auto_now_add=True)

    # Number of connected clients
    client_count = models.IntegerField(default=0)

    # Number of messages sent
    message_count = models.IntegerField(default=0)
