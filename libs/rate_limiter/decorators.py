from functools import wraps
from django.http import JsonResponse
from libs.redis.redis_cluster_manager import RedisClusterManager
from .strategies import FixedWindowCounterStrategy


def rate_limit(limit=10, window=300, strategy=None, key=None):
    strategy = strategy or FixedWindowCounterStrategy()

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            # request is args[0] in FBVs and args[1] in CBVs
            request = args[0] if hasattr(args[0], 'META') else args[1]
            
            # Identify user by ID or Fallback to IP address
            ident = str(request.user.id) if getattr(request.user, "is_authenticated", False) else request.META.get("REMOTE_ADDR")
            
            # Use provided key or fallback to function name
            base_key = key or view_func.__name__
            redis_key = f"{RedisClusterManager.SERVICE_PREFIX}ratelimit:{base_key}:{ident}"

            if not strategy.is_allowed(redis_key, limit, window):
                return JsonResponse({"error": "Rate limit exceeded"}, status=429)

            return view_func(*args, **kwargs)
            
        return _wrapped_view
    return decorator
