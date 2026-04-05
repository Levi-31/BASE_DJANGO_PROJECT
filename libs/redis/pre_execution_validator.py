import logging
from functools import wraps

logger = logging.getLogger("RedisValidator")


def pre_execution_validation(func):
    """
    Decorator for Redis methods to validate keys and inject default logic.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # 1. Key nomenclature validation
        if "key" in kwargs:
            key = kwargs.get("key")
            service_prefix = getattr(self, "SERVICE_PREFIX", "hld:")
            
            if not isinstance(key, str):
                raise RedisKeyValidationException("key type is not str")
            
            # Require the key to start with the standard application prefix
            if service_prefix and not key.startswith(service_prefix):
                raise RedisKeyValidationException(f"key - '{key}' does not start with standard prefix '{service_prefix}'")

        # 2. Add default expiry if not provided
        DEFAULT_EXPIRY_ALLOWED_METHODS = ["set_cache", "set_cache_ttl", "set_cache_expiry"]
        if func.__name__ in DEFAULT_EXPIRY_ALLOWED_METHODS:
            expiry = kwargs.get("expiry")
            if expiry is None:
                expiry = 600  # Default 10 minutes (600 seconds)
                kwargs["expiry"] = expiry
                logger.info(f"Default expiry ({expiry}s) added for command - {func.__name__}")

        return func(self, *args, **kwargs)

    return wrapper


class RedisKeyValidationException(Exception):
    """Custom exception for redis key validation error."""
    def __init__(self, message):
        logger.error(message)
        super().__init__(message)
