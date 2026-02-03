import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet_transfert_argent.settings")

application = get_asgi_application()
