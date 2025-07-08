from contextlib import asynccontextmanager
from datetime import date
from io import BytesIO
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient
from starlette.datastructures import UploadFile
from test_util import api_prefix, get_firebase_token

from src.app import create_app
from src.certificate.constants import (
    CERTIFICATION_ADDITION_SUCCESS,
    CERTIFICATION_FILE_MISSING,
    CERTIFICATION_METADATA_MISSING,
)
from src.certificate.exceptions import (
    CertificateNotFoundException,
    CertificateUploadException,
    CertificateValidationException,
)
from src.certificate.schemas import CertificateOut
from src.certificate.service import (
    delete_user_certificate,
    generate_signed_url,
    get_certificate_or_404,
    get_user_certificates,
    process_certificate_uploads,
    update_user_certificate,
    upload_file_to_supabase,
    validate_file,
)


@pytest.fixture
def auth_headers():
    token = get_firebase_token()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_pdf_file():
    """Create a mock PDF file for testing."""
    content = b"%PDF-1.4 fake pdf content"
    return UploadFile(
        filename="test_certificate.pdf",
        file=BytesIO(content),
        size=len(content),
        headers={"content-type": "application/pdf"},
    )


@pytest.fixture
def sample_certificate_data():
    return {
        "title": "AWS Certified Developer",
        "issuer": "Amazon Web Services",
        "issued_date": "2024-01-15",
    }


# =============================================================================
# INTEGRATION TESTS - Testing all API endpoints
# =============================================================================


