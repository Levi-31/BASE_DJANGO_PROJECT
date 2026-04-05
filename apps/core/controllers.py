"""
Core controllers — business logic layer.

Each controller is instantiated with (validated_data, user, headers)
and exposes a .process() method that returns the result.
"""

import logging

from django.contrib.auth.hashers import make_password
from django.utils import timezone

from apps.core.db_managers import UserDBManager
from apps.core.db_router import PrimaryReplicaRouter

logger = logging.getLogger(__name__)

user_db_manager = UserDBManager()


class HealthCheckController:
    def __init__(self, validated_data, user, headers):
        self.validated_data = validated_data
        self.user = user
        self.headers = headers

    def process(self):
        return {
            "status": "healthy",
            "message": "API is running",
            "timestamp": timezone.now(),
        }


class HelloController:
    def __init__(self, validated_data, user, headers):
        self.validated_data = validated_data
        self.user = user
        self.headers = headers

    def process(self):
        name = self.validated_data.get("name", "World")
        return {
            "message": f"Hello, {name}!",
            "timestamp": timezone.now(),
        }


class UserCreateController:
    """
    Creates a new user → writes to the MAIN database.
    """

    def __init__(self, validated_data, user, headers):
        self.validated_data = validated_data
        self.user = user
        self.headers = headers

    def process(self):
        data = dict(self.validated_data)
        data["password"] = make_password(data["password"])
        logger.info("Creating user: %s", data.get("username"))
        return user_db_manager.create(data)


class UserReadController:
    """
    Reads a user → hash-based 50/50 between MASTER and REPLICA.
    """

    def __init__(self, validated_data, user, headers):
        self.validated_data = validated_data
        self.user = user
        self.headers = headers

    def process(self):
        user_id = self.validated_data.get("user_id")

        db = PrimaryReplicaRouter.pick_read_db()
        db_label = "MASTER" if db == "default" else "REPLICA"
        logger.info("Reading user id=%s from %s (%s)", user_id, db_label, db)

        try:
            user = user_db_manager.model.objects.using(db).get(pk=user_id)
        except user_db_manager.model.DoesNotExist:
            return None

        # Attach db_label so the serializer can include it
        user.read_from = db_label
        return user
