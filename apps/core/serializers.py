"""
Core serializers using BaseSerializer with explicit
to_internal_value / to_representation.
"""

import re

from rest_framework import serializers
from django.utils import timezone


class HealthCheckSerializer(serializers.BaseSerializer):
    """Serializer for the health-check response."""

    def to_internal_value(self, data):
        return {}

    def to_representation(self, instance):
        return {
            "status": instance.get("status", "healthy"),
            "message": instance.get("message", "API is running"),
            "timestamp": instance.get("timestamp", timezone.now()).isoformat(),
        }


class HelloSerializer(serializers.BaseSerializer):
    """Serializer for the hello message."""

    def to_internal_value(self, data):
        name = data.get("name", "World")
        if not isinstance(name, str):
            raise serializers.ValidationError({"name": ["Must be a string."]})
        return {"name": name.strip()}

    def to_representation(self, instance):
        return {
            "message": instance.get("message", "Hello, World!"),
            "timestamp": instance.get("timestamp", timezone.now()).isoformat(),
        }


class UserCreateSerializer(serializers.BaseSerializer):
    """
    Validates inbound data for creating a user.
    Shapes outbound data for user responses.
    """

    def to_internal_value(self, data):
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        errors = {}

        # username
        if not username:
            errors["username"] = ["This field is required."]
        elif not isinstance(username, str):
            errors["username"] = ["Must be a string."]
        elif len(username) > 50:
            errors["username"] = ["Max length is 50 characters."]

        # email
        if not email:
            errors["email"] = ["This field is required."]
        elif not isinstance(email, str):
            errors["email"] = ["Must be a string."]
        elif not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            errors["email"] = ["Enter a valid email address."]
        elif len(email) > 100:
            errors["email"] = ["Max length is 100 characters."]

        # password
        if not password:
            errors["password"] = ["This field is required."]
        elif not isinstance(password, str):
            errors["password"] = ["Must be a string."]
        elif len(password) < 6:
            errors["password"] = ["Password must be at least 6 characters."]

        if errors:
            raise serializers.ValidationError(errors)

        return {
            "username": username.strip(),
            "email": email.strip().lower(),
            "password": password,
        }

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "username": instance.username,
            "email": instance.email,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
        }


class UserReadSerializer(serializers.BaseSerializer):
    """
    Read-only serializer — used for GET responses.
    Password is never returned.
    """

    def to_internal_value(self, data):
        return {}

    def to_representation(self, instance):
        data = {
            "id": instance.id,
            "username": instance.username,
            "email": instance.email,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
        }
        if hasattr(instance, "read_from"):
            data["read_from"] = instance.read_from
        return data
