"""Dataset ingestion, sheet switching, and configuration endpoints."""
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
import pandas as pd

from app.api.deps import validate_session_query
from app.core.exceptions import DataParsingError, ValidationError
from app.models.dataset import (
    ColumnInfo,
    ConfigureDatasetRequest,
    ConfigureDatasetResponse,
    DatasetMetadata,
    DatasetUploadResponse,
    SelectSheetRequest,
    SheetListResponse,
)
from app.services.data_loader import DataLoader
from app.storage.session_manager import SessionManager

router = APIRouter(prefix="/dataset", tags=["Dataset"])


@router.post(
    "/upload",
    response_model=DatasetUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload CSV, XLSX, or XLS dataset",
    description="Validates file size (up to 50MB) and content, creates isolated session, saves raw Parquet dataset, and returns metadata with first 50 rows preview."
)
async def upload_dataset(
    file: UploadFile = File(...),
    sheet_name: str | None = Form(None),
    delimiter: str | None = Form(None),
) -> DatasetUploadResponse:
    """Handle multipart file upload, validate format, and initialize dataset session."""
    
    print("[UPLOAD] Step 1: Starting upload", flush=True)
    filename = file.filename or "uploaded_data.csv"
    print(f"[UPLOAD] Filename: {filename}", flush=True)

    # 1. Read and validate file
    print("[UPLOAD] Step 2: Reading file stream...", flush=True)
    file_bytes = DataLoader.validate_and_read_stream(file.file, filename)
    print(f"[UPLOAD] Step 2 complete: {len(file_bytes)} bytes", flush=True)

    # 2. Parse DataFrame
    print("[UPLOAD] Step 3: Parsing dataset...", flush=True)
    df, meta_dict = DataLoader.load_file_to_dataframe(
        file_bytes=file_bytes,
        filename=filename,
        sheet_name=sheet_name,
        delimiter=delimiter
    )
    print(f"[UPLOAD] Step 3 complete: {df.shape}", flush=True)

    # 3. Create session
    print("[UPLOAD] Step 4: Creating session...", flush=True)
    session_id = SessionManager.create_session()
    print(f"[UPLOAD] Step 4 complete: {session_id}", flush=True)

    # 4. Save dataset
    print("[UPLOAD] Step 5: Saving raw dataset...", flush=True)
    SessionManager.save_raw_dataset(
        session_id=session_id,
        df=df,
        metadata_dict=meta_dict,
        original_bytes=file_bytes,
        original_filename=filename
    )
    print("[UPLOAD] Step 5 complete", flush=True)

    # 5. Extract column information
    print("[UPLOAD] Step 6: Extracting column information...", flush=True)
    columns_info = DataLoader.extract_column_info(df)
    print("[UPLOAD] Step 6 complete", flush=True)

    # 6. Generate preview
    print("[UPLOAD] Step 7: Generating preview...", flush=True)
    preview_rows = DataLoader.get_preview_records(df, max_rows=50)
    print("[UPLOAD] Step 7 complete", flush=True)

    # 7. Retrieve metadata
    print("[UPLOAD] Step 8: Retrieving metadata...", flush=True)
    full_meta = SessionManager.get_metadata(session_id)
    print("[UPLOAD] Step 8 complete", flush=True)

    print("[UPLOAD] Step 9: Building response...", flush=True)
    result = DatasetUploadResponse(
        success=True,
        session_id=session_id,
        metadata=DatasetMetadata(**full_meta),
        columns=columns_info,
        preview=preview_rows
    )
    print("[UPLOAD] SUCCESS: Response ready", flush=True)

    return result



@router.get(
    "/sheets",
    response_model=SheetListResponse,
    summary="List Excel sheets",
    description="Retrieve available sheet names for the currently uploaded Excel workbook."
)
async def list_sheets(session_id: str = Depends(validate_session_query)) -> SheetListResponse:
    """Return available sheet names for an Excel dataset."""
    meta = SessionManager.get_metadata(session_id)
    if meta.get("file_type") not in ["xlsx", "xls"]:
        raise ValidationError("Sheet selection is only available for Excel files.")

    orig_path = SessionManager.get_original_file_path(session_id)
    if not orig_path:
        raise DataParsingError("Original Excel workbook is not available.")

    with open(orig_path, "rb") as f:
        content = f.read()
    sheets = DataLoader.get_excel_sheets(content, meta["filename"])
    active_sheet = meta.get("active_sheet") or (sheets[0] if sheets else "")

    return SheetListResponse(
        success=True,
        sheets=sheets,
        active_sheet=active_sheet
    )


