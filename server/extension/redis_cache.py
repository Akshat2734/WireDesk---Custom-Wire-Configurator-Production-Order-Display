import json
import os

from redis import Redis
from redis.exceptions import RedisError


class RedisCache:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            url = os.environ.get("REDIS_URL")
            if url:
                self._client = Redis.from_url(url, decode_responses=True)
        return self._client

    def get_json(self, key):
        try:
            value = self.client.get(key) if self.client else None
            return json.loads(value) if value else None
        except (RedisError, ValueError):
            return None

    def set_json(self, key, value, ttl=15):
        try:
            if self.client:
                self.client.setex(key, ttl, json.dumps(value))
        except RedisError:
            pass

    def delete(self, *keys):
        try:
            if self.client and keys:
                self.client.delete(*keys)
        except RedisError:
            pass


redis_cache = RedisCache()
