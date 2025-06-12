from django.contrib import admin
from .models import Service


# Return the installed apps in the order the user has registred them
def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request, app_label)
    app_list = list(app_dict.values())
    return app_list


admin.AdminSite.get_app_list = get_app_list


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "allow_public_code",
        "allow_multiple_hosts",
        "created_at",
        "changed_at",
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
        "host_token",
        "client_token",
        "public_code",
    ]
