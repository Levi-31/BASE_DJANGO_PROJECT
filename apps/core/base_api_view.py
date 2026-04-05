"""
Base API Views — abstract base classes that standardise the
request → validate → process → serialize → respond lifecycle.

All concrete views should inherit from one of these and implement
the abstract method (get_, post_, patch_, delete_).
"""

from abc import ABC, abstractmethod

from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from rest_framework.response import Response

from libs.utils.api_response import (
    generate_success_response,
    generate_error_response
)


# ──────────────────────────────────────────────
# Fallback defaults
# ──────────────────────────────────────────────

class GenericSerializer(BaseSerializer):
    """No-op serializer used as default when no serializer_class is set."""

    def to_internal_value(self, data):
        return data

    def to_representation(self, instance):
        if isinstance(instance, dict):
            return instance
        return {}


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "limit"
    max_page_size = 500


def prepare_success_response(data=None, extras=None):
    """Wraps data inside the project's standard libs JSON envelope."""
    resp_dict = generate_success_response(data=data)
    # Map back to Djangos REST Response (assuming 200 OK for standard successes)
    return Response(resp_dict, status=200)


# ──────────────────────────────────────────────
# GET
# ──────────────────────────────────────────────

class GetApiBaseView(APIView, ABC):
    serializer_class = GenericSerializer
    many = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validated_data = None
        self.response_data = None
        self.request = None

    def get(self, *args, **kwargs):
        self.validate_data()
        self.response_data = self.get_(*args, **kwargs)
        return self.success_response

    def validate_data(self):
        request_data = self.query_data
        validator = self.serializer_class(data=request_data)
        validator.is_valid(raise_exception=True)
        self.validated_data = validator.validated_data

    @property
    def query_data(self):
        return self.request.GET

    @abstractmethod
    def get_(self, *args, **kwargs):
        pass

    @property
    def success_response(self):
        return prepare_success_response(data=self.final_response_structure)

    @property
    def final_response_structure(self):
        return self.serialized_response_data

    @property
    def serialized_response_data(self):
        return self.serializer_class(
            self.response_data,
            many=self.many,
        ).data


# ──────────────────────────────────────────────
# CREATE (POST)
# ──────────────────────────────────────────────

class CreateApiBaseView(APIView, ABC):
    serializer_class = GenericSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validated_data = None
        self.response_data = None
        self.request = None

    def post(self, request, **kwargs):
        self.validate_data()
        self.response_data = self.post_(request, **kwargs)
        return self.success_response

    def validate_data(self):
        request_data = self.request.data
        validator = self.serializer_class(data=request_data)
        validator.is_valid(raise_exception=True)
        self.validated_data = self.get_validated_data(validator)

    def get_validated_data(self, validator):
        return validator.validated_data

    def get_file_data(self):
        return self.request.FILES

    @abstractmethod
    def post_(self, request, **kwargs):
        pass

    @property
    def success_response(self):
        data = self.serializer_class(self.response_data).data
        return prepare_success_response(data=data)

    def set_extra_logging_data(self, data):
        self.request.META["extra_logging_data"] = data


# ──────────────────────────────────────────────
# UPDATE (PATCH)
# ──────────────────────────────────────────────

class UpdateApiBaseView(APIView, ABC):
    serializer_class = GenericSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validated_data = None
        self.response_data = None
        self.request = None

    def patch(self, request, **kwargs):
        self.validate_data()
        self.response_data = self.patch_(request, **kwargs)
        return self.success_response

    def validate_data(self):
        request_data = self.request.data
        validator = self.serializer_class(data=request_data)
        validator.is_valid(raise_exception=True)
        self.validated_data = self.get_validated_data(validator)

    def get_validated_data(self, validator):
        return validator.validated_data

    def get_file_data(self):
        return self.request.FILES

    @abstractmethod
    def patch_(self, request, **kwargs):
        pass

    @property
    def success_response(self):
        data = self.serializer_class(self.response_data).data
        return prepare_success_response(data=data)


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

class DeleteApiBaseView(APIView, ABC):
    serializer_class = GenericSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validated_data = None
        self.response_data = None
        self.request = None

    def delete(self, *args, **kwargs):
        self.validate_data()
        self.response_data = self.delete_(*args, **kwargs)
        return self.success_response

    def validate_data(self):
        request_data = self.query_data
        validator = self.serializer_class(data=request_data)
        validator.is_valid(raise_exception=True)
        self.validated_data = validator.validated_data

    @property
    def query_data(self):
        return self.request.GET

    @abstractmethod
    def delete_(self, *args, **kwargs):
        pass

    @property
    def success_response(self):
        data = self.serializer_class(self.response_data).data
        return prepare_success_response(data=data)


