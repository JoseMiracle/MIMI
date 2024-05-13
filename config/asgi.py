import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from dotenv import load_dotenv
load_dotenv(override=True)

os.environ['DJANGO_SETTINGS_MODULE'] = os.getenv('DJANGO_SETTINGS_MODULE')


# Get the ASGI application instance for Django
django_asgi_application = get_asgi_application()

from config import routing
from config.jwt_middleware import JWTAuthMiddleware 


# Defining the ASGI application with ProtocolTypeRouter
application = ProtocolTypeRouter(
    {
        'http': django_asgi_application,
        'websocket': 
        JWTAuthMiddleware(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    }
)
