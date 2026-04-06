# Rate Limiter Module

This module provides a Redis-backed, highly extensible rate limiting solution designed for Django/Django REST Framework applications.

## Key Features
- **Algorithm Agnostic**: Implements the Strategy design pattern, allowing the rate-limiting algorithm to be easily swapped out.
- **Redis-Backed**: Leverages the `RedisClusterManager` singleton for fast, distributed rate limiting with a fail-open mechanism in case of Redis outages.
- **Universal Decorator**: A single `@rate_limit` wrapper works seamlessly for both Function-Based Views (FBVs) and Class-Based Views (CBVs).

## Usage

### 1. Class-Based Views (Django REST Framework)
When decorating a Class-Based View, **do not** place the decorator on internal lifecycle methods (like `get`, `post`, or `get_`). Doing so will pass the `429 JsonResponse` up into your view's internal data pipeline (crashing the serializer).

Instead, apply the decorator directly onto the `dispatch` method to correctly short-circuit the request at the very beginning of the lifecycle.

```python
from libs.rate_limiter import rate_limit
from rest_framework.views import APIView

class MyAPIView(APIView):
    # Apply rate limiting to 10 requests per 5 minutes (300 seconds)
    @rate_limit(limit=10, window=300)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Normal view logic
        pass
```

### 2. Using `@method_decorator` on the Class
If you prefer not to override `dispatch` manually, you can use Django's built-in `method_decorator` to apply the rate limiter to the `dispatch` method from the class level.

```python
from django.utils.decorators import method_decorator
from libs.rate_limiter import rate_limit
from rest_framework.views import APIView

@method_decorator(rate_limit(limit=10, window=300), name="dispatch")
class MyAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Normal view logic
        pass
```

### 3. URL configuration (urls.py)
If you want to apply the decorator without touching the view code at all, you can wrap the view directly in `urls.py`. This is especially useful for external or third-party views.

```python
from django.urls import path
from libs.rate_limiter import rate_limit
from my_app.views import MyAPIView, my_function_view

urlpatterns = [
    # Wrapping a Class-Based View
    path("api/data/", rate_limit(limit=10, window=300)(MyAPIView.as_view())),
    
    # Wrapping a Function-Based View
    path("api/info/", rate_limit(limit=5, window=60)(my_function_view)),
]
```

### 4. Function-Based Views
For standard function-based views, you can apply the decorator directly to the view function:

```python
from libs.rate_limiter import rate_limit

@rate_limit(limit=5, window=60) # 5 requests per minute
def my_api_view(request):
    return JsonResponse({"message": "Success!"})
```

## How It Works

### The Decorator
The `@rate_limit(limit, window, strategy, key)` decorator automatically detects whether it's wrapped around a bound method (CBV) or a simple function (FBV) and extracts the `request` object appropriately.

By default, the rate limiter uses the name of the decorated function (`view_func.__name__`) to generate the Redis key. However, you can pass a custom `key` string if you want to group requests across multiple views or use a more descriptive identifier:

```python
@rate_limit(limit=10, window=60, key="login_attempts")
def custom_login_view(request): ...
```

If the request is authenticated, it uses `request.user.id` as the identity key. If unauthenticated, it falls back to the client's IP (`REMOTE_ADDR`).

If the rate limit is exceeded, it immediately responds with:
`HTTP 429 Too Many Requests`
```json
{
  "error": "Rate limit exceeded"
}
```

### Strategies
The default strategy is the **Fixed Window Counter** (`FixedWindowCounterStrategy`), tracked in Redis.

If you wish to switch behavior (e.g. to a Leaky Bucket or Token Bucket algorithm in the future), you can implement the `RateLimiterStrategy` interface and pass your new strategy into the decorator:

```python
from libs.rate_limiter import rate_limit
from libs.rate_limiter.strategies import TokenBucketStrategy

@rate_limit(limit=100, window=60, strategy=TokenBucketStrategy())
def dispatch(self, request, *args, **kwargs):
    ...
```

### High Availability
The `FixedWindowCounterStrategy` implements a **fail-open** policy. If the `RedisClusterManager` is unavailable or throws an exception (e.g. cluster node failure), the rate limiter logs an error but allows traffic to pass through. This ensures our API remains available during transient cache infrastructure outages.
