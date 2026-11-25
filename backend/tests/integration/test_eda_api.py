"""Integration tests for EDA API endpoints."""
import pytest
from fastapi.testclient import TestClient
import pandas as pd


@pytest.fixture
def session_with_data(client: TestClient, sample_csv_bytes) -> str:
    """Helper to upload CSV and return active session ID."""
    resp = client.post(
        "/api/v1/dataset/upload",
        files={"file": ("customer_data.csv", sample_csv_bytes, "text/csv")}
    )
    assert resp.status_code == 201
    return resp.json()["session_id"]


def test_eda_overview_endpoint(client: TestClient, session_with_data: str):
    """Verify GET /api/v1/eda/overview."""
    resp = client.get(f"/api/v1/eda/overview?session_id={session_with_data}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_rows"] == 5
    assert data["total_columns"] == 5
    assert data["numerical_columns_count"] >= 3
    assert "memory_usage_formatted" in data


def test_eda_columns_endpoint_all_and_single(client: TestClient, session_with_data: str):
    """Verify GET /api/v1/eda/columns for all columns and single column."""
    # All columns
    all_resp = client.get(f"/api/v1/eda/columns?session_id={session_with_data}")
    assert all_resp.status_code == 200
    all_data = all_resp.json()
    assert "age" in all_data["columns_stats"]
    assert "gender" in all_data["columns_stats"]

    # Single numerical column
    age_resp = client.get(f"/api/v1/eda/columns?session_id={session_with_data}&column_name=age")
    assert age_resp.status_code == 200
    age_data = age_resp.json()
    assert age_data["column"] == "age"
    assert "mean" in age_data["stats"]
    assert "std" in age_data["stats"]

    # Single categorical column
    gender_resp = client.get(f"/api/v1/eda/columns?session_id={session_with_data}&column_name=gender")
    assert gender_resp.status_code == 200
    gender_data = gender_resp.json()
    assert gender_data["stats"]["mode"] in ["Female", "Male"]


def test_eda_columns_invalid_column(client: TestClient, session_with_data: str):
    """Verify 400 validation error on invalid column name."""
    resp = client.get(f"/api/v1/eda/columns?session_id={session_with_data}&column_name=non_existent")
    assert resp.status_code == 400
    assert "does not exist" in resp.json()["error"]["message"]


def test_eda_quality_endpoint(client: TestClient, session_with_data: str):
    """Verify GET /api/v1/eda/quality."""
    resp = client.get(f"/api/v1/eda/quality?session_id={session_with_data}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_rows"] == 5
    assert "columns_with_missing_values" in data
    assert "constant_columns" in data


def test_eda_correlations_endpoint(client: TestClient, session_with_data: str):
    """Verify GET /api/v1/eda/correlations with Pearson and Spearman."""
    pearson_resp = client.get(f"/api/v1/eda/correlations?session_id={session_with_data}&method=pearson")
    assert pearson_resp.status_code == 200
    p_data = pearson_resp.json()
    assert p_data["method"] == "pearson"
    assert len(p_data["columns"]) >= 2
    assert len(p_data["matrix"]) == len(p_data["columns"])

    spearman_resp = client.get(f"/api/v1/eda/correlations?session_id={session_with_data}&method=spearman")
    assert spearman_resp.status_code == 200
    s_data = spearman_resp.json()
    assert s_data["method"] == "spearman"


def test_eda_visualization_endpoint(client: TestClient, session_with_data: str):
    """Verify GET /api/v1/eda/visualizations/{column_name}."""
    resp = client.get(f"/api/v1/eda/visualizations/income?session_id={session_with_data}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["column"] == "income"
    assert data["box_min"] is not None
    assert data["box_median"] is not None
    assert len(data["histogram_bins"]) > 0


def test_eda_target_endpoint_unsupervised_vs_supervised(client: TestClient, session_with_data: str):
    """Verify GET /api/v1/eda/target in unsupervised and supervised states."""
    # 1. Unsupervised state
    un_resp = client.get(f"/api/v1/eda/target?session_id={session_with_data}")
    assert un_resp.status_code == 200
    assert un_resp.json()["has_target"] is False

    # 2. Configure supervised mode
    cfg_resp = client.post(
        f"/api/v1/dataset/configure?session_id={session_with_data}",
        json={"learning_mode": "supervised", "target_column": "is_fraud"}
    )
    assert cfg_resp.status_code == 200

    # 3. Supervised state
    sup_resp = client.get(f"/api/v1/eda/target?session_id={session_with_data}")
    assert sup_resp.status_code == 200
    sup_data = sup_resp.json()
    assert sup_data["has_target"] is True
    assert sup_data["target"]["target_column"] == "is_fraud"
    assert sup_data["target"]["is_classification"] is True


def test_raw_dataset_preservation_after_eda(client: TestClient, session_with_data: str):
    """Verify that calling EDA endpoints does not mutate the raw dataset."""
    from app.storage.session_manager import SessionManager
    df_before = SessionManager.get_raw_dataset(session_with_data)

    client.get(f"/api/v1/eda/overview?session_id={session_with_data}")
    client.get(f"/api/v1/eda/quality?session_id={session_with_data}")
    client.get(f"/api/v1/eda/correlations?session_id={session_with_data}")
    client.get(f"/api/v1/eda/columns?session_id={session_with_data}")

    df_after = SessionManager.get_raw_dataset(session_with_data)
    pd.testing.assert_frame_equal(df_before, df_after)

