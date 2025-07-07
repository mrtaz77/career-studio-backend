from src.cv.constants import (
    CV_INVALID_TEMPLATE,
    CV_INVALID_TYPE,
    CV_NOT_FOUND,
    CV_SAVE_FAILED,
)


class CVNotFoundException(Exception):
    def __init__(self, message: str = CV_NOT_FOUND) -> None:
        self.message = message
        self.status_code = 404
        super().__init__(self.message)


class CVSaveException(Exception):
    def __init__(self, message: str = CV_SAVE_FAILED) -> None:
        self.message = message
        self.status_code = 500
        super().__init__(self.message)


class CVInvalidTypeException(Exception):
    def __init__(self, message: str = CV_INVALID_TYPE) -> None:
        self.message = message
        self.status_code = 400
        super().__init__(self.message)


class CVInvalidTemplateException(Exception):
    def __init__(self, message: str = CV_INVALID_TEMPLATE) -> None:
        self.message = message
        self.status_code = 404
        super().__init__(self.message)
