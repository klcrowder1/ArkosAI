"""
Migration to add TOTP device table for two-factor authentication.
"""

from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    DoubleField,
    ForeignKeyField,
    Model,
    UUIDField,
)
from playhouse.migrate import SqliteMigrator, migrate

from arkos.models import User


def migrate_forward(migrator: SqliteMigrator):
    """
    Migrate forward.
    
    Args:
        migrator: SqliteMigrator instance
    """
    # Create the TOTP device table
    migrate(
        migrator.create_table(
            "totpdevice",
            (
                ("id", UUIDField(primary_key=True)),
                ("user_id", ForeignKeyField(User, backref="totp_devices")),
                ("name", CharField(max_length=100)),
                ("secret", CharField(max_length=64)),
                ("created_at", DateTimeField()),
                ("confirmed_at", DoubleField(null=True)),
                ("last_used_at", DoubleField(null=True)),
                ("is_active", BooleanField(default=False)),
            ),
        ),
    )


def migrate_backward(migrator: SqliteMigrator):
    """
    Migrate backward.
    
    Args:
        migrator: SqliteMigrator instance
    """
    # Drop the TOTP device table
    migrate(
        migrator.drop_table("totpdevice"),
    )
