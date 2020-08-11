import os

TESTING = True
DEBUG = True
FLASK_ENV = 'development'
SECRET_KEY = os.urandom(32)  # Generates a 32-bit key.
WTF_CSRF_SECRET_KEY = os.urandom(32)