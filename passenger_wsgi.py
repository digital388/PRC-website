"""
Passenger WSGI entry point for cPanel's "Setup Python App".
Created manually as a fallback in case cPanel does not auto-generate it.

In cPanel's Setup Python App, set:
  - Application root : the folder containing this file (e.g. ~/prcapp)
  - Application URL  : your domain
  - Application startup file : app.py  (or leave this file as the startup)
"""
import os
import sys

# Ensure the app root is on sys.path so that `config`, `website`, etc. resolve.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DJANGO_DEBUG", "False")

from config.wsgi import application
