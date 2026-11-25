
"""Export API endpoints.

Provides CSV downloads of processed training and testing datasets
and a detailed seven-sheet Excel preprocessing audit report.
"""

import io
import json
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from app.storage.session_manager import SessionManager


router = APIRouter(prefix="/export", tags=["Export"])


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _load_parquet(path: str) -> pd.DataFrame:
    """Load a Parquet file safely."""
    try:
        return pd.read_parquet(path)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load Parquet file: {exc}",
        )


def _stream_csv(df: pd.DataFrame):
    """Stream a DataFrame as CSV bytes."""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    for line in buffer:
        yield line.encode("utf-8")


def _json_text(value: Any) -> str:
    """Convert dictionaries, lists and other objects into Excel-safe text."""
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(value)


def _excel_value(value: Any) -> Any:
    """Convert values into types supported by openpyxl."""
    if value is None:
        return ""

    if isinstance(value, (dict, list, tuple, set)):
        return _json_text(value)

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, (pd.Timestamp,)):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    if hasattr(value, "item"):
        try:
            value = value.item()
        except (ValueError, TypeError):
            pass

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def _format_workbook(wb: Workbook) -> None:
    """Apply consistent, professional formatting to every worksheet.

    - Sheet‑specific header colors (soft palette).
    - Light‑grey thin borders around populated cells.
    - Subtle alternating row fills.
    - Gridlines visible.
    - Freeze header row, enable auto‑filter.
    - Adjust column widths, align numeric values to the right.
    """
    # Mapping of worksheet titles to soft header fill colors (hex RGB).
    header_colors = {
        "General Summary": "DCE6F1",          # soft blue
        "Dataset Overview": "D9EAD3",         # soft green
        "Data Quality": "D9EAD3",            # soft green (same as overview)
        "Recommendations": "F9E2D2",        # soft amber
        "Applied Transformations": "E4D9F5", # soft purple
        "Train-Test Split": "DCE6F1",        # soft blue (reuse)
        "Execution Details": "F9D9D0",      # soft coral
    }

    # Styles used across all sheets.
    from openpyxl.styles import Border, Side
    thin_side = Side(style="thin", color="CCCCCC")
    thin_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    alternating_fill = PatternFill(fill_type="solid", fgColor="F2F2F2")  # light grey

    for ws in wb.worksheets:
        # Freeze first data row and keep gridlines visible.
        ws.freeze_panes = "A2"
        ws.sheet_view.showGridLines = True

        # Auto‑filter if there is at least one row of data.
        if ws.max_row >= 1:
            ws.auto_filter.ref = ws.dimensions

        # Determine header fill based on sheet title.
        header_fill = PatternFill(fill_type="solid", fgColor=header_colors.get(ws.title, "DCE6F1"))
        header_font = Font(bold=True, color="000000", size=11)

        # Apply header style.
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        ws.row_dimensions[1].height = 30

        # Apply column widths and alignments.
        for column_cells in ws.columns:
            column_letter = get_column_letter(column_cells[0].column)
            max_length = 0
            for cell in column_cells:
                # Apply thin border to all cells with content.
                if cell.value is not None:
                    cell.border = thin_border
                # Align numbers to the right, text to left.
                if isinstance(cell.value, (int, float)):
                    cell.alignment = Alignment(horizontal="right", vertical="top", wrap_text=True)
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = min(max(max_length + 3, 14), 55)

        # Apply alternating row fill for data rows (starting from row 2).
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row:
                if (cell.row % 2) == 0:
                    cell.fill = alternating_fill



        for column_cells in ws.columns:
            column_letter = get_column_letter(
                column_cells[0].column
            )

            max_length = 0

            for cell in column_cells:
                cell.alignment = Alignment(
                    vertical="top",
                    wrap_text=True,
                )

                if cell.value is not None:
                    max_length = max(
                        max_length,
                        len(str(cell.value)),
                    )

            ws.column_dimensions[column_letter].width = min(
                max(max_length + 3, 14),
                55,
            )


def _get_recommendation_status(
    rec: dict,
    accepted_ids: set,
) -> str:
    """Determine a recommendation's recorded decision."""
    status = str(rec.get("status", "")).lower()

    if status in ("accepted", "rejected", "modified"):
        return status

    if rec.get("id") in accepted_ids:
        return "accepted"

    return status or "pending"


# ---------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------

@router.get(
    "/data",
    summary="Download processed data CSV",
    response_description="CSV file",
)
async def download_data(
    session_id: str = Query(..., description="Active session UUID"),
    type: str = Query(
        ...,
        pattern="^(train|test)$",
        description="Dataset type to download",
    ),
) -> StreamingResponse:
    """Download processed training or testing data."""

    try:
        SessionManager.validate_session_id(session_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    if not SessionManager.session_exists(session_id):
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found",
        )

    meta = SessionManager.get_metadata(session_id)
    summary = meta.get("preprocess_summary", {})

    path_key = "train_path" if type == "train" else "test_path"
    file_path = summary.get(path_key)

    if not file_path or not Path(file_path).is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Processed {type} data not available for this session",
        )

    df = _load_parquet(file_path)

    filename = f"{type}_{session_id}.csv"

    return StreamingResponse(
        _stream_csv(df),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )


