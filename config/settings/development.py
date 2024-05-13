from .base import *
from datetime import timedelta


SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

LOCAL_APPS = [
    "mimi.accounts",
    "mimi.friendships",
    "mimi.posts",
    "mimi.chats",
    "mimi.currencies",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "cloudinary_storage",
    "cloudinary",
    "channels",
    "drf_standardized_errors",
    "drf_spectacular"

]

INSTALLED_APPS += LOCAL_APPS + THIRD_PARTY_APPS



CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUD_NAME'),
    'API_KEY':  os.getenv('API_KEY'),
    'API_SECRET': os.getenv('API_SECRET')
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
}

if DEBUG == False:
    MEDIA_URL = '/media/'  # or any prefix you choose
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



# SIMPLE JWT SETTINGS
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

PASSWORD_RESET_TIMEOUT = 18000

# CHANNELS_SETTINGS
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}


ASGI_APPLICATION = "config.asgi.application"
AUTH_USER_MODEL = 'accounts.CustomUser'

CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY')

SPECTACULAR_SETTINGS = {
    'TITLE': 'MIMI',
    'DESCRIPTION': 'CHAT APPLICATION',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    
}