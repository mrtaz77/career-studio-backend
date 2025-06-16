class CertificateUploadException(Exception):
    def __init__(self, message: str = "Failed to upload certificate file.") -> None:
        self.message = message
        self.status_code = 500
        super().__init__(self.message)


class CertificateValidationException(Exception):
    def __init__(self, message: str = "Invalid certification data.") -> None:
        self.message = message
        self.status_code = 400
        super().__init__(self.message)


class CertificateNotFoundException(Exception):
    def __init__(self, message: str = "Certification not found.") -> None:
        self.message = message
        self.status_code = 404
        super().__init__(self.message)