# ---------------------------------------------------------------------
# Excel audit report
# ---------------------------------------------------------------------

@router.get(
    "/report",
    summary="Download detailed preprocessing audit report",
    response_description="Seven-sheet Excel audit report",
)
async def download_report(
    session_id: str = Query(..., description="Active session UUID"),
) -> StreamingResponse:
    """Generate a detailed seven-sheet Excel audit report."""

    try:
        SessionManager.validate_session_id(session_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    if not SessionManager.session_exists(session_id):
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found",
        )

    try:
        # -------------------------------------------------------------
        # 1. Load session information
        # -------------------------------------------------------------

        meta = SessionManager.get_metadata(session_id)

        summary = meta.get("preprocess_summary", {})
        recommendations = meta.get("recommendations", [])
        accepted = meta.get("accepted_recommendations", [])

        if not isinstance(summary, dict):
            summary = {}

        if not isinstance(recommendations, list):
            recommendations = []

        if not isinstance(accepted, list):
            accepted = []

        original_filename = meta.get(
            "original_filename",
            meta.get("original_file", "Unknown"),
        )

        learning_mode = meta.get("learning_mode", "unsupervised")
        target_column = meta.get("target_column") or "None"

        # Load original dataset.
        raw_df = SessionManager.get_raw_dataset(session_id)

        # Load processed datasets if they exist.
        train_path = summary.get("train_path")
        test_path = summary.get("test_path")

        train_df = None
        test_df = None

        if train_path and Path(train_path).is_file():
            train_df = _load_parquet(train_path)

        if test_path and Path(test_path).is_file():
            test_df = _load_parquet(test_path)

        train_rows = len(train_df) if train_df is not None else 0
        test_rows = len(test_df) if test_df is not None else 0

        total_processed = train_rows + test_rows

        test_ratio = (
            test_rows / total_processed
            if total_processed > 0
            else None
        )

        accepted_ids = {
            rec.get("id")
            for rec in accepted
            if isinstance(rec, dict) and rec.get("id") is not None
        }

        # -------------------------------------------------------------
        # Create workbook
        # -------------------------------------------------------------

        wb = Workbook()

        # =============================================================
        # SHEET 1 — GENERAL SUMMARY
        # =============================================================

        ws = wb.active
        ws.title = "General Summary"

        ws.append(["Field", "Value"])

        general_information = [
            ("Report Date", pd.Timestamp.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )),
            ("Session ID", session_id),
            ("Original Filename", original_filename),
            ("Learning Mode", learning_mode),
            ("Target Column", target_column),
            ("Original Rows", len(raw_df)),
            ("Original Columns", len(raw_df.columns)),
            ("Training Rows", train_rows),
            ("Testing Rows", test_rows),
            ("Test Size Ratio", test_ratio if test_ratio is not None else "N/A"),
            ("Accepted Recommendations", len(accepted)),
            ("Total Recommendations", len(recommendations)),
            ("Execution Status", "Completed" if train_df is not None else "Not available"),
        ]

        for field, value in general_information:
            ws.append([field, _excel_value(value)])

        # =============================================================
        # SHEET 2 — DATASET OVERVIEW
        # =============================================================

        ws = wb.create_sheet("Dataset Overview")

        ws.append([
            "Column",
            "Data Type",
            "Non-Missing Values",
            "Missing Values",
            "Missing Percentage",
            "Unique Values",
            "Sample Value",
        ])

        for column in raw_df.columns:
            series = raw_df[column]

            missing_count = int(series.isna().sum())
            non_missing = int(series.notna().sum())

            missing_percentage = (
                missing_count / len(raw_df) * 100
                if len(raw_df) > 0
                else 0
            )

            unique_count = int(series.nunique(dropna=True))

            sample = series.dropna()
            sample_value = (
                str(sample.iloc[0])[:150]
                if not sample.empty
                else ""
            )

            ws.append([
                str(column),
                str(series.dtype),
                non_missing,
                missing_count,
                round(missing_percentage, 2),
                unique_count,
                sample_value,
            ])

        # =============================================================
        # SHEET 3 — DATA QUALITY
        # =============================================================

        ws = wb.create_sheet("Data Quality")

        ws.append(["Metric", "Value"])

        missing_total = int(raw_df.isna().sum().sum())
        duplicate_rows = int(raw_df.duplicated().sum())

        constant_columns = [
            str(column)
            for column in raw_df.columns
            if raw_df[column].nunique(dropna=False) <= 1
        ]

        ws.append(["Original Rows", len(raw_df)])
        ws.append(["Original Columns", len(raw_df.columns)])
        ws.append(["Total Missing Values", missing_total])
        ws.append(["Duplicate Rows", duplicate_rows])
        ws.append(["Constant Columns", _json_text(constant_columns)])

        if train_df is not None:
            ws.append([
                "Training Dataset Missing Values",
                int(train_df.isna().sum().sum()),
            ])

        if test_df is not None:
            ws.append([
                "Testing Dataset Missing Values",
                int(test_df.isna().sum().sum()),
            ])

        ws.append([])
        ws.append([
            "Numeric Column",
            "Outliers (IQR Method)",
        ])

        for column in raw_df.select_dtypes(include="number").columns:
            series = raw_df[column].dropna()

            if series.empty:
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_count = int(
                ((series < lower_bound) | (series > upper_bound)).sum()
            )

            ws.append([str(column), outlier_count])

        # =============================================================
        # SHEET 4 — RECOMMENDATIONS
        # =============================================================

        ws = wb.create_sheet("Recommendations")

        ws.append([
            "ID",
            "Category",
            "Column",
            "Issue",
            "Evidence",
            "Suggested Action",
            "Suggested Method",
            "Decision Status",
        ])

        for rec in recommendations:
            if not isinstance(rec, dict):
                continue

            status = _get_recommendation_status(
                rec,
                accepted_ids,
            )

            ws.append([
                _excel_value(rec.get("id", "")),
                _excel_value(rec.get("category", "")),
                _excel_value(rec.get("column", "")),
                _excel_value(rec.get("issue", "")),
                _json_text(rec.get("evidence", "")),
                _excel_value(
                    rec.get("suggested_action", rec.get("action", ""))
                ),
                _excel_value(rec.get("suggested_method", "")),
                status,
            ])

        # =============================================================
        # SHEET 5 — APPLIED TRANSFORMATIONS
        # =============================================================

        ws = wb.create_sheet("Applied Transformations")

        ws.append([
            "Column",
            "Category",
            "Transformation / Action",
            "Method / Details",
            "Decision",
        ])

        for rec in accepted:
            if not isinstance(rec, dict):
                continue

            ws.append([
                _excel_value(rec.get("column", "")),
                _excel_value(rec.get("category", "")),
                _excel_value(rec.get("action", "")),
                _excel_value(
                    rec.get("suggested_method", rec.get("explanation", ""))
                ),
                "Accepted",
            ])

        for column in summary.get("dropped_columns", []):
            ws.append([
                _excel_value(column),
                "Column removal",
                "Remove column",
                "Column removed during preprocessing",
                "Applied",
            ])

        # Record the pipeline transformer components.
        for transformer in summary.get("applied_transformers", []):
            ws.append([
                "",
                "Pipeline",
                _excel_value(transformer),
                "Transformer component used in preprocessing pipeline",
                "Applied",
            ])

        # =============================================================
        # SHEET 6 — TRAIN-TEST SPLIT
        # =============================================================

        ws = wb.create_sheet("Train-Test Split")

        ws.append(["Field", "Value"])

        split_information = [
            ("Learning Mode", learning_mode),
            ("Target Column", target_column),
            ("Original Dataset Rows", len(raw_df)),
            ("Training Rows", train_rows),
            ("Testing Rows", test_rows),
            (
                "Training Percentage",
                round(train_rows / total_processed * 100, 2)
                if total_processed else "N/A",
            ),
            (
                "Testing Percentage",
                round(test_ratio * 100, 2)
                if test_ratio is not None else "N/A",
            ),
            ("Random State", 42),
            ("Stratification", "Applied when target has more than one class" if learning_mode == "supervised" else "Not applicable"),
            ("Train File", Path(train_path).name if train_path else "Not available"),
            ("Test File", Path(test_path).name if test_path else "Not available"),
        ]

        for field, value in split_information:
            ws.append([field, _excel_value(value)])

        # =============================================================
        # SHEET 7 — EXECUTION DETAILS
        # =============================================================

        ws = wb.create_sheet("Execution Details")

        ws.append(["Field", "Value"])

        execution_information = [
            ("Execution Timestamp", pd.Timestamp.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )),
            ("Execution Status", "Completed" if train_df is not None else "Not available"),
            ("Session ID", session_id),
            ("Original Dataset Path", "Session storage / raw.parquet"),
            ("Training Dataset Path", train_path or "Not available"),
            ("Testing Dataset Path", test_path or "Not available"),
            ("Training Dataset Rows", train_rows),
            ("Testing Dataset Rows", test_rows),
            ("Dropped Columns", _json_text(summary.get("dropped_columns", []))),
            ("Applied Transformers", _json_text(summary.get("applied_transformers", []))),
            ("Accepted Recommendations", len(accepted)),
        ]

        for field, value in execution_information:
            ws.append([field, _excel_value(value)])

        # -------------------------------------------------------------
        # Final formatting and response
        # -------------------------------------------------------------

        _format_workbook(wb)

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        filename = f"audit_report_{session_id}.xlsx"

        return StreamingResponse(
            buffer,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition": (
                    f"attachment; filename={filename}"
                )
            },
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate audit report: {exc}",
        ) from exc
