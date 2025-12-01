"""
Repository for health record persistence.

Handles saving health records to the database using Peewee ORM models.
"""
from dateutil.parser import parse
from health.domain.entities import HealthRecord
from health.infrastructure.models import HealthRecord as HealthRecordModel


class HealthRecordRepository:
    """
    Repository for managing HealthRecord persistence.
    """
    @staticmethod
    def save(health_record) -> HealthRecord:
        """
        Save a HealthRecord entity to the database.
        Args:
            health_record (HealthRecord): The health record to save.
        Returns:
            HealthRecord: The saved health record with assigned ID.
        """
        record = HealthRecordModel.create(
            device_id   =   health_record.device_id,
            bpm         =   health_record.bpm,
            temp        =   health_record.temp,
            spo2        =   health_record.spo2,
            created_at  =   health_record.created_at
        )
        return HealthRecord(
            health_record.device_id,
            health_record.bpm,
            health_record.temp,
            health_record.spo2,
            health_record.created_at,
            record.id
        )

    @staticmethod
    def find_all() -> list[HealthRecord]:
        """
        Fetch all health records from the database, ordered by creation date.
        Returns:
            list[HealthRecord]: A list of all health records.
        """
        records = HealthRecordModel.select().order_by(HealthRecordModel.created_at.desc())
        return [
            HealthRecord(
                device_id=record.device_id,
                bpm=record.bpm,
                temp=record.temp,
                spo2=record.spo2,
                created_at=parse(record.created_at) if isinstance(record.created_at, str) else record.created_at,
                id=record.id
            ) for record in records
        ]

    @staticmethod
    def find_by_device_id(device_id: str) -> list[HealthRecord]:
        """
        Fetch all health records for a specific device from the database.
        Args:
            device_id (str): The device identifier.
        Returns:
            list[HealthRecord]: A list of health records for the specified device.
        """
        records = HealthRecordModel.select().where(HealthRecordModel.device_id == device_id).order_by(HealthRecordModel.created_at.desc())
        return [
            HealthRecord(
                device_id=record.device_id,
                bpm=record.bpm,
                temp=record.temp,
                spo2=record.spo2,
                created_at=parse(record.created_at) if isinstance(record.created_at, str) else record.created_at,
                id=record.id
            ) for record in records
        ]

    @staticmethod
    def find_latest_for_device(device_id: str) -> HealthRecord | None:
        """
        Fetch the latest health record for a specific device from the database.
        Args:
            device_id (str): The device identifier.
        Returns:
            HealthRecord | None: The latest health record entity or None if not found.
        """
        record = HealthRecordModel.select().where(HealthRecordModel.device_id == device_id).order_by(HealthRecordModel.created_at.desc()).get_or_none()

        if not record:
            return None

        return HealthRecord(
            device_id=record.device_id,
            bpm=record.bpm,
            temp=record.temp,
            spo2=record.spo2,
            created_at=parse(record.created_at) if isinstance(record.created_at, str) else record.created_at,
            id=record.id
        )

    @staticmethod
    def find_by_device_ids(device_ids: list[str]) -> list[HealthRecord]:
        """
        Fetch all health records for a list of specific devices from the database.
        Args:
            device_ids (list[str]): A list of device identifiers.
        Returns:
            list[HealthRecord]: A list of health records for the specified devices.
        """
        if not device_ids:
            return [] # Return empty list if no device IDs are provided

        records = HealthRecordModel.select().where(HealthRecordModel.device_id.in_(device_ids)).order_by(HealthRecordModel.created_at.desc())
        return [
            HealthRecord(
                device_id=record.device_id,
                bpm=record.bpm,
                temp=record.temp,
                spo2=record.spo2,
                created_at=parse(record.created_at) if isinstance(record.created_at, str) else record.created_at,
                id=record.id
            ) for record in records
        ]

    @staticmethod
    def find_latest_for_devices(device_ids: list[str]) -> HealthRecord | None:
        """
        Fetch the single latest health record for a list of specific devices from the database.
        Args:
            device_ids (list[str]): A list of device identifiers.
        Returns:
            HealthRecord | None: The latest health record entity among the specified devices, or None if not found.
        """
        if not device_ids:
            return None

        record = HealthRecordModel.select().where(HealthRecordModel.device_id.in_(device_ids)).order_by(HealthRecordModel.created_at.desc()).get_or_none()

        if not record:
            return None

        return HealthRecord(
            device_id=record.device_id,
            bpm=record.bpm,
            temp=record.temp,
            spo2=record.spo2,
            created_at=parse(record.created_at) if isinstance(record.created_at, str) else record.created_at,
            id=record.id
        )
