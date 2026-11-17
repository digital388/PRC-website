"""
Entry point for cPanel's "Setup Python App" (Phusion Passenger).

In cPanel's Setup Python App, set:
  - Application root : the folder containing this file
  - Application URL  : your domain
  - Application startup file : app.py

cPanel generates passenger_wsgi.py automatically (it imports `application`
from this module). Secrets are provided via the app's Environment variables
UI (DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS, ...).
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# Safety net: cPanel apps must never run with DEBUG accidentally enabled.
os.environ.setdefault("DJANGO_DEBUG", "False")

from config.wsgi import application  # noqa: E402