class TestCertificateIntegration:
    """Integration tests for certificate API endpoints."""

    def test_add_certificates_success(self, client, auth_headers, mock_pdf_file):
        """Test successful certificate upload with all required fields."""
        with patch(
            "src.certificate.router.process_certificate_uploads"
        ) as mock_process:
            mock_process.return_value = None

            # Prepare form data
            files = {"file_0": ("test.pdf", mock_pdf_file.file, "application/pdf")}
            data = {
                "title_0": "AWS Certified Developer",
                "issuer_0": "Amazon Web Services",
                "issued_date_0": "2024-01-15",
            }

            response = client.post(
                f"{api_prefix}/certificate/add",
                files=files,
                data=data,
                headers=auth_headers,
            )

            assert response.status_code == 201
            assert response.json()["message"] == CERTIFICATION_ADDITION_SUCCESS
            mock_process.assert_called_once()

    def test_add_certificates_multiple_files(self, client, auth_headers):
        """Test adding multiple certificates in one request."""
        with patch(
            "src.certificate.router.process_certificate_uploads"
        ) as mock_process:
            mock_process.return_value = None

            # Create mock files
            file1 = BytesIO(b"%PDF-1.4 fake pdf 1")
            file2 = BytesIO(b"%PDF-1.4 fake pdf 2")

            files = [
                ("file_0", ("cert1.pdf", file1, "application/pdf")),
                ("file_1", ("cert2.pdf", file2, "application/pdf")),
            ]
            data = {
                "title_0": "Certificate 1",
                "issuer_0": "Issuer 1",
                "issued_date_0": "2024-01-15",
                "title_1": "Certificate 2",
                "issuer_1": "Issuer 2",
                "issued_date_1": "2024-02-20",
            }

            response = client.post(
                f"{api_prefix}/certificate/add",
                files=files,
                data=data,
                headers=auth_headers,
            )

            assert response.status_code == 201
            assert response.json()["message"] == CERTIFICATION_ADDITION_SUCCESS

    def test_add_certificates_missing_metadata(self, client, auth_headers):
        """Test error when required metadata is missing."""
        file_content = BytesIO(b"%PDF-1.4 fake pdf")
        files = {"file_0": ("test.pdf", file_content, "application/pdf")}
        data = {
            "title_0": "AWS Certified Developer",
            # Missing issuer and issued_date
        }

        response = client.post(
            f"{api_prefix}/certificate/add",
            files=files,
            data=data,
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert CERTIFICATION_METADATA_MISSING in response.json()["detail"]

    def test_add_certificates_missing_file(self, client, auth_headers):
        """Test error when file is missing."""
        data = {
            "title_0": "AWS Certified Developer",
            "issuer_0": "Amazon Web Services",
            "issued_date_0": "2024-01-15",
            # Missing file_0
        }

        response = client.post(
            f"{api_prefix}/certificate/add", data=data, headers=auth_headers
        )

        assert response.status_code == 400
        assert CERTIFICATION_FILE_MISSING in response.json()["detail"]

    def test_add_certificates_validation_error(self, client, auth_headers):
        """Test handling of validation errors."""
        with patch(
            "src.certificate.router.process_certificate_uploads"
        ) as mock_process:
            mock_process.side_effect = CertificateValidationException(
                "Invalid date format"
            )

            file_content = BytesIO(b"%PDF-1.4 fake pdf")
            files = {"file_0": ("test.pdf", file_content, "application/pdf")}
            data = {
                "title_0": "AWS Certified Developer",
                "issuer_0": "Amazon Web Services",
                "issued_date_0": "invalid-date",
            }

            response = client.post(
                f"{api_prefix}/certificate/add",
                files=files,
                data=data,
                headers=auth_headers,
            )

            assert response.status_code == 400
            assert "Invalid date format" in response.json()["detail"]

    def test_add_certificates_upload_error(self, client, auth_headers):
        """Test handling of upload errors."""
        with patch(
            "src.certificate.router.process_certificate_uploads"
        ) as mock_process:
            mock_process.side_effect = CertificateUploadException("Upload failed")

            file_content = BytesIO(b"%PDF-1.4 fake pdf")
            files = {"file_0": ("test.pdf", file_content, "application/pdf")}
            data = {
                "title_0": "AWS Certified Developer",
                "issuer_0": "Amazon Web Services",
                "issued_date_0": "2024-01-15",
            }

            response = client.post(
                f"{api_prefix}/certificate/add",
                files=files,
                data=data,
                headers=auth_headers,
            )

            assert response.status_code == 500
            assert "Upload failed" in response.json()["detail"]

    def test_add_certificates_internal_error(self, client, auth_headers):
        """Test handling of unexpected internal errors during certificate addition."""
        with patch(
            "src.certificate.router.process_certificate_uploads"
        ) as mock_process:
            # Simulate an unexpected internal error (e.g., database connection failure)
            mock_process.side_effect = Exception("Unexpected database error")

            file_content = BytesIO(b"%PDF-1.4 fake pdf")
            files = {"file_0": ("test.pdf", file_content, "application/pdf")}
            data = {
                "title_0": "AWS Certified Developer",
                "issuer_0": "Amazon Web Services",
                "issued_date_0": "2024-01-15",
            }

            response = client.post(
                f"{api_prefix}/certificate/add",
                files=files,
                data=data,
                headers=auth_headers,
            )

            assert response.status_code == 500
            assert "Internal server error" in response.json()["detail"]

    def test_list_certificates_success(self, client, auth_headers):
        """Test successful retrieval of user certificates."""
        mock_certificates = [
            CertificateOut(
                id=1,
                title="AWS Certified Developer",
                issuer="Amazon Web Services",
                issued_date="2024-01-15",
                link="https://example.com/cert1",
            ),
            CertificateOut(
                id=2,
                title="Google Cloud Professional",
                issuer="Google Cloud",
                issued_date="2024-02-20",
                link="https://example.com/cert2",
            ),
        ]

        with patch("src.certificate.router.get_user_certificates") as mock_get:
            mock_get.return_value = mock_certificates

            response = client.get(f"{api_prefix}/certificate", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["title"] == "AWS Certified Developer"
            assert data[1]["title"] == "Google Cloud Professional"

    def test_list_certificates_empty(self, client, auth_headers):
        """Test retrieval when user has no certificates."""
        with patch("src.certificate.router.get_user_certificates") as mock_get:
            mock_get.return_value = []

            response = client.get(f"{api_prefix}/certificate", headers=auth_headers)

            assert response.status_code == 200
            assert response.json() == []

    def test_list_certificates_error(self, client, auth_headers):
        """Test error handling in list certificates."""
        with patch("src.certificate.router.get_user_certificates") as mock_get:
            mock_get.side_effect = Exception("Database error")

            response = client.get(f"{api_prefix}/certificate", headers=auth_headers)

            assert response.status_code == 500
            assert "Could not retrieve certificates" in response.json()["detail"]

    def test_update_certificate_success(self, client, auth_headers):
        """Test successful certificate update."""
        updated_cert = CertificateOut(
            id=1,
            title="Updated Certificate Title",
            issuer="Updated Issuer",
            issued_date="2024-03-01",
            link="https://example.com/updated-cert",
        )

        with patch("src.certificate.router.update_user_certificate") as mock_update:
            mock_update.return_value = updated_cert

            data = {
                "title": "Updated Certificate Title",
                "issuer": "Updated Issuer",
                "issued_date": "2024-03-01",
            }

            response = client.patch(
                f"{api_prefix}/certificate/1", data=data, headers=auth_headers
            )

            assert response.status_code == 200
            result = response.json()
            assert result["title"] == "Updated Certificate Title"
            assert result["issuer"] == "Updated Issuer"

    def test_update_certificate_with_file(self, client, auth_headers):
        """Test certificate update with new file."""
        updated_cert = CertificateOut(
            id=1,
            title="Certificate with New File",
            issuer="Issuer",
            issued_date="2024-01-15",
            link="https://example.com/new-cert-file",
        )

        with patch("src.certificate.router.update_user_certificate") as mock_update:
            mock_update.return_value = updated_cert

            file_content = BytesIO(b"%PDF-1.4 new fake pdf")
            files = {"file": ("new_cert.pdf", file_content, "application/pdf")}
            data = {"title": "Certificate with New File"}

            response = client.patch(
                f"{api_prefix}/certificate/1",
                files=files,
                data=data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            result = response.json()
            assert result["title"] == "Certificate with New File"

    def test_update_certificate_upload_error(self, client, auth_headers):
        """Test update certificate with upload error."""
        with patch("src.certificate.router.update_user_certificate") as mock_update:
            mock_update.side_effect = CertificateUploadException("Upload failed")

            data = {"title": "New Title"}

            response = client.patch(
                f"{api_prefix}/certificate/1", data=data, headers=auth_headers
            )

            assert response.status_code == 500
            assert "Upload failed" in response.json()["detail"]

    def test_update_certificate_general_error(self, client, auth_headers):
        """Test update certificate with general error."""
        with patch("src.certificate.router.update_user_certificate") as mock_update:
            mock_update.side_effect = Exception("Unexpected error")

            data = {"title": "New Title"}

            response = client.patch(
                f"{api_prefix}/certificate/1", data=data, headers=auth_headers
            )

            assert response.status_code == 500
            assert "Update failed" in response.json()["detail"]

    def test_delete_certificate_success(self, client, auth_headers):
        """Test successful certificate deletion."""
        with patch("src.certificate.router.delete_user_certificate") as mock_delete:
            mock_delete.return_value = None

            response = client.delete(
                f"{api_prefix}/certificate/1", headers=auth_headers
            )

            assert response.status_code == 200
            assert response.json()["message"] == "Certificate deleted successfully"
            mock_delete.assert_called_once_with("WNSxHvdn70XAd9D6qz70dhVNzZo2", 1)

    def test_delete_certificate_not_found(self, client, auth_headers):
        """Test delete non-existent certificate."""
        with patch("src.certificate.router.delete_user_certificate") as mock_delete:
            mock_delete.side_effect = CertificateNotFoundException(
                "Certification not found."
            )

            response = client.delete(
                f"{api_prefix}/certificate/999", headers=auth_headers
            )

            assert response.status_code == 404
            assert "Certification not found." in response.json()["detail"]

    def test_delete_certificate_general_error(self, client, auth_headers):
        """Test delete certificate with general error."""
        with patch("src.certificate.router.delete_user_certificate") as mock_delete:
            mock_delete.side_effect = Exception("Unexpected error")

            response = client.delete(
                f"{api_prefix}/certificate/1", headers=auth_headers
            )

            assert response.status_code == 500
            assert "Delete failed" in response.json()["detail"]

    def test_add_certificates_empty_request(self, client, auth_headers):
        """Test error when no certificates are provided."""
        data = {}

        response = client.post(
            f"{api_prefix}/certificate/add", data=data, headers=auth_headers
        )

        assert response.status_code == 400
        assert CERTIFICATION_METADATA_MISSING in response.json()["detail"]

    def test_add_certificates_no_auth(self, client):
        """Test add certificates without authentication."""
        data = {
            "title_0": "AWS Certified Developer",
            "issuer_0": "Amazon Web Services",
            "issued_date_0": "2024-01-15",
        }

        response = client.post(f"{api_prefix}/certificate/add", data=data)

        assert response.status_code == 401

    def test_list_certificates_no_auth(self, client):
        """Test list certificates without authentication."""
        response = client.get(f"{api_prefix}/certificate")

        assert response.status_code == 401

    def test_update_certificate_no_auth(self, client):
        """Test update certificate without authentication."""
        data = {"title": "New Title"}

        response = client.patch(f"{api_prefix}/certificate/1", data=data)

        assert response.status_code == 401

    def test_delete_certificate_no_auth(self, client):
        """Test delete certificate without authentication."""
        response = client.delete(f"{api_prefix}/certificate/1")

        assert response.status_code == 401

    def test_add_certificates_partial_metadata(self, client, auth_headers):
        """Test error when some required fields are missing."""
        file_content = BytesIO(b"%PDF-1.4 fake pdf")
        files = {"file_0": ("test.pdf", file_content, "application/pdf")}
        data = {
            "title_0": "AWS Certified Developer",
            "issuer_0": "Amazon Web Services",
            # Missing issued_date_0
        }

        response = client.post(
            f"{api_prefix}/certificate/add",
            files=files,
            data=data,
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert CERTIFICATION_METADATA_MISSING in response.json()["detail"]

    def test_update_certificate_not_found_error(self, client, auth_headers):
        """Test update with certificate not found error."""
        with patch("src.certificate.router.update_user_certificate") as mock_update:
            mock_update.side_effect = CertificateNotFoundException(
                "Certification not found."
            )

            data = {"title": "New Title"}

            response = client.patch(
                f"{api_prefix}/certificate/1", data=data, headers=auth_headers
            )

            assert response.status_code == 500
            assert "Update failed" in response.json()["detail"]

    def test_validate_and_format_date_success(self):
        """Test successful date validation and formatting."""
        from src.certificate.service import validate_and_format_date

        result = validate_and_format_date("2024-01-15")
        assert result == "2024-01-15T00:00:00.000Z"

    def test_validate_and_format_date_today(self):
        """Test date validation with today's date."""
        from datetime import date

        from src.certificate.service import validate_and_format_date

        today = date.today().isoformat()
        result = validate_and_format_date(today)
        assert result == f"{today}T00:00:00.000Z"

    def test_validate_and_format_date_future_error(self):
        """Test date validation with future date."""
        from src.certificate.service import validate_and_format_date

        with pytest.raises(CertificateUploadException) as exc_info:
            validate_and_format_date("2030-01-01")

        assert "Certificate issue date cannot be in the future" in str(exc_info.value)

    def test_validate_and_format_date_too_old_error(self):
        """Test date validation with date before 1900."""
        from src.certificate.service import validate_and_format_date

        with pytest.raises(CertificateUploadException) as exc_info:
            validate_and_format_date("1899-12-31")

        assert "Certificate issue date must be from 1900 onwards" in str(exc_info.value)

    def test_validate_and_format_date_invalid_format(self):
        """Test date validation with invalid format."""
        from src.certificate.service import validate_and_format_date

        with pytest.raises(CertificateUploadException) as exc_info:
            validate_and_format_date("invalid-date")

        assert "Invalid issued_date format. Use YYYY-MM-DD" in str(exc_info.value)

    def test_validate_and_format_date_edge_cases(self):
        """Test date validation with edge cases."""
        from src.certificate.service import validate_and_format_date

        # Test leap year
        result = validate_and_format_date("2024-02-29")
        assert result == "2024-02-29T00:00:00.000Z"

        # Test minimum valid year
        result = validate_and_format_date("1900-01-01")
        assert result == "1900-01-01T00:00:00.000Z"

    @pytest.mark.asyncio
    async def test_process_certificate_uploads_future_date_error(
        self, sample_certificate_data
    ):
        """Test certificate upload with future date."""
        mock_file = Mock()
        cert_data = {
            **sample_certificate_data,
            "issued_date": "2030-01-01",
            "file": mock_file,
        }

        with pytest.raises(CertificateUploadException) as exc_info:
            await process_certificate_uploads("test-uid", [cert_data])

        assert "Certificate issue date cannot be in the future" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_certificate_future_date_error(self):
        """Test certificate update with future date."""
        mock_cert = CertificateOut(
            id=1, title="Title", issuer="Issuer", issued_date="2024-01-15", link="path"
        )

        mock_db = Mock()
        mock_supabase = Mock()

        @asynccontextmanager
        async def mock_get_db():
            yield mock_db

        @asynccontextmanager
        async def mock_get_supabase():
            yield mock_supabase

        with patch("src.certificate.service.get_db", mock_get_db), patch(
            "src.certificate.service.get_supabase", mock_get_supabase
        ), patch("src.certificate.service.get_certificate_or_404") as mock_get_cert:

            mock_get_cert.return_value = mock_cert

            with pytest.raises(CertificateUploadException) as exc_info:
                await update_user_certificate(
                    "test-uid", 1, None, None, "2030-01-01", None
                )

            assert "Certificate issue date cannot be in the future" in str(
                exc_info.value
            )


# =============================================================================
# UNIT TESTS - Testing service functions
# =============================================================================


class TestCertificateService:
    """Unit tests for certificate service functions."""

    @pytest.mark.asyncio
    async def test_validate_file_success(self):
        """Test successful file validation."""
        filename = "certificate.pdf"
        contents = b"%PDF-1.4 content under 5MB"

        # Should not raise any exception
        validate_file(filename, contents)

    def test_validate_file_invalid_extension(self):
        """Test file validation with invalid extension."""
        filename = "certificate.docx"
        contents = b"some content"

        with pytest.raises(CertificateUploadException) as exc_info:
            validate_file(filename, contents)

        assert "Only PDF files are supported" in str(exc_info.value)

    def test_validate_file_too_large(self):
        """Test file validation with file too large."""
        filename = "certificate.pdf"
        contents = b"x" * (6 * 1024 * 1024)  # 6MB file

        with pytest.raises(CertificateUploadException) as exc_info:
            validate_file(filename, contents)

        assert "File size exceeds 5MB limit" in str(exc_info.value)

    def test_generate_signed_url_success(self):
        """Test successful signed URL generation."""
        mock_supabase = Mock()
        mock_supabase.storage.from_().create_signed_url.return_value = {
            "signedURL": "https://example.com/signed-url"
        }

        result = generate_signed_url(mock_supabase, "path/to/file", "bucket")

        assert result == "https://example.com/signed-url"
        mock_supabase.storage.from_.assert_called_with("bucket")

    def test_generate_signed_url_failure(self):
        """Test signed URL generation failure."""
        mock_supabase = Mock()
        mock_supabase.storage.from_().create_signed_url.return_value = {}

        with pytest.raises(CertificateUploadException) as exc_info:
            generate_signed_url(mock_supabase, "path/to/file", "bucket")

        assert "Failed to generate signed URL" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upload_file_to_supabase_success(self, mock_pdf_file):
        """Test successful file upload to Supabase."""
        mock_supabase = Mock()
        mock_supabase.storage.from_().upload.return_value = None

        with patch("src.certificate.service.validate_file") as mock_validate:
            mock_validate.return_value = None

            result = await upload_file_to_supabase(
                mock_supabase, "test-uid", mock_pdf_file, "test-bucket"
            )

            assert result.startswith("test-uid/")
            assert result.endswith(".pdf")
            mock_supabase.storage.from_.assert_called_with("test-bucket")

    @pytest.mark.asyncio
    async def test_upload_file_to_supabase_failure(self, mock_pdf_file):
        """Test file upload failure to Supabase."""
        mock_supabase = Mock()
        mock_supabase.storage.from_().upload.side_effect = Exception("Upload failed")

        with patch("src.certificate.service.validate_file") as mock_validate:
            mock_validate.return_value = None

            with pytest.raises(CertificateUploadException):
                await upload_file_to_supabase(
                    mock_supabase, "test-uid", mock_pdf_file, "test-bucket"
                )

    @pytest.mark.asyncio
    async def test_get_certificate_or_404_success(self):
        """Test successful certificate retrieval."""
        mock_db = Mock()
        mock_cert = Mock()
        mock_cert.id = 1
        mock_cert.user_id = "test-uid"
        mock_cert.title = "Test Certificate"
        mock_cert.issuer = "Test Issuer"
        mock_cert.issued_date = date(2024, 1, 15)
        mock_cert.link = "path/to/cert"

        mock_db.certification.find_unique = AsyncMock(return_value=mock_cert)

        result = await get_certificate_or_404(mock_db, "test-uid", 1)

        assert isinstance(result, CertificateOut)
        assert result.id == 1
        assert result.title == "Test Certificate"

    @pytest.mark.asyncio
    async def test_get_certificate_or_404_not_found(self):
        """Test certificate not found."""
        mock_db = Mock()
        mock_db.certification.find_unique = AsyncMock(return_value=None)

        with pytest.raises(CertificateNotFoundException):
            await get_certificate_or_404(mock_db, "test-uid", 999)

    @pytest.mark.asyncio
    async def test_get_certificate_or_404_wrong_user(self):
        """Test certificate belongs to different user."""
        mock_db = Mock()
        mock_cert = Mock()
        mock_cert.user_id = "other-uid"
        mock_db.certification.find_unique = AsyncMock(return_value=mock_cert)

        with pytest.raises(CertificateNotFoundException):
            await get_certificate_or_404(mock_db, "test-uid", 1)

    @pytest.mark.asyncio
    async def test_process_certificate_uploads_success(self, sample_certificate_data):
        """Test successful certificate upload processing."""
        mock_file = Mock()
        mock_file.filename = "test.pdf"

        cert_data = {**sample_certificate_data, "file": mock_file}

        mock_db = Mock()
        mock_supabase = Mock()
        mock_db.certification.create = AsyncMock()

        @asynccontextmanager
        async def mock_get_db():
            yield mock_db

        @asynccontextmanager
        async def mock_get_supabase():
            yield mock_supabase

        with patch("src.certificate.service.get_db", mock_get_db), patch(
            "src.certificate.service.get_supabase", mock_get_supabase
        ), patch("src.certificate.service.upload_file_to_supabase") as mock_upload:

            mock_upload.return_value = "test-uid/file-path.pdf"

            await process_certificate_uploads("test-uid", [cert_data])

            mock_db.certification.create.assert_called_once()
            mock_upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_certificate_uploads_invalid_date(
        self, sample_certificate_data
    ):
        """Test certificate upload with invalid date."""
        mock_file = Mock()
        cert_data = {
            **sample_certificate_data,
            "issued_date": "invalid-date",
            "file": mock_file,
        }

        with pytest.raises(CertificateUploadException) as exc_info:
            await process_certificate_uploads("test-uid", [cert_data])

        assert "Invalid issued_date" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_certificates_success(self):
        """Test successful retrieval of user certificates."""
        mock_cert1 = Mock()
        mock_cert1.id = 1
        mock_cert1.title = "Cert 1"
        mock_cert1.issuer = "Issuer 1"
        mock_cert1.issued_date = date(2024, 1, 15)
        mock_cert1.link = "path/to/cert1"

        mock_cert2 = Mock()
        mock_cert2.id = 2
        mock_cert2.title = "Cert 2"
        mock_cert2.issuer = "Issuer 2"
        mock_cert2.issued_date = date(2024, 2, 20)
        mock_cert2.link = "path/to/cert2"

        mock_db = Mock()
        mock_supabase = Mock()
        mock_db.certification.find_many = AsyncMock(
            return_value=[mock_cert1, mock_cert2]
        )

        @asynccontextmanager
        async def mock_get_db():
            yield mock_db

        @asynccontextmanager
        async def mock_get_supabase():
            yield mock_supabase

        with patch("src.certificate.service.get_db", mock_get_db), patch(
            "src.certificate.service.get_supabase", mock_get_supabase
        ), patch("src.certificate.service.generate_signed_url") as mock_generate:

            mock_generate.return_value = "https://signed-url.com"

            result = await get_user_certificates("test-uid")

            assert len(result) == 2
            assert result[0].title == "Cert 1"
            assert result[1].title == "Cert 2"

    @pytest.mark.asyncio
    async def test_update_user_certificate_success(self):
        """Test successful certificate update."""
        mock_cert = CertificateOut(
            id=1,
            title="Original Title",
            issuer="Original Issuer",
            issued_date="2024-01-15",
            link="original/path",
        )

        mock_updated_cert = Mock()
        mock_updated_cert.id = 1
        mock_updated_cert.title = "Updated Title"
        mock_updated_cert.issuer = "Updated Issuer"
        mock_updated_cert.issued_date = date(2024, 3, 1)
        mock_updated_cert.link = "updated/path"

        mock_db = Mock()
        mock_supabase = Mock()
        mock_db.certification.update = AsyncMock(return_value=mock_updated_cert)

        @asynccontextmanager
        async def mock_get_db():
            yield mock_db

        @asynccontextmanager
        async def mock_get_supabase():
            yield mock_supabase

        with patch("src.certificate.service.get_db", mock_get_db), patch(
            "src.certificate.service.get_supabase", mock_get_supabase
        ), patch(
            "src.certificate.service.get_certificate_or_404"
        ) as mock_get_cert, patch(
            "src.certificate.service.generate_signed_url"
        ) as mock_generate:

            mock_get_cert.return_value = mock_cert
            mock_generate.return_value = "https://signed-url.com"

            result = await update_user_certificate(
                "test-uid",
                1,
                title="Updated Title",
                issuer="Updated Issuer",
                issued_date="2024-03-01",
                file=None,
            )

            assert result.title == "Updated Title"
            assert result.issuer == "Updated Issuer"

    @pytest.mark.asyncio
    async def test_update_user_certificate_no_fields(self):
        """Test certificate update with no fields provided."""
        mock_cert = CertificateOut(
            id=1, title="Title", issuer="Issuer", issued_date="2024-01-15", link="path"
        )

        mock_db = Mock()
        mock_supabase = Mock()

        @asynccontextmanager
        async def mock_get_db():
            yield mock_db

        @asynccontextmanager
        async def mock_get_supabase():
            yield mock_supabase

        with patch("src.certificate.service.get_db", mock_get_db), patch(
            "src.certificate.service.get_supabase", mock_get_supabase
        ), patch("src.certificate.service.get_certificate_or_404") as mock_get_cert:

            mock_get_cert.return_value = mock_cert

            with pytest.raises(CertificateUploadException) as exc_info:
                await update_user_certificate("test-uid", 1, None, None, None, None)

            assert "No fields provided to update" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_certificate_invalid_date(self):
        """Test certificate update with invalid date format."""
        mock_cert = CertificateOut(
            id=1, title="Title", issuer="Issuer", issued_date="2024-01-15", link="path"
        )

        mock_db = Mock()
        mock_supabase = Mock()

        @asynccontextmanager
        async def mock_get_db():
            yield mock_db

        @asynccontextmanager
        async def mock_get_supabase():
            yield mock_supabase

        with patch("src.certificate.service.get_db", mock_get_db), patch(
            "src.certificate.service.get_supabase", mock_get_supabase
        ), patch("src.certificate.service.get_certificate_or_404") as mock_get_cert:

            mock_get_cert.return_value = mock_cert

            with pytest.raises(CertificateUploadException) as exc_info:
                await update_user_certificate(
                    "test-uid", 1, None, None, "invalid-date", None
                )

            assert "Invalid issued_date format" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_user_certificate_success(self):
        """Test successful certificate deletion."""
        mock_cert = CertificateOut(
            id=1,
            title="Title",
            issuer="Issuer",
            issued_date="2024-01-15",
            link="path/to/cert",
        )

        mock_db = Mock()
        mock_supabase = Mock()
        mock_db.certification.delete = AsyncMock()
        mock_supabase.storage.from_().remove.return_value = None

        @asynccontextmanager
        async def mock_get_db():
            yield mock_db

        @asynccontextmanager
        async def mock_get_supabase():
            yield mock_supabase

        with patch("src.certificate.service.get_db", mock_get_db), patch(
            "src.certificate.service.get_supabase", mock_get_supabase
        ), patch("src.certificate.service.get_certificate_or_404") as mock_get_cert:

            mock_get_cert.return_value = mock_cert

            await delete_user_certificate("test-uid", 1)

            mock_db.certification.delete.assert_called_once_with(where={"id": 1})
            mock_supabase.storage.from_.assert_called_with("certificates")

    @pytest.mark.asyncio
    async def test_update_user_certificate_with_file_replacement(self):
        """Test certificate update with file replacement."""
        mock_cert = CertificateOut(
            id=1,
            title="Title",
            issuer="Issuer",
            issued_date="2024-01-15",
            link="old/path",
        )

        mock_updated_cert = Mock()
        mock_updated_cert.id = 1
        mock_updated_cert.title = "Title"
        mock_updated_cert.issuer = "Issuer"
        mock_updated_cert.issued_date = date(2024, 1, 15)
        mock_updated_cert.link = "new/path"

        mock_file = Mock()
        mock_file.filename = "new_cert.pdf"

        mock_db = Mock()
        mock_supabase = Mock()
        mock_db.certification.update = AsyncMock(return_value=mock_updated_cert)
        mock_supabase.storage.from_().remove.return_value = None

        @asynccontextmanager
        async def mock_get_db():
            yield mock_db

        @asynccontextmanager
        async def mock_get_supabase():
            yield mock_supabase

        with patch("src.certificate.service.get_db", mock_get_db), patch(
            "src.certificate.service.get_supabase", mock_get_supabase
        ), patch(
            "src.certificate.service.get_certificate_or_404"
        ) as mock_get_cert, patch(
            "src.certificate.service.upload_file_to_supabase"
        ) as mock_upload, patch(
            "src.certificate.service.generate_signed_url"
        ) as mock_generate:

            mock_get_cert.return_value = mock_cert
            mock_upload.return_value = "new/path"
            mock_generate.return_value = "https://signed-url.com"

            result = await update_user_certificate(
                "test-uid", 1, title=None, issuer=None, issued_date=None, file=mock_file
            )

            # Should remove old file and upload new one
            mock_supabase.storage.from_().remove.assert_called_once_with(["old/path"])
            mock_upload.assert_called_once()
            assert result.link == "https://signed-url.com"

    @pytest.mark.asyncio
    async def test_validate_file_case_insensitive_extension(self):
        """Test file validation with uppercase extension."""
        filename = "certificate.PDF"
        contents = b"%PDF-1.4 content under 5MB"

        # Should not raise any exception (extension should be case-insensitive)
        validate_file(filename, contents)

    @pytest.mark.asyncio
    async def test_validate_file_no_extension(self):
        """Test file validation with no extension."""
        filename = "certificate"
        contents = b"some content"

        with pytest.raises(CertificateUploadException) as exc_info:
            validate_file(filename, contents)

        assert "Only PDF files are supported" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upload_file_to_supabase_no_filename(self):
        """Test file upload with no filename."""
        mock_file = Mock()
        mock_file.filename = None
        mock_file.read = AsyncMock(return_value=b"%PDF-1.4 content")

        mock_supabase = Mock()
        mock_supabase.storage.from_().upload.return_value = None

        with patch("src.certificate.service.validate_file") as mock_validate:
            mock_validate.return_value = None

            result = await upload_file_to_supabase(
                mock_supabase, "test-uid", mock_file, "test-bucket"
            )

            # Should still generate a path even without filename
            assert result.startswith("test-uid/")

    @pytest.mark.asyncio
    async def test_process_certificate_uploads_multiple_certs(
        self, sample_certificate_data
    ):
        """Test processing multiple certificates in one batch."""
        mock_file1 = Mock()
        mock_file1.filename = "cert1.pdf"
        mock_file2 = Mock()
        mock_file2.filename = "cert2.pdf"

        cert_data1 = {**sample_certificate_data, "file": mock_file1}
        cert_data2 = {
            "title": "Google Cloud Certified",
            "issuer": "Google Cloud",
            "issued_date": "2024-02-20",
            "file": mock_file2,
        }

        mock_db = Mock()
        mock_supabase = Mock()
        mock_db.certification.create = AsyncMock()

        @asynccontextmanager
        async def mock_get_db():
            yield mock_db

        @asynccontextmanager
        async def mock_get_supabase():
            yield mock_supabase

        with patch("src.certificate.service.get_db", mock_get_db), patch(
            "src.certificate.service.get_supabase", mock_get_supabase
        ), patch("src.certificate.service.upload_file_to_supabase") as mock_upload:

            mock_upload.side_effect = ["test-uid/cert1.pdf", "test-uid/cert2.pdf"]

            await process_certificate_uploads("test-uid", [cert_data1, cert_data2])

            # Should create two database entries
            assert mock_db.certification.create.call_count == 2
            assert mock_upload.call_count == 2

    @pytest.mark.asyncio
    async def test_get_user_certificates_empty_result(self):
        """Test get user certificates when no certificates exist."""
        mock_db = Mock()
        mock_supabase = Mock()
        mock_db.certification.find_many = AsyncMock(return_value=[])

        @asynccontextmanager
        async def mock_get_db():
            yield mock_db

        @asynccontextmanager
        async def mock_get_supabase():
            yield mock_supabase

        with patch("src.certificate.service.get_db", mock_get_db), patch(
            "src.certificate.service.get_supabase", mock_get_supabase
        ):

            result = await get_user_certificates("test-uid")

            assert result == []
            mock_db.certification.find_many.assert_called_once_with(
                where={"user_id": "test-uid"}
            )

    def test_generate_signed_url_with_custom_expiry(self):
        """Test signed URL generation with custom expiry time."""
        mock_supabase = Mock()
        mock_supabase.storage.from_().create_signed_url.return_value = {
            "signedURL": "https://example.com/signed-url-custom"
        }

        result = generate_signed_url(
            mock_supabase, "path/to/file", "bucket", expires=7200
        )

        assert result == "https://example.com/signed-url-custom"
        mock_supabase.storage.from_().create_signed_url.assert_called_with(
            "path/to/file", expires_in=7200
        )

    @pytest.mark.asyncio
    async def test_delete_user_certificate_file_removal_error(self):
        """Test certificate deletion when file removal fails but database deletion succeeds."""
        mock_cert = CertificateOut(
            id=1,
            title="Title",
            issuer="Issuer",
            issued_date="2024-01-15",
            link="path/to/cert",
        )

        mock_db = Mock()
        mock_supabase = Mock()
        mock_db.certification.delete = AsyncMock()
        mock_supabase.storage.from_().remove.side_effect = Exception(
            "File removal failed"
        )

        @asynccontextmanager
        async def mock_get_db():
            yield mock_db

        @asynccontextmanager
        async def mock_get_supabase():
            yield mock_supabase

        with patch("src.certificate.service.get_db", mock_get_db), patch(
            "src.certificate.service.get_supabase", mock_get_supabase
        ), patch("src.certificate.service.get_certificate_or_404") as mock_get_cert:

            mock_get_cert.return_value = mock_cert

            # Should still raise the file removal exception
            with pytest.raises(Exception) as exc_info:
                await delete_user_certificate("test-uid", 1)

            assert "File removal failed" in str(exc_info.value)

    def test_format_date_for_output_datetime_object(self):
        """Test date formatting with datetime object."""
        from datetime import datetime

        from src.certificate.service import format_date_for_output

        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = format_date_for_output(dt)
        assert result == "2024-01-15"

    def test_format_date_for_output_date_object(self):
        """Test date formatting with date object."""
        from datetime import date

        from src.certificate.service import format_date_for_output

        d = date(2024, 1, 15)
        result = format_date_for_output(d)
        assert result == "2024-01-15"

    def test_format_date_for_output_iso_string(self):
        """Test date formatting with ISO datetime string."""
        from src.certificate.service import format_date_for_output

        iso_string = "2024-01-15T00:00:00.000Z"
        result = format_date_for_output(iso_string)
        assert result == "2024-01-15"

    def test_format_date_for_output_date_string(self):
        """Test date formatting with plain date string."""
        from src.certificate.service import format_date_for_output

        date_string = "2024-01-15"
        result = format_date_for_output(date_string)
        assert result == "2024-01-15"

    def test_format_date_for_output_none_value(self):
        """Test date formatting with None value."""
        from src.certificate.service import format_date_for_output

        with pytest.raises(CertificateUploadException) as exc_info:
            format_date_for_output(None)

        assert "Date value cannot be None" in str(exc_info.value)

    def test_format_date_for_output_empty_string(self):
        """Test date formatting with empty string."""
        from src.certificate.service import format_date_for_output

        with pytest.raises(CertificateUploadException) as exc_info:
            format_date_for_output("")

        assert "Date value cannot be empty" in str(exc_info.value)

    def test_format_date_for_output_invalid_date_string(self):
        """Test date formatting with invalid date string."""
        from src.certificate.service import format_date_for_output

        with pytest.raises(CertificateUploadException) as exc_info:
            format_date_for_output("invalid-date-format")

        assert "Invalid date format" in str(exc_info.value)

    def test_format_date_for_output_malformed_iso_string(self):
        """Test date formatting with malformed ISO string."""
        from src.certificate.service import format_date_for_output

        with pytest.raises(CertificateUploadException) as exc_info:
            format_date_for_output("2024-13-45T00:00:00.000Z")  # Invalid month/day

        assert "Invalid date format" in str(exc_info.value)

    def test_format_date_for_output_validates_extracted_date(self):
        """Test that date formatting validates extracted date parts."""
        from src.certificate.service import format_date_for_output

        # Valid ISO string should work
        result = format_date_for_output("2024-01-15T10:30:00.000Z")
        assert result == "2024-01-15"

        # Invalid date in ISO string should fail
        with pytest.raises(CertificateUploadException):
            format_date_for_output("2024-13-32T10:30:00.000Z")

    def test_issued_date_always_returns_string(self, client, auth_headers):
        """Test that issued_date is always returned as a string in all endpoints."""
        mock_certificates = [
            CertificateOut(
                id=1,
                title="Test Certificate",
                issuer="Test Issuer",
                issued_date="2024-01-15",  # Ensure this is a string
                link="https://example.com/cert1",
            )
        ]

        with patch("src.certificate.router.get_user_certificates") as mock_get:
            mock_get.return_value = mock_certificates

            response = client.get(f"{api_prefix}/certificate", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

            # Verify issued_date is a string
            issued_date = data[0]["issued_date"]
            assert isinstance(issued_date, str)
            assert issued_date == "2024-01-15"

    def test_update_certificate_returns_string_date(self, client, auth_headers):
        """Test that update certificate returns issued_date as string."""
        updated_cert = CertificateOut(
            id=1,
            title="Updated Certificate",
            issuer="Updated Issuer",
            issued_date="2024-03-01",  # Ensure this is a string
            link="https://example.com/updated-cert",
        )

        with patch("src.certificate.router.update_user_certificate") as mock_update:
            mock_update.return_value = updated_cert

            data = {
                "title": "Updated Certificate",
                "issuer": "Updated Issuer",
                "issued_date": "2024-03-01",
            }

            response = client.patch(
                f"{api_prefix}/certificate/1", data=data, headers=auth_headers
            )

            assert response.status_code == 200
            result = response.json()

            # Verify issued_date is a string
            issued_date = result["issued_date"]
            assert isinstance(issued_date, str)
            assert issued_date == "2024-03-01"
