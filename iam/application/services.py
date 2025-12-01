"""Application services for the IAM bounded context."""
from typing import Optional
import peewee

from iam.domain.entities import Device
from iam.domain.services import AuthService
from iam.infrastructure.repositories import DeviceRepository, DeviceOwnershipRepository

class AuthApplicationService:
    """Application service for device authentication."""

    def __init__(self):
        """Initialize the AuthApplicationService."""
        self.device_repository = DeviceRepository()
        self.auth_service = AuthService()

    def authenticate(self, device_id: str, api_key: str) -> bool:
        """Authenticate a device.

        Args:
            device_id (str): Unique identifier of the device.
            api_key (str): API key for authentication.

        Returns:
            bool: True if authentication succeeds, False otherwise.
        """
        device: Optional[Device] = self.device_repository.find_by_id_and_api_key(device_id, api_key)
        return self.auth_service.authenticate(device)

    def get_or_create_test_device(self) -> Device:
        """Get or create a test device for development.

        Returns:
            Device: The test device entity.
        """
        return self.device_repository.get_or_create_test_device()


class DeviceOwnershipApplicationService:
    """Application service for managing device ownership."""

    def __init__(self):
        """Initialize the DeviceOwnershipApplicationService."""
        self.device_ownership_repository = DeviceOwnershipRepository()

    def claim_device(self, patient_profile_id: str, device_id: str) -> None:
        """
        Claims a device for a patient.
        Raises ValueError if the device is already claimed by another patient.
        """
        # Check if the device is already claimed
        existing_ownership = self.device_ownership_repository.find_by_device_id(device_id)

        if existing_ownership:
            if existing_ownership.patient_profile_id == patient_profile_id:
                # Device already claimed by this patient, nothing to do
                return
            else:
                raise ValueError(f"Device {device_id} is already claimed by another patient.")
        
        try:
            self.device_ownership_repository.create(patient_profile_id, device_id)
        except peewee.IntegrityError:
            # This handles the unlikely race condition if another process claimed it simultaneously
            raise ValueError(f"Device {device_id} is already claimed.")

    def get_devices_for_patient(self, patient_profile_id: str) -> list[str]:
        """
        Retrieves all device IDs claimed by a specific patient.
        """
        ownership_records = self.device_ownership_repository.find_devices_by_patient_profile_id(patient_profile_id)
        return [record.device_id for record in ownership_records]