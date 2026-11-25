"""Application domain exceptions and HTTP error handlers."""
from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base class for all application-specific exceptions."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class SessionNotFoundError(AppException):
    """Raised when the specified session ID does not exist or has expired."""
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session '{session_id}' not found or has expired.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"session_id": session_id}
        )


class InvalidFileFormatError(AppException):
    """Raised when an unsupported file format or malformed content is uploaded."""
    def __init__(self, message: str = "Invalid file format. Supported formats: CSV, XLSX, XLS."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class FileSizeExceededError(AppException):
    """Raised when file upload exceeds maximum allowed size."""
    def __init__(self, max_size_mb: int, current_size_mb: float):
        super().__init__(
            message=f"File size ({current_size_mb:.2f} MB) exceeds maximum allowed limit of {max_size_mb} MB.",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            details={"max_size_mb": max_size_mb, "current_size_mb": round(current_size_mb, 2)}
        )


class DataParsingError(AppException):
    """Raised when dataset content cannot be parsed into a tabular structure."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=f"Failed to parse dataset: {message}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details or {}
        )


class ValidationError(AppException):
    """Raised when input parameters fail business validation."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details or {}
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Standardized handler for application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for uncaught server errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred while processing the request.",
                "details": {"error": str(exc)}
            }
        }
    )

