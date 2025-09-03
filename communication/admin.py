from django.contrib import admin
from .models import Service, Session, SessionLog
from django.utils import timezone


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "session_mode",
        "allow_public_code",
        "live_session_count",
        "times_used",
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
        "time_alive",
    ]
    fields = [
        "created_on",
        "service",
        "_code",
    ]
    readonly_fields = [
        "created_on",
        "service",
        "_code",
    ]

    def has_add_permission(self, request, obj=None):
        return False

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


@admin.register(SessionLog)
class SessionLogAdmin(admin.ModelAdmin):
    list_filter = ["service"]
    list_display = [
        "id",
        "started_at",
        "ended_at",
        "time_alive",
        "service",
        "client_count",
        "message_count",
    ]
    fields = [
        "started_at",
        "ended_at",
        "service",
        "client_count",
        "message_count",
    ]
    readonly_fields = [
        "started_at",
        "ended_at",
        "service",
        "client_count",
        "message_count",
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def time_alive(self, obj: SessionLog):
        delta = obj.ended_at - obj.started_at
        seconds = int(delta.total_seconds())

        if seconds < 60:
            return f"{seconds}s"
        minutes, seconds = divmod(seconds, 60)
        if minutes < 60:
            return f"{minutes}m {seconds}s"
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h {minutes}m {seconds}s"
