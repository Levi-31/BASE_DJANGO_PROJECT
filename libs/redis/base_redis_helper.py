from datetime import timedelta


class BaseRedisHelper:
    redis = None

    def set_cache(self, key, value):
        self.redis.set(key, value)

    def mget_cache(self, pattern):
        key_list = self.redis.keys(pattern=pattern)
        value_list = self.redis.mget(key_list)
        return dict(zip(key_list, value_list))

    def hgetall_cache(self, key):
        value = self.redis.hgetall(key)

        return value if value else None

    def get_cache(self, key):
        value = self.redis.get(key)

        return value if value else None

    def key_exists(self, key):
        return self.redis.exists(key)

    def set_cache_ttl(self, key, value, ttl=600):
        self.redis.set(key, value, ttl)

    def set_cache_expiry(self, key, value, expire=10):
        self.redis.setex(key, timedelta(minutes=expire), value)

    def delete_cache(self, key):
        self.redis.delete(key)

    def increament(self, key):
        self.redis.incr(key)

    def get_keys(self, pattern):
        return self.redis.keys(pattern)

    def get_ttl(self, key):
        return self.redis.ttl(key)

    def get_shadow_key(self, key):
        return "shadow:" + key

    def set_zadd_key(self, key, dict_of_key_score):
        self.redis.zadd(key, dict_of_key_score)

    def get_keys_in_zrange(self, hashset, start_score, end_score):
        values = self.redis.zrangebyscore(hashset, start_score, end_score)
        return values

    def zremrangebyscore(self, hashset, start_score, end_score):
        self.redis.zremrangebyscore(hashset, start_score, end_score)
