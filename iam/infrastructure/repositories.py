"""Repositories for the IAM bounded context."""
import os
from datetime import datetime, timezone
from typing import Optional

import peewee

from iam.domain.entities import Device
from iam.infrastructure.models import Device as DeviceModel, DeviceOwnership as DeviceOwnershipModel

class DeviceRepository:
    """Repository for managing Device entities."""

    DEFAULT_DEVICE_ID = "smart-band-001"
    DEFAULT_DEVICE_API_KEY = "oncontrol-grupo2-demo-key"

    @staticmethod
    def find_by_id_and_api_key(device_id: str, api_key: str) -> Optional[Device]:
        """Find a device by its ID and API key.

        Args:
            device_id (str): Unique identifier of the device.
            api_key (str): API key for authentication.

        Returns:
            Optional[Device]: Device entity if found, None otherwise.
        """
        try:
            device = DeviceModel.get(
                (DeviceModel.device_id == device_id) & (DeviceModel.api_key == api_key)
            )
            return Device(device.device_id, device.api_key, device.created_at)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def get_or_create_test_device() -> Device:
        """Get or create a test device for development.

        Returns:
            Device: The test device entity.
        """
        device_id = os.getenv("DEVICE_ID", DeviceRepository.DEFAULT_DEVICE_ID)
        api_key = os.getenv("DEVICE_API_KEY", DeviceRepository.DEFAULT_DEVICE_API_KEY)

        device, _ = DeviceModel.get_or_create(
            device_id=device_id,
            defaults={
                "api_key": api_key,
                "created_at": datetime.now(timezone.utc)
            }
        )

        if device.api_key != api_key:
            device.api_key = api_key
            device.save()

        return Device(device.device_id, device.api_key, device.created_at)


class DeviceOwnershipRepository:
    """Repository for managing DeviceOwnership entities."""

    @staticmethod
    def create(patient_profile_id: str, device_id: str) -> DeviceOwnershipModel:
        """Create a new device ownership record."""
        return DeviceOwnershipModel.create(
            patient_profile_id=patient_profile_id,
            device_id=device_id
        )

    @staticmethod
    def find_by_device_id(device_id: str) -> Optional[DeviceOwnershipModel]:
        """Find a device ownership record by device ID."""
        try:
            return DeviceOwnershipModel.get(DeviceOwnershipModel.device_id == device_id)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def find_devices_by_patient_profile_id(patient_profile_id: str) -> list[DeviceOwnershipModel]:
        """Find all device ownership records for a specific patient profile ID."""
        return list(DeviceOwnershipModel.select().where(DeviceOwnershipModel.patient_profile_id == patient_profile_id))
