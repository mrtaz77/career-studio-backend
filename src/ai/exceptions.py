from src.ai.constants import (
    AI_USAGE_LIMIT_EXCEEDED_MESSAGE,
    REQUEST_LENGTH_LIMIT_EXCEEDED_MESSAGE,
)


class RequestLimitExceeded(Exception):
    def __init__(self, message: str = AI_USAGE_LIMIT_EXCEEDED_MESSAGE) -> None:
        self.message = message
        self.status_code = 429
        super().__init__(self.message)


class RequestLengthExceeded(Exception):
    def __init__(self, message: str = REQUEST_LENGTH_LIMIT_EXCEEDED_MESSAGE) -> None:
        self.message = message
        self.status_code = 413
        super().__init__(self.message)
