
import redis


class redisclient(object):
    def __init__(self):
        self._redis = redis.StrictRedis(host='localhost')

    def set(self, key, value, time=3600):
        self._redis.setex(key, time, value)

    def get(self, name):
        return self._redis.get(name)

    def delete(self, name):
        return self._redis.delete(name)
