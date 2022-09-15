"""
ASGI config

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/

"""
# import os

# from django.core.asgi import get_asgi_application
# # This allows easy placement of apps within the interior
# # skill4cash-be directory.

# # If DJANGO_SETTINGS_MODULE is unset, default to the local settings
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")

# # This application object is used by any ASGI server configured to use this file.
# django_application = get_asgi_application()

# Import websocket application here, so apps from django_application are loaded first
# import socketio
# # Import websocket application here, so apps from django_application are loaded first
# import socketio
# from chat.sockets import sio


# application = socketio.ASGIApp(sio, django_application)
