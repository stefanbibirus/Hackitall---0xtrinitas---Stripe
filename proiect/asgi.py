#FILE PATH: proiect/asgi.py
#================================================================================

"""
ASGI config for proiect project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proiect.settings')
application = get_asgi_application()