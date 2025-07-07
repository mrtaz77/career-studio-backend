from src.auth.constants import (
    EMAIL_UNAVAILABLE,
    USER_ALREADY_EXISTS,
    USER_NOT_FOUND,
    USERNAME_UNAVAILABLE,
)


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user that already exists."""

    def __init__(self) -> None:
        super().__init__(USER_ALREADY_EXISTS)
        self.status_code = 409


class UserNotFoundException(Exception):
    """Raised when a user is not found in the database."""

    def __init__(self) -> None:
        super().__init__(USER_NOT_FOUND)
        self.status_code = 404


class UsernameUnavailableException(Exception):
    """Raised when the requested username is already taken."""

    def __init__(self) -> None:
        super().__init__(USERNAME_UNAVAILABLE)
        self.status_code = 400


class EmailUnavailableException(Exception):
    """Raised when the requested email is already associated with an account."""

    def __init__(self) -> None:
        super().__init__(EMAIL_UNAVAILABLE)
        self.status_code = 400
