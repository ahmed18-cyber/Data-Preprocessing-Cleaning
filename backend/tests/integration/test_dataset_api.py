"""Integration tests for Dataset API endpoints."""
import io
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Verify health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["max_upload_size_mb"] == 50


def test_upload_valid_csv(client: TestClient, sample_csv_bytes):
    """Verify uploading a valid CSV returns metadata, preview, and session ID."""
    response = client.post(
        "/api/v1/dataset/upload",
        files={"file": ("fraud_dataset.csv", sample_csv_bytes, "text/csv")}
    )
    assert response.status_code == 201
    data = response.json()

    assert data["success"] is True
    assert "session_id" in data
    assert data["metadata"]["row_count"] == 5
    assert data["metadata"]["column_count"] == 5
    assert len(data["columns"]) == 5
    assert len(data["preview"]) == 5


def test_upload_valid_xlsx(client: TestClient, sample_xlsx_bytes):
    """Verify uploading an XLSX file returns sheets and preview."""
    response = client.post(
        "/api/v1/dataset/upload",
        files={"file": ("transactions.xlsx", sample_xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 201
    data = response.json()

    assert data["success"] is True
    assert data["metadata"]["file_type"] == "xlsx"
    assert "Transactions" in data["metadata"]["sheet_names"]
    assert "Summary" in data["metadata"]["sheet_names"]


def test_upload_invalid_extension(client: TestClient):
    """Verify uploading an unsupported extension is rejected with 400 Bad Request."""
    response = client.post(
        "/api/v1/dataset/upload",
        files={"file": ("script.py", b"print('hello')", "text/x-python")}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "Unsupported file format" in data["error"]["message"]


def test_upload_empty_file(client: TestClient):
    """Verify uploading empty file returns 422 Unprocessable Entity."""
    response = client.post(
        "/api/v1/dataset/upload",
        files={"file": ("empty.csv", b"", "text/csv")}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert "empty" in data["error"]["message"]


def test_upload_exceeds_size_limit(client: TestClient, monkeypatch):
    """Verify that file exceeding configured size limit returns 413 Content Too Large."""
    from app.core.config import settings
    # Temporarily set max upload to 1 MB for testing
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)
    large_csv = b"a,b\n" + (b"1,2\n" * 600000)  # ~2.4 MB
    response = client.post(
        "/api/v1/dataset/upload",
        files={"file": ("large.csv", large_csv, "text/csv")}
    )
    assert response.status_code == 413
    data = response.json()
    assert data["success"] is False
    assert "exceeds maximum allowed limit" in data["error"]["message"]


def test_missing_session_id(client: TestClient):
    """Verify accessing preview with missing or nonexistent session returns 404."""
    response = client.get("/api/v1/dataset/preview?session_id=550e8400-e29b-41d4-a716-446655440000")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False


def test_configure_dataset_supervised_success(client: TestClient, sample_csv_bytes):
    """Verify configuring supervised learning mode with valid target column."""
    # 1. Upload
    up_resp = client.post(
        "/api/v1/dataset/upload",
        files={"file": ("data.csv", sample_csv_bytes, "text/csv")}
    )
    session_id = up_resp.json()["session_id"]

    # 2. Configure
    cfg_resp = client.post(
        f"/api/v1/dataset/configure?session_id={session_id}",
        json={"learning_mode": "supervised", "target_column": "is_fraud"}
    )
    assert cfg_resp.status_code == 200
    cfg_data = cfg_resp.json()
    assert cfg_data["metadata"]["learning_mode"] == "supervised"
    assert cfg_data["metadata"]["target_column"] == "is_fraud"


def test_configure_dataset_supervised_invalid_target(client: TestClient, sample_csv_bytes):
    """Verify configuring supervised mode with non-existent target raises 400."""
    up_resp = client.post(
        "/api/v1/dataset/upload",
        files={"file": ("data.csv", sample_csv_bytes, "text/csv")}
    )
    session_id = up_resp.json()["session_id"]

    cfg_resp = client.post(
        f"/api/v1/dataset/configure?session_id={session_id}",
        json={"learning_mode": "supervised", "target_column": "non_existent_col"}
    )
    assert cfg_resp.status_code == 400
    assert "does not exist" in cfg_resp.json()["error"]["message"]


def test_sheet_selection_flow(client: TestClient, sample_xlsx_bytes):
    """Verify listing sheets and switching active sheet."""
    # 1. Upload
    up_resp = client.post(
        "/api/v1/dataset/upload",
        files={"file": ("multi.xlsx", sample_xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    session_id = up_resp.json()["session_id"]

    # 2. List sheets
    sheets_resp = client.get(f"/api/v1/dataset/sheets?session_id={session_id}")
    assert sheets_resp.status_code == 200
    assert sheets_resp.json()["sheets"] == ["Transactions", "Summary"]

    # 3. Switch sheet to "Summary"
    switch_resp = client.post(
        f"/api/v1/dataset/select-sheet?session_id={session_id}",
        json={"sheet_name": "Summary"}
    )
    assert switch_resp.status_code == 200
    data = switch_resp.json()
    assert data["metadata"]["active_sheet"] == "Summary"
    assert data["metadata"]["row_count"] == 2
    assert "metric" in [c["name"] for c in data["columns"]]


def test_upload_real_banking_fraud_dataset(client: TestClient):
    """Verify uploading the generated banking_fraud.csv demo dataset."""
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[3]
    fraud_path = project_root / "data" / "banking_fraud.csv"
    assert fraud_path.is_file(), f"Demo banking_fraud.csv should exist at {fraud_path}"

    with open(fraud_path, "rb") as f:
        response = client.post(
            "/api/v1/dataset/upload",
            files={"file": ("banking_fraud.csv", f.read(), "text/csv")}
        )
    assert response.status_code == 201
    data = response.json()
    assert data["metadata"]["row_count"] == 500
    assert data["metadata"]["column_count"] == 9
    assert "is_fraud" in [c["name"] for c in data["columns"]]


def test_upload_real_generic_validation_dataset(client: TestClient):
    """Verify uploading the generated generic_validation.csv demo dataset."""
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[3]
    val_path = project_root / "data" / "generic_validation.csv"
    assert val_path.is_file(), f"Demo generic_validation.csv should exist at {val_path}"

    with open(val_path, "rb") as f:
        response = client.post(
            "/api/v1/dataset/upload",
            files={"file": ("generic_validation.csv", f.read(), "text/csv")}
        )
    assert response.status_code == 201
    data = response.json()
    assert data["metadata"]["row_count"] == 300
    assert data["metadata"]["column_count"] == 7
    # Verify missing values were properly profiled
    salary_col = next(c for c in data["columns"] if c["name"] == "monthly_salary")
    assert salary_col["null_count"] > 0
