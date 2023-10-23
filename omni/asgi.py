"""
ASGI config for omni project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import django, os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omni.settings.prod")

http = get_asgi_application()  # Loads models
import communication.routing  # Requires models

application = ProtocolTypeRouter(
    {
        "http": http,
        "websocket": AuthMiddlewareStack(
            URLRouter(communication.routing.websocket_urlpatterns)
        ),
    }
)
