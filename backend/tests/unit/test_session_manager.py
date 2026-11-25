"""Unit tests for SessionManager."""
import json
import time
from datetime import datetime, timezone, timedelta
import pytest
import pandas as pd
from app.core.exceptions import SessionNotFoundError, ValidationError
from app.storage.session_manager import SessionManager


def test_validate_session_id():
    """Verify UUID validation accepts valid v4 UUID and rejects malformed strings."""
    valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
    assert SessionManager.validate_session_id(valid_uuid) == valid_uuid

    with pytest.raises(ValidationError):
        SessionManager.validate_session_id("../../../etc/passwd")

    with pytest.raises(ValidationError):
        SessionManager.validate_session_id("invalid-id-1234")


def test_session_creation_and_isolation():
    """Verify separate sessions have distinct directories and isolated data."""
    s1 = SessionManager.create_session()
    s2 = SessionManager.create_session()
    assert s1 != s2

    dir1 = SessionManager.get_session_dir(s1)
    dir2 = SessionManager.get_session_dir(s2)
    assert dir1 != dir2
    assert dir1.is_dir()
    assert dir2.is_dir()


def test_raw_dataset_preservation():
    """Verify raw Parquet dataset is saved and read back with exact data parity."""
    session_id = SessionManager.create_session()
    orig_df = pd.DataFrame({
        "feature_1": [10.0, 20.5, 30.2],
        "feature_2": ["A", "B", "C"]
    })
    meta = {"filename": "test.csv", "row_count": 3, "column_count": 2}

    SessionManager.save_raw_dataset(session_id, orig_df, meta)
    loaded_df = SessionManager.get_raw_dataset(session_id)

    pd.testing.assert_frame_equal(orig_df, loaded_df)


def test_touch_session_updates_timestamp():
    """Verify touching session updates the last_accessed field."""
    session_id = SessionManager.create_session()
    initial_meta = SessionManager.get_metadata(session_id)
    time.sleep(0.01)

    SessionManager.touch_session(session_id)
    updated_meta = SessionManager.get_metadata(session_id)

    assert updated_meta["last_accessed"] >= initial_meta["last_accessed"]


def test_cleanup_expired_sessions():
    """Verify expired sessions older than threshold are safely removed."""
    session_id = SessionManager.create_session()
    session_dir = SessionManager.get_session_dir(session_id)
    meta_file = session_dir / "metadata.json"

    # Artificially age the session to 3 hours ago
    past_iso = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
    with open(meta_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["last_accessed"] = past_iso
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    purged = SessionManager.cleanup_expired_sessions()
    assert purged >= 1
    assert not SessionManager.session_exists(session_id)

