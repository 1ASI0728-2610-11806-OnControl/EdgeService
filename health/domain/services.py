"""Domain services for the Health-bounded context."""
from datetime import datetime, timezone

from dateutil.parser import parse

from health.domain.entities import HealthRecord


class HealthRecordService:
    """Service for managing health records."""

    def __init__(self):
        """Initialize the HealthRecordService.
        """

    @staticmethod
    def create_record(device_id: str, bpm: float, temp: float, spo2: float, created_at: str | None) -> HealthRecord:

        """Create a new health record.

                    Args:
                        device_id (str): Device identifier.
                        bpm (float): Heart rate in beats per minute.
                        temp (float): Body temperature in Celsius (30-45 valid range).
                        spo2 (float): Blood oxygen saturation percentage (0-100).
                        created_at (str): ISO 8601 timestamp (e.g., '2025-06-04T18:23:00-05:00').

                    Returns:
                        HealthRecord: The created health record entity.

                    Raises:
                        ValueError: If BPM, temp, or spo2 is invalid, or created_at is malformed.
                    """
        try:
            bpm = float(bpm)
            if not (0 <= bpm <= 200):
                raise ValueError("Invalid BPM value")

            temp = float(temp)

            spo2 = float(spo2)
            if not (0 <= spo2 <= 100):
                raise ValueError("Invalid SpO2 value")

            if created_at:
                parsed_created_at = parse(created_at).astimezone(timezone.utc)
            else:
                parsed_created_at = datetime.now(timezone.utc)
        except (ValueError, TypeError):
            raise ValueError("Invalid data format")

        return HealthRecord(device_id, bpm, temp, spo2, parsed_created_at)

    @staticmethod
    def check_health_risk(bpm: float, temp: float, spo2: float) -> bool:
        """
        Evaluates if the provided health metrics indicate a risk situation.
        
        Demo risk criteria:
        - BPM: > 120 or < 50
        - Temp: > 38.0 or < 35.5
        - SpO2: < 92
        
        Returns:
            bool: True if actuator alarm should be triggered, False otherwise.
        """
        bpm = float(bpm)
        temp = float(temp)
        spo2 = float(spo2)

        if bpm > 120 or bpm < 50:
            return True
        if temp > 38.0 or temp < 35.5:
            return True
        if spo2 < 92:
            return True
        return False
