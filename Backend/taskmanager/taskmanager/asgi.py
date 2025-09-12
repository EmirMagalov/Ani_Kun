from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from main.routing import websocket_urlpatterns
from .middleware import JWTAuthMiddleware
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
