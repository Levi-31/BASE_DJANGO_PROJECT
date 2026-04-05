"""
Database Router — directs writes to default (main) and distributes
reads between default and replica with ~50/50 probability using a
hash-based approach.
"""

import hashlib
import os
import time


class PrimaryReplicaRouter:
    """
    Routes all write operations to the 'default' (primary) database.
    Routes read operations to either 'default' or 'replica' with
    equal probability using a hash of (pid + monotonic timestamp).
    """

    READ_DATABASES = ("default", "replica")

    @classmethod
    def pick_read_db(cls):
        """
        Hash-based coin-flip:
        Combine the current PID with a high-resolution monotonic timestamp,
        hash it, and use the last byte to decide 0 or 1.
        """
        raw = f"{os.getpid()}-{time.monotonic_ns()}"
        digest = hashlib.md5(raw.encode()).hexdigest()
        index = int(digest[-1], 16) % 2   # 0 or 1
        return cls.READ_DATABASES[index]

    def db_for_read(self, model, **hints):
        """Distribute reads between default and replica."""
        return self.pick_read_db()

    def db_for_write(self, model, **hints):
        """All writes go to the primary."""
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between objects in the same DB pool."""
        db_set = {"default", "replica"}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Only allow migrations on the primary database."""
        return db == "default"
