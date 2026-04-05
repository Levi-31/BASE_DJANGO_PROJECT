"""
DB Managers — model-specific manager classes that extend BaseDBManager.

Each manager binds to a specific model and provides a clean interface
for controllers to perform database operations.
"""

from apps.core.base_db_manager import GenericBaseDBManager
from apps.core.models import User


class UserDBManager(GenericBaseDBManager):
    """
    DB Manager for the User model.

    Write operations go to the default (main) database.
    Read operations can be routed to the replica via
    get_from_replica() / filter_from_replica().
    """
    model = User
    has_active_filter = False
