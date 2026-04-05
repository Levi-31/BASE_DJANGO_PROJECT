"""
Core utilities — shared helpers used across views.
"""

from rest_framework.response import Response
from rest_framework import status


def generate_response(data=None, message="Success", status_code=status.HTTP_200_OK, errors=None):
    """
    Generic response builder.

    Returns a consistently shaped JSON envelope:
    {
        "success": true/false,
        "message": "...",
        "data": { ... } | [ ... ] | null,
        "errors": { ... } | null
    }
    """
    success = status_code < 400

    payload = {
        "success": success,
        "message": message,
        "data": data,
        "errors": errors,
    }

    return Response(payload, status=status_code)
