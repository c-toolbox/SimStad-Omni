from django.contrib import admin
from .models import Service, Session


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "session_count",
        "allow_public_code",
        "created_on",
    ]
    fields = [
        "title",
        "host_token",
        "client_token",
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
        "code",
        "guest_count",
    ]
    fields = [
        "created_on",
        "service",
        "code",
        "guest_count",
    ]
    readonly_fields = [
        "created_on",
        "service",
        "code",
        "guest_count",
    ]