@router.post(
    "/select-sheet",
    response_model=DatasetUploadResponse,
    summary="Select active sheet",
    description="Switch active sheet for Excel workbook, reloading the dataset."
)
async def select_sheet(
    payload: SelectSheetRequest,
    session_id: str = Depends(validate_session_query),
) -> DatasetUploadResponse:
    """Switch active sheet in Excel file and update raw dataset."""
    meta = SessionManager.get_metadata(session_id)
    if meta.get("file_type") not in ["xlsx", "xls"]:
        raise ValidationError("Sheet selection is only available for Excel files.")

    orig_path = SessionManager.get_original_file_path(session_id)
    if not orig_path:
        raise DataParsingError("Original Excel file not found.")

    with open(orig_path, "rb") as f:
        file_bytes = f.read()

    sheets = DataLoader.get_excel_sheets(file_bytes, meta["filename"])
    if payload.sheet_name not in sheets:
        raise ValidationError(f"Sheet '{payload.sheet_name}' not found. Available sheets: {', '.join(sheets)}")

    df, updated_meta = DataLoader.load_file_to_dataframe(
        file_bytes=file_bytes,
        filename=meta["filename"],
        sheet_name=payload.sheet_name
    )

    meta.update(updated_meta)
    SessionManager.save_raw_dataset(
        session_id=session_id,
        df=df,
        metadata_dict=meta,
        original_bytes=file_bytes,
        original_filename=meta["filename"]
    )

    columns_info = DataLoader.extract_column_info(df)
    preview_rows = DataLoader.get_preview_records(df, max_rows=50)

    return DatasetUploadResponse(
        success=True,
        session_id=session_id,
        metadata=DatasetMetadata(**meta),
        columns=columns_info,
        preview=preview_rows
    )


@router.post(
    "/configure",
    response_model=ConfigureDatasetResponse,
    summary="Configure learning mode and target column",
    description="Sets Supervised or Unsupervised mode. Validates target column existence if Supervised."
)
async def configure_dataset(
    payload: ConfigureDatasetRequest,
    session_id: str = Depends(validate_session_query),
) -> ConfigureDatasetResponse:
    """Configure learning mode and target column."""
    df = SessionManager.get_raw_dataset(session_id)
    
    if payload.learning_mode == "supervised":
        if not payload.target_column:
            raise ValidationError("A target column must be specified when using Supervised mode.")
        if payload.target_column not in df.columns:
            raise ValidationError(
                f"Target column '{payload.target_column}' does not exist in dataset. "
                f"Available columns: {', '.join(df.columns.tolist()[:10])}..."
            )
    else:
        # In unsupervised mode, clear target column
        payload.target_column = None

    updated = SessionManager.update_metadata(
        session_id=session_id,
        updates={
            "learning_mode": payload.learning_mode,
            "target_column": payload.target_column
        }
    )

    return ConfigureDatasetResponse(
        success=True,
        metadata=DatasetMetadata(**updated)
    )


@router.get(
    "/metadata",
    response_model=DatasetMetadata,
    summary="Retrieve dataset metadata",
    description="Fetch current session metadata."
)
async def get_metadata(session_id: str = Depends(validate_session_query)) -> DatasetMetadata:
    """Get metadata for the current session."""
    meta = SessionManager.get_metadata(session_id)
    return DatasetMetadata(**meta)


@router.get(
    "/preview",
    summary="Retrieve preview rows and column metadata",
    description="Fetch the first N rows (up to 50) and column type information."
)
async def get_preview(
    session_id: str = Depends(validate_session_query),
    limit: int = Query(50, ge=1, le=100)
) -> dict:
    """Return dataset preview records and column info."""
    df = SessionManager.get_raw_dataset(session_id)
    columns_info = DataLoader.extract_column_info(df)
    preview_rows = DataLoader.get_preview_records(df, max_rows=limit)
    meta = SessionManager.get_metadata(session_id)

    return {
        "success": True,
        "metadata": meta,
        "columns": [c.model_dump() for c in columns_info],
        "preview": preview_rows
    }

