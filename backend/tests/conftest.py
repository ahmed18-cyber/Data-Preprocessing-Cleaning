"""Pytest configuration and shared fixtures."""
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import pandas as pd

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Set testing environment variables before importing app
os.environ["ENVIRONMENT"] = "testing"
os.environ["MAX_UPLOAD_SIZE_MB"] = "50"

from app.main import app
from app.core.config import settings
from app.storage.session_manager import SessionManager


@pytest.fixture(scope="session")
def client() -> TestClient:
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_test_storage():
    """Ensure session storage is clean before and after tests."""
    yield
    # Cleanup sessions directory
    storage_path = settings.storage_path
    if storage_path.exists():
        for item in storage_path.iterdir():
            if item.is_dir() and item.name != ".gitkeep":
                try:
                    shutil.rmtree(item)
                except Exception:
                    pass


@pytest.fixture
def sample_csv_bytes() -> bytes:
    """Generate in-memory sample CSV data."""
    df = pd.DataFrame({
        "customer_id": [101, 102, 103, 104, 105],
        "age": [25, 42, 37, 58, 29],
        "income": [50000.0, 85000.5, 62000.0, 120000.0, 48000.0],
        "gender": ["Female", "Male", "Female", "Male", "Female"],
        "is_fraud": [0, 0, 1, 0, 0]
    })
    return df.to_csv(index=False).encode("utf-8")


@pytest.fixture
def sample_semicolon_csv_bytes() -> bytes:
    """Generate in-memory semicolon-delimited CSV data."""
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "metric_a": [10.5, 20.3, 30.1],
        "metric_b": ["alpha", "beta", "gamma"]
    })
    return df.to_csv(index=False, sep=";").encode("utf-8")


@pytest.fixture
def sample_xlsx_bytes() -> bytes:
    """Generate in-memory multi-sheet XLSX workbook."""
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df1 = pd.DataFrame({"col_a": [1, 2, 3], "col_b": ["x", "y", "z"]})
        df2 = pd.DataFrame({"metric": [100, 200], "score": [0.95, 0.88]})
        df1.to_excel(writer, sheet_name="Transactions", index=False)
        df2.to_excel(writer, sheet_name="Summary", index=False)
    return out.getvalue()
