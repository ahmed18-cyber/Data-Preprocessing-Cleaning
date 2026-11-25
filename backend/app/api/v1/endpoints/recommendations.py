"""Recommendation API endpoints.

Provides two routes:
* **GET /recommendations?session_id=...** – generate (once) and retrieve recommendations.
* **POST /recommendations/decision** – accept/reject/modify a recommendation and store executable
  versions under the session metadata ``accepted_recommendations``.
"""

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import validate_session_query
from app.core.exceptions import ValidationError
from app.services.recommendation_engine import RecommendationEngine
from app.storage.session_manager import SessionManager

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

# ---------------------------------------------------------------------------
# Pydantic models for request/response payloads
# ---------------------------------------------------------------------------
from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    session_id: str = Field(..., description="Active session UUID")
    recommendation_id: str = Field(..., description="ID of the recommendation to act on")
    decision: Literal["accept", "reject", "modify"] = Field(..., description="User decision")
    modified_action: Optional[str] = Field(None, description="New action when modifying")
    modified_method: Optional[str] = Field(None, description="New method when modifying (e.g., scaling method)")


# ---------------------------------------------------------------------------
# Helper validation utilities – mirror what ``PreprocessingEngine._build_transformers``
# expects.
# ---------------------------------------------------------------------------
_ALLOWED = {
    "class_imbalance": {"action": ["apply_smote"]},
    "constant_columns": {"action": ["remove"]},    "missing_values": {"action": ["impute"]},
    "numerical_outliers": {"action": ["clip"]},
    "skewed_numeric": {"action": ["transform"], "method": ["log"]},
    "datetime_extraction": {"action": ["extract"]},
    "scaling": {"action": ["scale"], "method": ["standard", "minmax", "robust"]},
    "categorical_encoding": {"action": ["encode"], "method": ["onehot", "ordinal"]},
}


def _validate_category_action(cat: str, action: str, method: Optional[str] = None) -> None:
    rules = _ALLOWED.get(cat)
    if not rules:
        raise ValidationError(f"Unsupported recommendation category '{cat}'.")
    if action not in rules.get("action", []):
        raise ValidationError(f"Action '{action}' not allowed for category '{cat}'.")
    if "method" in rules:
        if method is None:
            raise ValidationError(f"Method must be supplied for category '{cat}'.")
        if method not in rules["method"]:
            raise ValidationError(f"Method '{method}' not allowed for category '{cat}'.")
    else:
        # categories without a method must not provide one
        if method is not None:
            raise ValidationError(f"Category '{cat}' does not accept a method argument.")


def _executable_copy(rec: dict) -> dict:
    """Return a shallow copy containing only fields required by the preprocessing engine.

    The engine looks for ``category``, ``column``, ``action``, optional ``suggested_method``
    and optional ``dtype`` (for missing values).  Extra fields are ignored, but we keep the
    copy minimal to avoid storing large evidence objects.
    """
    exec_rec: dict = {
        "category": rec["category"],
        "action": rec["action"],
    }
    # Include column only if the recommendation specifies one (e.g., class_imbalance has none)
    if "column" in rec:
        exec_rec["column"] = rec["column"]
    if rec.get("suggested_method"):
        exec_rec["suggested_method"] = rec["suggested_method"]
    if rec.get("dtype"):
        exec_rec["dtype"] = rec["dtype"]
    return exec_rec


# ---------------------------------------------------------------------------
# GET endpoint – generate or retrieve stored recommendations
# ---------------------------------------------------------------------------
@router.get("/", response_model=list[dict])
async def get_recommendations(session_id: str = Depends(validate_session_query)) -> list[dict]:
    # Ensure the session exists – ``validate_session_query`` already does that.
    meta = SessionManager.get_metadata(session_id)
    # If recommendations are already present, return them directly.
    if "recommendations" in meta:
        return meta["recommendations"]

    # Otherwise generate fresh recommendations from the raw dataset.
    recs = RecommendationEngine.generate(session_id)
    # Persist them under the metadata key.
    SessionManager.update_metadata(session_id, {"recommendations": recs})
    return recs


# ---------------------------------------------------------------------------
# POST endpoint – handle user decision on a recommendation
# ---------------------------------------------------------------------------
@router.post("/decision", status_code=status.HTTP_200_OK)
async def post_decision(payload: DecisionRequest) -> dict:
    # Validate session existence
    session_id = payload.session_id
    try:
        SessionManager.validate_session_id(session_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    if not SessionManager.session_exists(session_id):
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    meta = SessionManager.get_metadata(session_id)
    recs: list[dict] = meta.get("recommendations", [])
    # Locate the recommendation by ID
    rec = next((r for r in recs if r.get("id") == payload.recommendation_id), None)
    if rec is None:
        raise HTTPException(status_code=404, detail="Recommendation ID not found")

    # Prepare accepted list container
    accepted: list[dict] = meta.get("accepted_recommendations", [])

    # -------------------------------------------------------------------
    # Decision handling
    # -------------------------------------------------------------------
    if payload.decision == "accept":
        # Validate action/method are still consistent
        _validate_category_action(rec["category"], rec["action"], rec.get("suggested_method"))
        # Mark status
        rec["status"] = "accepted"
        # Add executable version if not already present (prevent duplicates)
        exec_rec = _executable_copy(rec)
        if not any(r.get("category") == exec_rec["category"] and r.get("column") == exec_rec["column"] for r in accepted):
            accepted.append(exec_rec)

    elif payload.decision == "reject":
        rec["status"] = "rejected"
        # Remove from accepted list if present
        accepted = [r for r in accepted if not (r.get("category") == rec["category"] and r.get("column") == rec["column"])]

    elif payload.decision == "modify":
        new_action = payload.modified_action or rec["action"]
        new_method = payload.modified_method or rec.get("suggested_method")
        
        _validate_category_action(
            rec["category"],
            new_action,
            new_method
        )
            
        rec["action"] = new_action
            
        if new_method:
            rec["suggested_method"] = new_method
                
        rec["status"] = "accepted"
        # Remove any previous entry for the same column/category
        accepted = [r for r in accepted if not (r.get("category") == rec["category"] and r.get("column") == rec["column"])]
        accepted.append(exec_rec)

    else:
        raise HTTPException(status_code=400, detail="Invalid decision value")

    # Persist updated metadata (both recommendations list and accepted list)
    updates = {
        "recommendations": recs,
        "accepted_recommendations": accepted,
    }
    SessionManager.update_metadata(session_id, updates)

    return {"detail": f"Recommendation {payload.decision}ed successfully"}

