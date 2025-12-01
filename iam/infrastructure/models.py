"""Peewee models for the IAM bounded context."""
from peewee import Model, CharField, DateTimeField, AutoField
from shared.infrastructure.database import db


class Device(Model):
    """Peewee model for the 'devices' table.

    Attributes:
        device_id (CharField): Unique identifier (primary key).
        api_key (CharField): API key for authentication.
        created_at (DateTimeField): Creation timestamp.
    """
    device_id   = CharField(primary_key=True)
    api_key     = CharField()
    created_at  = DateTimeField()

    class Meta:
        """Metadata for the Device model."""
        database    = db
        table_name  = 'devices'


class DeviceOwnership(Model):
    """
    Peewee model for the 'device_ownership' table.
    Maps a patient_profile_id to a device_id.
    """
    id = AutoField() # Primary key
    patient_profile_id = CharField()
    device_id = CharField(unique=True) # Ensure device_id is unique

    class Meta:
        database = db
        table_name = 'device_ownership'
