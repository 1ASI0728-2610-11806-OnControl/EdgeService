"""Application services for the Health-bounded context."""

from health.domain.entities import HealthRecord
from health.domain.services import HealthRecordService
from health.infrastructure.repositories import HealthRecordRepository
from iam.infrastructure.repositories import DeviceRepository

class HealthRecordApplicationService:
    """Application service for creating health records."""

    def __init__(self):
        """Initialize the HealthRecordApplicationService."""
        self.health_record_repository = HealthRecordRepository()
        self.health_record_service = HealthRecordService()
        self.device_repository = DeviceRepository()

    def create_health_record(self, device_id: str, bpm: float, temp: float, spo2: float, created_at: str, api_key: str) -> tuple[HealthRecord, bool]:
        """Create a health record after validating the device.

        Args:
            device_id (str): Device identifier.
            bpm (float): Heart rate in beats per minute.
            temp (float): Body temperature in Celsius.
            spo2 (float): Blood oxygen saturation percentage.
            created_at (str): ISO 8601 timestamp.
            api_key (str): API key for device authentication.

        Returns:
            tuple[HealthRecord, bool]: The created record and a boolean indicating if an alert should be triggered.

        Raises:
            ValueError: If the device_id and api_key are invalid.
        """
        # Validate device_id exists in IAM context
        if not self.device_repository.find_by_id_and_api_key(device_id, api_key):
            raise ValueError("Device not found")
            
        record = self.health_record_service.create_record(device_id, bpm, temp, spo2, created_at)
        saved_record = self.health_record_repository.save(record)
        
        # Check for health risks to trigger actuator
        trigger_alert = self.health_record_service.check_health_risk(bpm, temp, spo2)
        
        return saved_record, trigger_alert

    def get_all_health_records(self) -> list[HealthRecord]:
        """Fetch all health records.

        Returns:
            list[HealthRecord]: A list of all health records.
        """
        return self.health_record_repository.find_all()

    def get_records_for_device(self, device_id: str) -> list[HealthRecord]:
        """Fetch all health records for a specific device.

        Args:
            device_id (str): The device identifier.

        Returns:
            list[HealthRecord]: A list of health records.
        """
        return self.health_record_repository.find_by_device_id(device_id)

    def get_latest_record_for_device(self, device_id: str) -> HealthRecord | None:
        """Fetch the latest health record for a specific device.

        Args:
            device_id (str): The device identifier.

        Returns:
            HealthRecord | None: The latest health record or None if not found.
        """
        return self.health_record_repository.find_latest_for_device(device_id)

    def get_records_for_devices(self, device_ids: list[str]) -> list[HealthRecord]:
        """Fetch all health records for a list of specific devices.

        Args:
            device_ids (list[str]): A list of device identifiers.

        Returns:
            list[HealthRecord]: A list of health records for the specified devices.
        """
        return self.health_record_repository.find_by_device_ids(device_ids)

    def get_latest_record_for_devices(self, device_ids: list[str]) -> HealthRecord | None:
        """Fetch the single latest health record for a list of specific devices.

        Args:
            device_ids (list[str]): A list of device identifiers.

        Returns:
            HealthRecord | None: The latest health record among the specified devices, or None if not found.
        """
        return self.health_record_repository.find_latest_for_devices(device_ids)

    def check_health_risk(self, bpm: float, temp: float, spo2: float) -> bool:
        """Check if the health metrics indicate a risk situation."""
        return self.health_record_service.check_health_risk(bpm, temp, spo2)
