from django.contrib import admin
from .models import Service, Session
from django.utils import timezone


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "session_count",
        "session_mode",
        "allow_public_code",
        "created_on",
    ]
    fields = [
        "title",
        "host_token",
        "client_token",
        "session_mode",
        "allow_public_code",
    ]
    readonly_fields = [
        "created_on",
        "host_token",
        "client_token",
    ]


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = [
        "created_on",
        "service",
        "_code",
        "guest_count",
        "time_alive",
    ]
    fields = [
        "created_on",
        "service",
        "_code",
        "guest_count",
    ]
    readonly_fields = [
        "created_on",
        "service",
        "_code",
        "guest_count",
    ]

    @admin.display(description="Code")
    def _code(self, obj: Session):
        if obj.service.allow_public_code:
            return obj.code
        return f"({obj.code})"

    def time_alive(self, obj: Session):
        delta = timezone.now() - obj.created_on
        seconds = int(delta.total_seconds())

        if seconds < 60:
            return f"{seconds}s"
        minutes, seconds = divmod(seconds, 60)
        if minutes < 60:
            return f"{minutes}m {seconds}s"
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h {minutes}m {seconds}s"
