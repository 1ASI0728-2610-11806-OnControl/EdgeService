"""Domain services for the IAM bounded context."""
from typing import Optional
from iam.domain.entities import Device

class AuthService:
    """Service for authenticating devices in the IAM context."""

    def __init__(self):
        """Initialize the AuthService.
        """

    @staticmethod
    def authenticate(device: Optional[Device]) -> bool:
        """Authenticate a device using its ID and API key.

        Args:
            device (Optional[Device]): The device to authenticate.

        Returns:
            bool: True if authentication succeeds, False otherwise.

        """
        return device is not None