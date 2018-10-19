"""
WSGI config for tranServerSite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application


sys.path.append("C:/workspace/tranServerSite")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tranServerSite.settings")

application = get_wsgi_application()