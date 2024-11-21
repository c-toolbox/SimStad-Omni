import os, zipfile
from django import forms
from django.contrib import admin, messages
from django.core.files.base import ContentFile
from django.utils.html import format_html
from .models import Service, Installation, Raster


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        "title",
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


@admin.register(Installation)
class InstallationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "create_time",
        "service",
    ]
    fields = [
        "name",
        "service",
    ]


@admin.register(Raster)
class RasterAdmin(admin.ModelAdmin):
    actions = ["bulk_upload"]
    list_display = [
        "id",
        "name",
        "group",
        "create_time",
        "change_time",
        "image",
        "thumbnail_image",
    ]
    fields = [
        "id",
        "name",
        "group",
        "image",
        "thumbnail_image",
    ]
    readonly_fields = [
        "thumbnail_image",
    ]

    def thumbnail_image(self, obj: Raster):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="100" height="100" />',
                obj.thumbnail.url,
            )
        return ""
