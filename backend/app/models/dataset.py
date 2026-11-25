"""Pydantic models and schemas for dataset ingestion and metadata."""
from typing import Any, Literal
from pydantic import BaseModel, Field


class ColumnInfo(BaseModel):
    """Metadata describing a single dataset column."""
    name: str
    original_dtype: str
    inferred_type: Literal["numeric", "categorical", "datetime", "boolean", "text"]
    non_null_count: int
    null_count: int
    null_percentage: float = Field(..., ge=0.0, le=100.0)
    unique_count: int
    sample_values: list[Any] = Field(default_factory=list)


class DatasetMetadata(BaseModel):
    """Metadata describing the active dataset within a session."""
    session_id: str
    filename: str
    file_type: Literal["csv", "xlsx", "xls"]
    file_size_bytes: int
    row_count: int
    column_count: int
    sheet_names: list[str] | None = None
    active_sheet: str | None = None
    delimiter: str | None = None
    learning_mode: Literal["supervised", "unsupervised"] = "unsupervised"
    target_column: str | None = None
    created_at: str
    last_accessed: str


class DatasetUploadResponse(BaseModel):
    """Payload returned upon successful dataset upload."""
    success: bool = True
    session_id: str
    metadata: DatasetMetadata
    columns: list[ColumnInfo]
    preview: list[dict[str, Any]]


class ConfigureDatasetRequest(BaseModel):
    """Request payload to set supervised/unsupervised mode and target."""
    learning_mode: Literal["supervised", "unsupervised"]
    target_column: str | None = None


class ConfigureDatasetResponse(BaseModel):
    """Response payload acknowledging configuration change."""
    success: bool = True
    metadata: DatasetMetadata


class SelectSheetRequest(BaseModel):
    """Request payload to switch the active sheet in an Excel workbook."""
    sheet_name: str


class SheetListResponse(BaseModel):
    """Response payload containing available sheet names."""
    success: bool = True
    sheets: list[str]
    active_sheet: str

