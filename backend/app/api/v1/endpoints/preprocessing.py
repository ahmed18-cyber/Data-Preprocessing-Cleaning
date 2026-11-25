'''Preprocessing API endpoints.
Implements execution of the preprocessing pipeline and retrieval of the summary.
''' 

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Dict

from app.api.deps import validate_session_query
from app.core.exceptions import ValidationError
from app.services.preprocessing_engine import PreprocessingEngine
from app.storage.session_manager import SessionManager

router = APIRouter(prefix="/preprocessing", tags=["Preprocessing"])


class ExecuteRequest(BaseModel):
    session_id: str = Field(..., description="Active session UUID")
    test_size: float = Field(0.2, gt=0.0, lt=1.0, description="Proportion of data for test set (supervised mode)")


@router.post(
    "/execute",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Execute preprocessing pipeline",
)
async def execute_preprocessing(payload: ExecuteRequest) -> Dict[str, Any]:
    """Run the preprocessing engine for a session.

    The endpoint validates the session, ensures that accepted recommendations exist,
    and forwards the request to :class:`PreprocessingEngine`.
    """
    # Validate session existence
    session_id = payload.session_id
    try:
        SessionManager.validate_session_id(session_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    if not SessionManager.session_exists(session_id):
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    meta = SessionManager.get_metadata(session_id)
    learning_mode = meta.get("learning_mode", "unsupervised")

    # Test size is only relevant for supervised mode; enforce presence if needed
    if learning_mode == "supervised":
        if payload.test_size is None:
            raise HTTPException(status_code=400, detail="test_size required for supervised mode")
    else:
        # ignore test_size for unsupervised – engine will treat it as None
        payload.test_size = 0.0

    # Ensure there are accepted recommendations; otherwise preprocessing would be a no‑op
    if not meta.get("accepted_recommendations"):
        raise HTTPException(status_code=400, detail="No accepted recommendations found for session")

    try:
        summary = PreprocessingEngine.run(session_id, test_size=payload.test_size)
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Preprocessing failed: {exc}")

    return summary


@router.get(
    "/summary",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieve preprocessing summary",
)
async def get_preprocessing_summary(session_id: str = Depends(validate_session_query)) -> Dict[str, Any]:
    """Return the stored preprocessing summary for a session.

    If the preprocessing step has not yet run, an empty dict is returned.
    """
    meta = SessionManager.get_metadata(session_id)
    return meta.get("preprocess_summary", {})
