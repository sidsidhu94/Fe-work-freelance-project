"""
ASGI config for fework project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

# import os
# import django

# from channels.routing import ProtocolTypeRouter,URLRouter
# from channels.auth import AuthMiddlewareStack
# from django.core.asgi import get_asgi_application
# import chat.routing

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fework.settings')
django.setup()
# application = get_asgi_application()
from chat.routing import websocket_urlpatterns
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),

        'websocket':AuthMiddlewareStack(
            URLRouter(
            websocket_urlpatterns
    )
),
        # Just HTTP for now. (We can add other protocols later.)
    }
)