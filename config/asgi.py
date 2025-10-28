import os

from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

if settings.DEBUG:
    application = ASGIStaticFilesHandler(django_asgi_app)
else:
    from whitenoise import WhiteNoise

    application = WhiteNoise(django_asgi_app, root=settings.STATIC_ROOT)
