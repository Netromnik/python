from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0-*i-g&&xvxe7#y^q=b0vv-77b=t^to^z5+cdn+3o8sj85ovpx'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*'] 

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS = INSTALLED_APPS + [
    'debug_toolbar',
]

MIDDLEWARE = MIDDLEWARE + [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
INTERNAL_IPS = ("127.0.0.1", "172.17.0.1")

try:
    from .local import *
except ImportError:
    pass
