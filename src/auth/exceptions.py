from src.auth.constants import USER_ALREADY_EXISTS, USER_NOT_FOUND


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
