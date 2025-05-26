from src.users.constants import USERNAME_UNAVAILABLE


class UsernameUnavailableException(Exception):
    """Exception raised when a username is unavailable."""

    def __init__(self) -> None:
        self.message = USERNAME_UNAVAILABLE
        super().__init__(self.message)
        self.status_code = 409
