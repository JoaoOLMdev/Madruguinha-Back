"""
ASGI config for MadruguinhaBack project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

import app.routing
from app.channels_middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    
    "websocket": JWTAuthMiddleware(
        URLRouter(
            app.routing.websocket_urlpatterns
        )
    ),
})
