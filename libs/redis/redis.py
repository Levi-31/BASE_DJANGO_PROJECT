from functools import wraps

from libs.app_logger import AppLogger
from libs.constants.constant import Constant

logger = AppLogger(tag="Redis Cluster Manager PRE EXECUTION VALIDATION")


def pre_execution_validation(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # key nomenclature validation
        if "key" in kwargs.keys():
            key = kwargs.get("key")
            service_prefix = Constant.REDIS_CONFIG.CACHE_KEYS.SERVICE_PREFIX
            if not isinstance(key, str):
                raise RedisKeyValidationException("key type is not str")
            if len(key) < len(service_prefix) or not key.startswith(service_prefix):
                raise RedisKeyValidationException(f"key - {key} length is less than {service_prefix}")

        # add default expiry in method is whitelisted
        if func.__name__ in Constant.REDIS_CONFIG.EXPIRY_CONFIG.DEFAULT_EXPIRY_ALLOWED_METHODS:
            expiry = kwargs.get("expiry")
            if expiry is None:
                expiry = Constant.REDIS_CONFIG.EXPIRY_CONFIG.EXPIRY_IN_SECONDS
                kwargs["expiry"] = expiry
                logger.info(f"default expiry - {expiry} added for command - {func.__name__}")
        return func(self, *args, **kwargs)

    return wrapper


class RedisKeyValidationException(Exception):
    """Custom exception for redis key validation error."""

    def __init__(self, message):
        logger.error(message)
        super().__init__(message)
