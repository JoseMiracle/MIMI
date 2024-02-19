from .development import *
import dj_database_url

ALLOWED_HOSTS = os.getenv('HOSTS').split()

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUD_NAME'),
    'API_KEY':  os.getenv('API_KEY'),
    'API_SECRET': os.getenv('API_SECRET')
}

DEBUG = bool(os.getenv('DEBUG'))

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
	"default": dj_database_url.parse(os.environ.get("DATABASE_URL"))
}


