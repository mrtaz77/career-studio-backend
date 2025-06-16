class EducationNotFoundException(Exception):
    """Raised when a requested education entry is not found or unauthorized."""

    def __init__(self) -> None:
        self.message = "Education entry not found"
        super().__init__(self.message)
        self.status_code = 404
