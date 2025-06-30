from src.users.constants import (
    INVALID_PHONE_NUMBER,
    INVALID_PHONE_NUMBER_FORMAT,
    USERNAME_UNAVAILABLE,
)


class UsernameUnavailableException(Exception):
    """Exception raised when a username is unavailable."""

    def __init__(self) -> None:
        self.message = USERNAME_UNAVAILABLE
        super().__init__(self.message)
        self.status_code = 409


class InvalidPhoneNumberFormatException(Exception):
    """Exception raised for invalid phone number format."""

    def __init__(self) -> None:
        self.message = INVALID_PHONE_NUMBER_FORMAT
        super().__init__(self.message)
        self.status_code = 400


class InvalidPhoneNumberException(Exception):
    """Exception raised for invalid phone number."""

    def __init__(self) -> None:
        self.message = INVALID_PHONE_NUMBER
        super().__init__(self.message)
        self.status_code = 400