# ──────────────────────────────────────────────
# LIST (paginated via POST body)
# ──────────────────────────────────────────────

class ListApiBaseView(ListAPIView, ABC):
    pagination_class = LargeResultsSetPagination
    serializer_class = GenericSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validated_data = None
        self.response_data = None
        self.count = None
        self.request = None

    def post(self, request):
        self.request = request
        self.validate_data()
        self.response_data = self.post_(request)
        return self.success_response

    def validate_data(self):
        validator = self.serializer_class(data=self.query_data)
        validator.is_valid(raise_exception=True)
        self.validated_data = validator.validated_data

    @abstractmethod
    def post_(self, request):
        pass

    @property
    def query_data(self):
        valid_data = self.request.data
        for key in self.request.GET:
            valid_data[key] = self.request.GET.get(key)
        return valid_data

    @property
    def success_response(self):
        data = self.serializer_class(self.response_data, many=True).data
        paginated_qset = self.paginate_queryset(data)
        paginated_data = self.get_paginated_response(paginated_qset).data

        extras = {
            "page": 1 if self.validated_data.get("page") is None else self.validated_data.get("page"),
            "limit": self.validated_data.get("limit"),
        }
        return prepare_success_response(data=paginated_data, extras=extras)


# ──────────────────────────────────────────────
# POST LIST (returns count)
# ──────────────────────────────────────────────

class PostListApiBaseView(ListAPIView, ABC):
    pagination_class = LargeResultsSetPagination
    serializer_class = GenericSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validated_data = None
        self.response_data = None
        self.count = None
        self.request = None

    def post(self, request, *args, **kwargs):
        self.request = request
        self.validate_data()
        self.response_data, self.count = self.post_(request, *args, **kwargs)
        return self.success_response

    def validate_data(self):
        request_data = self.query_data
        validator = self.serializer_class(data=request_data)
        validator.is_valid(raise_exception=True)
        self.validated_data = validator.validated_data

    @abstractmethod
    def post_(self, request):
        pass

    @property
    def query_data(self):
        valid_data = self.request.data
        for key in self.request.GET:
            valid_data[key] = self.request.GET.get(key)
        return valid_data

    @property
    def success_response(self):
        serialized_data = self.serializer_class(self.response_data, many=True).data
        data = {
            "count": self.count,
            "results": serialized_data,
            "page": self.query_data.get("page") if self.query_data.get("page") else 1,
            "limit": self.query_data.get("limit"),
        }
        return prepare_success_response(data=data)


# ──────────────────────────────────────────────
# GET LIST (paginated via query params)
# ──────────────────────────────────────────────

class GetListApiBaseView(ListAPIView, ABC):
    pagination_class = LargeResultsSetPagination
    serializer_class = GenericSerializer
    many = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validated_data = None
        self.response_data = None
        self.count = None
        self.request = None

    def get(self, *args, **kwargs):
        self.validate_data()
        self.response_data, self.count = self.get_(*args, **kwargs)
        return self.success_response

    def validate_data(self):
        request_data = self.query_data
        validator = self.serializer_class(data=request_data, many=self.many)
        validator.is_valid(raise_exception=True)
        self.validated_data = validator.validated_data

    @abstractmethod
    def get_(self, request):
        pass

    @property
    def query_data(self):
        return self.request.GET

    @property
    def success_response(self):
        serialized_data = self.serializer_class(self.response_data, many=self.many).data
        data = {
            "count": self.count,
            "results": serialized_data,
            "page": self.query_data.get("page") if self.query_data.get("page") else 1,
            "limit": self.query_data.get("limit"),
        }
        return prepare_success_response(data=data)


# ──────────────────────────────────────────────
# Combined GET + POST base
# ──────────────────────────────────────────────

class BaseAPIView(APIView, ABC):
    serializer_class = GenericSerializer
    many = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validated_data = None
        self.response_data = None
        self.request = None

    def post(self, request, **kwargs):
        request_data = self.request.data
        self.validate_data(request_data)
        self.response_data = self.post_(request, **kwargs)
        return self.success_response

    def get(self, *args, **kwargs):
        request_data = self.query_data
        self.validate_data(request_data)
        self.response_data = self.get_(*args, **kwargs)
        return self.success_response

    def validate_data(self, request_data):
        validator = self.serializer_class(data=request_data)
        validator.is_valid(raise_exception=True)
        self.validated_data = self.get_validated_data(validator)

    def get_validated_data(self, validator):
        return validator.validated_data

    def post_(self, request, **kwargs):
        pass

    def get_(self, *args, **kwargs):
        pass

    def patch_(self, *args, **kwargs):
        pass

    @property
    def query_data(self):
        return self.request.GET

    @property
    def success_response(self):
        data = self.serializer_class(self.response_data).data
        return prepare_success_response(data=data)
