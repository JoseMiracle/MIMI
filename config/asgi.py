# config/asgi.py
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from config.jwt_middleware import JWTAuthMiddleware  # Adjust the import path if necessary
from django.core.asgi import get_asgi_application
from config import routing

# REMOVE THE HARDCORDED DJANGO_SETTINS_MODULE LATER 
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
from django.core.asgi import get_asgi_application
django_asgi_application = get_asgi_application()




application = ProtocolTypeRouter(
    {
        'http': django_asgi_application,
        'websocket': JWTAuthMiddleware(
            URLRouter(
                routing.websocket_urlpatterns
        )),
    }
)

