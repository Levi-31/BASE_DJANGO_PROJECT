import abc
import logging

from libs.redis.redis_cluster_manager import RedisClusterManager

logger = logging.getLogger(__name__)


class RateLimiterStrategy(abc.ABC):
    """Abstract base class for all rate limiting strategies."""

    @abc.abstractmethod
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """
        Determines whether the current request should be allowed based on the rate limiting rules.
        
        Args:
            key (str): The unique identifier for the client (e.g. IP + view name).
            limit (int): The maximum number of allowed requests in the window.
            window (int): The duration of the window in seconds.
            
        Returns:
            bool: True if the request is allowed, False if limit is exceeded.
        """
        pass


class FixedWindowCounterStrategy(RateLimiterStrategy):
    """
    Fixed Window Counter implementation using Redis.
    Uses standard simple Redis commands to increment the counter and set the TTL.
    """

    def __init__(self):
        self.redis_manager = RedisClusterManager()

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        if not self.redis_manager.redis_client:
            logger.warning("Redis client is not available for rate limiting. Failing open.")
            return True

        try:
            # Increment the counter using the manager's built-in increment method
            # (Passing key as a kwarg for pre_execution_validation compatibility)
            current_count = self.redis_manager.increment(key=key)
            
            # If it's the very first request (count is 1), set the expiration window.
            # Since RedisClusterManager doesn't expose an expire method natively, 
            # we use set_cache with the window as expiry.
            if current_count == 1:
                self.redis_manager.set_cache(key=key, value=1, expiry=window)
                
            return current_count <= limit
        except Exception as e:
            logger.error(f"Error checking rate limit in Redis: {str(e)}")
            # Fallback behavior: fail open to avoid blocking valid traffic if Redis is down
            return True
