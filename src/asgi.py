from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator


from django.core.asgi import get_asgi_application

import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django_asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns
from chat.custom_middleware import JwtAuthMiddlewareStack


application = ProtocolTypeRouter({
            'http': django_asgi_app,
            'websocket': OriginValidator(JwtAuthMiddlewareStack(URLRouter(websocket_urlpatterns)),["*"])
        })