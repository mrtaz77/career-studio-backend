from src.portfolio.constants import PORTFOLIO_INVALID_THEME


class PortfolioInvalidThemeException(Exception):
    def __init__(self, message: str = PORTFOLIO_INVALID_THEME) -> None:
        self.message = message
        self.status_code = 400
        super().__init__(self.message)
