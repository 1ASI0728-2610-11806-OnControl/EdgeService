"""Domain entities for the Health-bounded context."""
from datetime import datetime


class HealthRecord:
    """Represents a health record entity in the Health context.

    Attributes:
        id (int, optional): Unique identifier for the record.
        device_id (str): Identifier of the device that generated the record.
        bpm (float): Beats per minute (heart rate).
        temp (float): Body temperature in Celsius.
        spo2 (float): Blood oxygen saturation percentage.
        created_at (datetime): Timestamp when the record was created.
    """

    def __init__(self, device_id: str, bpm: float, temp: float, spo2: float, created_at: datetime, id: int = None):
        """Initialize a HealthRecord instance.

        Args:
            device_id (str): Device identifier.
            bpm (float): Heart rate in beats per minute.
            temp (float): Body temperature in Celsius.
            spo2 (float): Blood oxygen saturation percentage (0-100).
            created_at (datetime): Creation timestamp.
            id (int, optional): Record identifier. Defaults to None.
        """
        self.id = id
        self.device_id = device_id
        self.bpm = bpm
        self.temp = temp
        self.spo2 = spo2
        self.created_at = created_at
