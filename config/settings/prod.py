from .development import *
import dj_database_url

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

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
	"default": dj_database_url.parse("postgres://db_utqx_user:OsuXNepP9XDWL8a6woCInmN3m2sf7LAn@dpg-cna36h7109ks73a0bqg0-a.oregon-postgres.render.com/db_utqx")
}


