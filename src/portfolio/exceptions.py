from src.portfolio.constants import (
    PORTFOLIO_INVALID_THEME,
    PORTFOLIO_NOT_FOUND,
    PORTFOLIO_PUBLIC_NOT_FOUND,
    PORTFOLIO_PUBLISH_ERROR,
)


class PortfolioInvalidThemeException(Exception):
    def __init__(self, message: str = PORTFOLIO_INVALID_THEME) -> None:
        self.message = message
        self.status_code = 400
        super().__init__(self.message)


class PortfolioNotFoundException(Exception):
    def __init__(self, message: str = PORTFOLIO_NOT_FOUND) -> None:
        self.message = message
        self.status_code = 404
        super().__init__(self.message)


class PortfolioPublishException(Exception):
    def __init__(self, message: str = PORTFOLIO_PUBLISH_ERROR) -> None:
        self.message = message
        self.status_code = 500
        super().__init__(self.message)


class PortfolioPublicNotFoundException(Exception):
    def __init__(self, message: str = PORTFOLIO_PUBLIC_NOT_FOUND) -> None:
        self.message = message
        self.status_code = 404
        super().__init__(self.message)


class PortfolioUnpublishException(Exception):
    def __init__(self, message: str = "Failed to unpublish portfolio.") -> None:
        self.message = message
        self.status_code = 500
        super().__init__(self.message)
