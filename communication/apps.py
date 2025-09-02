from django.apps import AppConfig


class CommunicationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "communication"

    def ready(self):
        from django.db import connection

        if connection.connection and connection.connection.is_connected():
            # Clear the sessions table on app startup
            from django.contrib.sessions.models import Session
            Session.objects.all().delete()
