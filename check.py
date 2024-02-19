# settings.py

import urllib.parse as urlparse  # For Python 3

# Parse the Redis connection string
redis_url = urlparse.urlparse("redis://default:i4mdAJOnDLnaaDM3P2ngMoDI5cKIl3Ia@roundhouse.proxy.rlwy.net:36119")

print(redis_url.hostname, redis_url.port)
print(redis_url.password)
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [(redis_url.hostname, redis_url.port)],
#             "password": redis_url.password,
#             "db": 0,  # Specify the Redis database number if needed
#         },
#     },
# }
