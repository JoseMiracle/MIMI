import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Get the ASGI application instance for Django
django_asgi_application = get_asgi_application()

from config import routing
from config.jwt_middleware import JWTAuthMiddleware  # Adjust the import path if necessary

# Define the ASGI application with ProtocolTypeRouter
application = ProtocolTypeRouter(
    {
        'http': django_asgi_application,
        'websocket': JWTAuthMiddleware(
            URLRouter(
                routing.websocket_urlpatterns
            )
        ),
    }
)
