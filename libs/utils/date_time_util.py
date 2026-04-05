import datetime
from django.utils import timezone

def get_current_datetime() -> datetime.datetime:
    """
    Returns the current timezone-aware datetime.
    """
    return timezone.now()

def get_current_date() -> datetime.date:
    """
    Returns the current local date.
    """
    return timezone.localdate()

def str_to_datetime(date_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime.datetime:
    """
    Coverts a string to a timezone-aware datetime object.
    """
    naive_dt = datetime.datetime.strptime(date_string, format_str)
    return timezone.make_aware(naive_dt)

def datetime_to_str(dt: datetime.datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Converts a datetime object to a string.
    """
    return dt.strftime(format_str)

def add_days_to_datetime(dt: datetime.datetime, days: int) -> datetime.datetime:
    """
    Adds a specified number of days to a datetime object.
    """
    return dt + datetime.timedelta(days=days)

def subtract_days_from_datetime(dt: datetime.datetime, days: int) -> datetime.datetime:
    """
    Subtracts a specified number of days from a datetime object.
    """
    return dt - datetime.timedelta(days=days)

def is_expired(target_dt: datetime.datetime) -> bool:
    """
    Checks if a target datetime has passed the current time.
    """
    return target_dt < get_current_datetime()
