"""
Core views — using base_api_view pattern.

Each view declares serializer_class and controller_class,
then delegates to controller_class(validated_data, user, headers).process()
"""

from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny

from apps.core.base_api_view import GetApiBaseView, CreateApiBaseView
from apps.core.controllers import (
    HealthCheckController,
    HelloController,
    UserCreateController,
    UserReadController,
)
from apps.core.serializers import (
    HealthCheckSerializer,
    HelloSerializer,
    UserCreateSerializer,
    UserReadSerializer,
)


# ───────────────────────────────────────────
# Health Check
# ───────────────────────────────────────────

class HealthCheckView(GetApiBaseView):
    serializer_class = HealthCheckSerializer
    controller_class = HealthCheckController
    permission_classes = [AllowAny]

    def get_(self, *args, **kwargs):
        return self.controller_class(self.validated_data, args[0].user, args[0].headers).process()


# ───────────────────────────────────────────
# Hello Message
# ───────────────────────────────────────────

class HelloMessageView(CreateApiBaseView):
    serializer_class = HelloSerializer
    controller_class = HelloController
    permission_classes = [AllowAny]

    def post_(self, request, **kwargs):
        return self.controller_class(self.validated_data, request.user, request.headers).process()


# ───────────────────────────────────────────
# User — Create (POST → writes to main DB)
# ───────────────────────────────────────────

class UserCreateView(CreateApiBaseView):
    serializer_class = UserCreateSerializer
    controller_class = UserCreateController
    permission_classes = [AllowAny]

    def post_(self, request, **kwargs):
        return self.controller_class(self.validated_data, request.user, request.headers).process()


# ───────────────────────────────────────────
# User — Read (GET → hash-based main/replica)
# ───────────────────────────────────────────

class UserReadView(GetApiBaseView):
    serializer_class = UserReadSerializer
    controller_class = UserReadController
    permission_classes = [AllowAny]

    @property
    def success_response(self):
        from rest_framework import status
        from rest_framework.response import Response
        from libs.utils.api_response import generate_success_response, generate_error_response

        if self.response_data is None:
            msg_tuple = (1, "User not found", 404)
            resp_dict = generate_error_response(msg=msg_tuple)
            return Response(resp_dict, status=status.HTTP_404_NOT_FOUND)

        data = self.serializer_class(self.response_data).data
        db_label = getattr(self.response_data, "read_from", "UNKNOWN")
        data["read_from"] = db_label
        
        msg_tuple = (0, f"User retrieved successfully from {db_label}", 200)
        resp_dict = generate_success_response(data=data, msg=msg_tuple)
        return Response(resp_dict, status=status.HTTP_200_OK)

    def get_(self, *args, **kwargs):
        self.validated_data["user_id"] = kwargs.get("user_id")
        return self.controller_class(self.validated_data, args[0].user, args[0].headers).process()
