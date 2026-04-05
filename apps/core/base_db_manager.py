"""
Base DB Managers — reusable query layer for all models.

Provides BaseDBManager, BuySellCarBaseDBManager, and GenericBaseDBManager
with support for main/replica database routing.
"""

from django.db import close_old_connections, connection, connections
from MySQLdb._mysql import OperationalError

from libs.utils import date_time_util


# ──────────────────────────────────────────────
# Cursor helpers (previously in libs.mysql_helper)
# ──────────────────────────────────────────────

def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dicts."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def namedtuplefetchall(cursor):
    """Return all rows from a cursor as a list of namedtuples."""
    from collections import namedtuple
    desc = cursor.description
    nt_result = namedtuple("Row", [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


# ──────────────────────────────────────────────
# BaseDBManager
# ──────────────────────────────────────────────

class BaseDBManager:
    model = None
    has_active_filter = False

    # ── writes (default / main DB) ──────────────

    def update_with_filter(self, filters=None, updates=None, excludes=None):
        if filters is None:
            filters = {}
        if updates is None:
            updates = {}
        if excludes is None:
            excludes = {}

        try:
            obj = self.model.objects.filter(**filters).exclude(**excludes).update(**updates)
        except OperationalError:
            obj = self.model.objects.filter(**filters).exclude(**excludes).update(**updates)
        return obj, None

    def get(self, **filters):
        if "active" not in filters and self.has_active_filter:
            filters["active"] = True

        try:
            return self.model.objects.get(**filters)
        except self.model.DoesNotExist:
            return None

    def get_from_replica(self, **filters):
        """Read from the replica database."""
        if "active" not in filters and self.has_active_filter:
            filters["active"] = True

        try:
            return self.model.objects.using("replica").get(**filters)
        except self.model.DoesNotExist:
            return None

    def get_with_row_lock(self, **filters):
        if "active" not in filters and self.has_active_filter:
            filters["active"] = True

        try:
            return self.model.objects.select_for_update().get(**filters)
        except self.model.DoesNotExist:
            return None

    def create(self, **data):
        return self.model.objects.create(**data)

    def update(self, query, **updates):
        objs = []
        try:
            objs = query.update(**updates)
        except OperationalError:
            objs = query.update(**updates)
        return objs, None

    def update_obj(self, obj, **updates):
        for key, value in updates.items():
            setattr(obj, key, value)
        obj.save()

    def update_obj_new(self, obj, **kwargs):
        fields_to_update = []
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
                fields_to_update.append(key)
        if fields_to_update:
            if hasattr(obj, "updated_at"):
                fields_to_update.append("updated_at")
                obj.updated_at = date_time_util.get_current_datetime()
            elif hasattr(obj, "updated"):
                fields_to_update.append("updated")
                obj.updated = date_time_util.get_current_datetime()
            obj.save(update_fields=fields_to_update)

    def update_via_filter(self, include_inactive=False, filters=None, updates=None, excludes=None):
        if filters is None:
            filters = {}
        if updates is None:
            updates = {}
        if excludes is None:
            excludes = {}

        if self.has_active_filter and (not include_inactive):
            excludes["active"] = False

        try:
            obj = self.model.objects.filter(**filters).exclude(**excludes).update(**updates)
        except OperationalError:
            obj = self.model.objects.filter(**filters).exclude(**excludes).update(**updates)
        return obj, None

    def update_via_qfilter(self, include_inactive=False, qfilters=None, updates=None, excludes=None):
        if qfilters is None:
            qfilters = {}
        if updates is None:
            updates = {}
        if excludes is None:
            excludes = {}

        if self.has_active_filter and (not include_inactive):
            excludes["active"] = False

        try:
            obj = self.model.objects.filter(qfilters).exclude(**excludes).update(**updates)
        except OperationalError:
            obj = self.model.objects.filter(qfilters).exclude(**excludes).update(**updates)
        return obj, None

    def filter(
        self,
        get_first=False,
        get_last=False,
        include_inactive=False,
        excludes=None,
        order_by="",
        select_for_update=False,
        nowait=False,
        **filters,
    ):
        if excludes is None:
            excludes = {}
        if self.has_active_filter and (not include_inactive):
            excludes["active"] = False
        else:
            if "active" in excludes:
                excludes.pop("active")

        if select_for_update:
            objs = self.model.objects.select_for_update(nowait=nowait)
        else:
            objs = self.model.objects

        try:
            objs = objs.filter(**filters).exclude(**excludes)
        except OperationalError:
            objs = objs.filter(**filters).exclude(**excludes)

        if order_by:
            objs = objs.order_by(order_by)

        if get_first:
            objs = objs.first()

        if get_last:
            objs = objs.last()

        return objs

    def filter_from_replica(
        self,
        get_first=False,
        get_last=False,
        include_inactive=False,
        excludes=None,
        order_by="",
        **filters,
    ):
        """Run filter queries against the replica database."""
        if excludes is None:
            excludes = {}
        if self.has_active_filter and (not include_inactive):
            excludes["active"] = False
        else:
            if "active" in excludes:
                excludes.pop("active")

        try:
            objs = self.model.objects.using("replica").filter(**filters).exclude(**excludes)
        except OperationalError:
            objs = self.model.objects.using("replica").filter(**filters).exclude(**excludes)

        if order_by:
            objs = objs.order_by(order_by)

        if get_first:
            objs = objs.first()

        if get_last:
            objs = objs.last()

        return objs

    def filter_without_active(
        self, get_first=False, get_last=False, include_inactive=False, excludes=None, order_by="", **filters
    ):
        if excludes is None:
            excludes = {}
        try:
            objs = self.model.objects.filter(**filters).exclude(**excludes)
        except OperationalError:
            objs = self.model.objects.filter(**filters).exclude(**excludes)

        if order_by:
            objs = objs.order_by(order_by)

        if get_first:
            objs = objs.first()

        if get_last:
            objs = objs.last()

        return objs

    def filter_queryset(self, queryset=None, get_first=False, get_last=False, excludes=None, order_by="", **filters):
        if excludes is None:
            excludes = {}
        if not queryset:
            return []

        try:
            objs = queryset.filter(**filters).exclude(**excludes)
        except OperationalError:
            objs = queryset.filter(**filters).exclude(**excludes)

        if order_by:
            objs = objs.order_by(order_by)

        if get_first:
            objs = objs.first()

        if get_last:
            objs = objs.last()

        return objs, None

    def get_or_create(self, defaults=None, **data):
        if defaults is None:
            defaults = {}
        obj, flag = self.model.objects.get_or_create(**data, defaults=defaults)
        return obj

    def update_or_create(self, defaults=None, **data):
        if defaults is None:
            defaults = {}
        obj, flag = self.model.objects.update_or_create(**data, defaults=defaults)
        return obj

    def execute_query(self, query):
        try:
            objs = self.model.objects.raw(query)
        except OperationalError:
            objs = self.model.objects.raw(query)
        return objs, None

    def bulk_create(self, data_list):
        return self.model.objects.bulk_create(data_list)

    def raw_execute_query(self, query):
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = dictfetchall(cursor)
        return results

    def get_object(self, data):
        return self.model(**data)


# ──────────────────────────────────────────────
# GenericBaseDBManager (uses is_active instead of active)
# ──────────────────────────────────────────────

class GenericBaseDBManager:
    model = None
    has_active_filter = False

    def get(self, **filters):
        if "is_active" not in filters and self.has_active_filter:
            filters["is_active"] = True
        try:
            return self.model.objects.get(**filters)
        except self.model.DoesNotExist:
            return None

    def get_from_replica(self, **filters):
        """Read from the replica database."""
        if "is_active" not in filters and self.has_active_filter:
            filters["is_active"] = True
        try:
            return self.model.objects.using("replica").get(**filters)
        except self.model.DoesNotExist:
            return None

    def create(self, data):
        return self.model.objects.create(**data)

    def update(self, query, updates):
        objs = []
        try:
            objs = query.update(**updates)
        except OperationalError:
            objs = query.update(**updates)
        return objs, None

    def update_obj(self, obj, **updates):
        for key, value in updates.items():
            setattr(obj, key, value)
        obj.save()

    def update_obj_new(self, obj, **kwargs):
        fields_to_update = []
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
                fields_to_update.append(key)
        if fields_to_update:
            if hasattr(obj, "updated_at"):
                fields_to_update.append("updated_at")
                obj.updated_at = date_time_util.get_current_datetime()
            elif hasattr(obj, "updated"):
                fields_to_update.append("updated")
                obj.updated = date_time_util.get_current_datetime()
            obj.save(update_fields=fields_to_update)

    def update_via_filter(self, include_inactive=False, filters=None, updates=None, excludes=None):
        if excludes is None:
            excludes = {}
        if updates is None:
            updates = {}
        if filters is None:
            filters = {}
        objs = []
        if self.has_active_filter and not include_inactive:
            excludes["is_active"] = False
        else:
            if "is_active" in excludes:
                excludes.pop("is_active")

        try:
            objs = self.model.objects.filter(**filters).exclude(**excludes).update(**updates)
        except OperationalError:
            objs = self.model.objects.filter(**filters).exclude(**excludes).update(**updates)

        return objs, None

    def filter(
        self,
        get_first=False,
        get_last=False,
        include_inactive=False,
        excludes=None,
        order_by="",
        order_list=None,
        select_for_update=False,
        nowait=False,
        **filters,
    ):
        if order_list is None:
            order_list = []
        if excludes is None:
            excludes = {}
        if self.has_active_filter and not include_inactive:
            excludes["is_active"] = False
        else:
            if "is_active" in excludes:
                excludes.pop("is_active")

        if select_for_update:
            objs = self.model.objects.select_for_update(nowait=nowait)
        else:
            objs = self.model.objects

        try:
            objs = objs.filter(**filters).exclude(**excludes)
        except OperationalError:
            objs = objs.filter(**filters).exclude(**excludes)

        if order_by:
            objs = objs.order_by(order_by)

        if order_list:
            objs = objs.order_by(*order_list)

        if get_first:
            objs = objs.first()

        if get_last:
            objs = objs.last()

        return objs

    def filter_from_replica(
        self,
        get_first=False,
        get_last=False,
        include_inactive=False,
        excludes=None,
        order_by="",
        **filters,
    ):
        """Run filter queries against the replica database."""
        if excludes is None:
            excludes = {}
        if self.has_active_filter and not include_inactive:
            excludes["is_active"] = False
        else:
            if "is_active" in excludes:
                excludes.pop("is_active")

        try:
            objs = self.model.objects.using("replica").filter(**filters).exclude(**excludes)
        except OperationalError:
            objs = self.model.objects.using("replica").filter(**filters).exclude(**excludes)

        if order_by:
            objs = objs.order_by(order_by)

        if get_first:
            objs = objs.first()

        if get_last:
            objs = objs.last()

        return objs

    def filter_without_active(
        self, get_first=False, get_last=False, include_inactive=False, excludes=None, order_by="", **filters
    ):
        if excludes is None:
            excludes = {}
        try:
            objs = self.model.objects.filter(**filters).exclude(**excludes)
        except OperationalError:
            objs = self.model.objects.filter(**filters).exclude(**excludes)

        if order_by:
            objs = objs.order_by(order_by)

        if get_first:
            objs = objs.first()

        if get_last:
            objs = objs.last()

        return objs, None

    def filter_queryset(self, queryset=None, get_first=False, get_last=False, excludes=None, order_by="", **filters):
        if excludes is None:
            excludes = {}
        if not queryset:
            return []

        try:
            objs = queryset.filter(**filters).exclude(**excludes)
        except OperationalError:
            objs = queryset.filter(**filters).exclude(**excludes)

        if order_by:
            objs = objs.order_by(order_by)

        if get_first:
            objs = objs.first()

        if get_last:
            objs = objs.last()

        return objs, None

    def get_or_create(self, defaults=None, **data):
        if defaults is None:
            defaults = {}
        obj, flag = self.model.objects.get_or_create(**data, defaults=defaults)
        return obj

    def update_or_create(self, defaults=None, **data):
        if defaults is None:
            defaults = {}
        obj, flag = self.model.objects.update_or_create(**data, defaults=defaults)
        return obj

    def execute_query(self, query):
        close_old_connections()
        data = self.model.objects.raw(query)
        close_old_connections()
        return data

    def execute_query_to_dict(self, query):
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = dictfetchall(cursor)
        return results

    def bulk_create(self, data_list):
        return self.model.objects.bulk_create(data_list)

    def raw_execute_query(self, query):
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = dictfetchall(cursor)
        return results
