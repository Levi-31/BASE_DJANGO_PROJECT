"""
Core URL configuration.

Included by the root URLconf under /api/v1/.
"""

from django.urls import path

from apps.core import views

urlpatterns = [
    path("health/", views.HealthCheckView.as_view(), name="health-check"),
    path("hello/", views.HelloMessageView.as_view(), name="hello-message"),
    path("users/", views.UserCreateView.as_view(), name="user-create"),
    path("users/<int:user_id>/", views.UserReadView.as_view(), name="user-read"),
]
