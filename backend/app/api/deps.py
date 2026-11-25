"""FastAPI route dependencies for session validation."""
from fastapi import Header, Query
from app.core.exceptions import SessionNotFoundError, ValidationError
from app.storage.session_manager import SessionManager


def validate_session(session_id: str = Header(..., alias="X-Session-ID")) -> str:
    """Validate that the session ID passed via X-Session-ID header exists."""
    clean_id = SessionManager.validate_session_id(session_id)
    if not SessionManager.session_exists(clean_id):
        raise SessionNotFoundError(clean_id)
    SessionManager.touch_session(clean_id)
    return clean_id


def validate_session_query(session_id: str = Query(..., description="Active session UUID")) -> str:
    """Validate that the session ID passed via query parameter exists."""
    clean_id = SessionManager.validate_session_id(session_id)
    if not SessionManager.session_exists(clean_id):
        raise SessionNotFoundError(clean_id)
    SessionManager.touch_session(clean_id)
    return clean_id

