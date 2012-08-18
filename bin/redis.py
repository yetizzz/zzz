import os
import redis

url = os.getenv('REDISTOGO_URL', 'redis://localhost')
redis = redis.from_url(url)

