import logging
import threading
from datetime import timedelta

import redis
from django.conf import settings

from libs.redis.pre_execution_validator import pre_execution_validation

logger = logging.getLogger("RedisClusterManager")


class RedisClusterManager:
    """
    Central Redis Manager for Singleton functionality anywhere in the project.
    
    Usage:
        from libs.redis.redis_cluster_manager import RedisClusterManager
        redis_client = RedisClusterManager()
        redis_client.set_cache(key="hld:user_1", value="test")
    """

    redis_client = None
    _lock = threading.Lock()  # Lock to ensure thread-safe singleton creation

    # This prefix is checked by the pre_execution_validation decorator.
    SERVICE_PREFIX = "hld:"

    def __new__(cls):
        if cls.redis_client is None:
            with cls._lock:
                # Double-check inside the lock to avoid initiating multiple connections
                if cls.redis_client is None:
                    # Dynamically read the Redis URL from Django CACHES setting
                    # Fallback to local default if not found
                    redis_url = "redis://127.0.0.1:6379/1"
                    if hasattr(settings, "CACHES") and "default" in settings.CACHES:
                        redis_url = settings.CACHES["default"].get("LOCATION", redis_url)
                        
                    try:
                        # Instantiate the standard connection payload
                        # (Adjust to redis.cluster.RedisCluster if moving to true multi-node cluster)
                        cls.redis_client = redis.from_url(
                            redis_url,
                            decode_responses=True,
                            socket_timeout=5,
                            socket_connect_timeout=5,
                            retry_on_timeout=True,
                        )
                        # Ping immediately to confirm connection is active
                        cls.redis_client.ping()
                        logger.info(f"Successfully connected to Redis singleton at {redis_url}")
                    except Exception as e:
                        logger.error(f"Error initializing generic Redis Manager: {str(e)}")
                        raise
        return super().__new__(cls)

    @pre_execution_validation
    def set_cache(self, *, key, value, expiry=None, nx=None):
        if expiry == 0 or expiry is None:
            return self.redis_client.set(name=key, value=value, nx=nx)
        return self.redis_client.set(name=key, value=value, ex=expiry, nx=nx)

    @pre_execution_validation
    def get_cache(self, *, key):
        return self.redis_client.get(name=key)

    @pre_execution_validation
    def delete_cache(self, *, key):
        return self.redis_client.delete(key)

    @pre_execution_validation
    def hgetall_cache(self, *, key):
        return self.redis_client.hgetall(key)

    @pre_execution_validation
    def hget_cache(self, *, key, hash_key):
        return self.redis_client.hget(key, hash_key)

    @pre_execution_validation
    def key_exists(self, key):
        return self.redis_client.exists(key)

    @pre_execution_validation
    def increment(self, key):
        return self.redis_client.incr(key)

    @pre_execution_validation
    def get_keys(self, pattern):
        return self.redis_client.keys(pattern)

    @pre_execution_validation
    def get_ttl(self, key):
        return self.redis_client.ttl(key)

    @pre_execution_validation
    def get_shadow_key(self, key):
        return "shadow:" + key
