"""
Core models.

Maps to the existing `user` table in MySQL.
Uses managed = False since the table is already created.
"""

from django.db import models


class User(models.Model):
    """
    Maps to the existing `user` table.

    CREATE TABLE `user` (
      `id`         int NOT NULL AUTO_INCREMENT,
      `username`   varchar(50)  NOT NULL,
      `email`      varchar(100) NOT NULL,
      `password`   varchar(255) NOT NULL,
      `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      UNIQUE KEY `username` (`username`),
      UNIQUE KEY `email`    (`email`)
    )
    """

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "user"
        managed = False          # table already exists in MySQL
        ordering = ["-created_at"]

    def __str__(self):
        return self.username
