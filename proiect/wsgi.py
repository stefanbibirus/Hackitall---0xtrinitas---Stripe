#FILE PATH: proiect/wsgi.py
#================================================================================

"""
WSGI config for proiect project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proiect.settings')
application = get_wsgi_application()