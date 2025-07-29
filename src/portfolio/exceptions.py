from src.portfolio.constants import PORTFOLIO_INVALID_THEME, PORTFOLIO_NOT_FOUND


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
