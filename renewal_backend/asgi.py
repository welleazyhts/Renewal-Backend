import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'renewal_backend.settings.development')

django_asgi_app = get_asgi_application()

import apps.email_inbox.routing
import apps.notifications.routing

websocket_urlpatterns = apps.notifications.routing.websocket_urlpatterns + apps.email_inbox.routing.websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": 
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        
    ),
}) 