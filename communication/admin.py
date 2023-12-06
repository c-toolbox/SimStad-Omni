from django.contrib import admin
from .models import Service, Visitor


class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "visitor_count",
        "allow_public_code",
        "allow_multiple_hosts",
        "created_on",
    ]
    fields = [
        "title",
        "host_token",
        "client_token",
        "allow_public_code",
        "allow_multiple_hosts",
        "public_code",
    ]
    readonly_fields = [
        "created_on",
        "host_token",
        "client_token",
        "public_code",
    ]


class VisitorAdmin(admin.ModelAdmin):
    list_display = [
        "created_on",
        "service",
    ]
    fields = [
        "created_on",
        "service",
    ]
    readonly_fields = [
        "created_on",
    ]


admin.site.register(Service, ServiceAdmin)
admin.site.register(Visitor, VisitorAdmin)
