from .development import *
import dj_database_url

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS').split(',')

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUD_NAME'),
    'API_KEY':  os.getenv('API_KEY'),
    'API_SECRET': os.getenv('API_SECRET')
}

DEBUG = bool(int(os.getenv('DEBUG', 0)))

REDIS_URL = os.getenv('REDIS_URL')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDIS_URL]
        },
    },
}




DATABASES = {
	"default": dj_database_url.parse(os.getenv('DATABASE_URL'))
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3172"
]
