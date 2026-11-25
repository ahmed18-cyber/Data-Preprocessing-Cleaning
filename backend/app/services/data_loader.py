"""Data ingestion service supporting CSV, XLSX, and XLS with validation."""
import csv
import io
from pathlib import Path
from typing import Any, BinaryIO
import numpy as np
import pandas as pd
from openpyxl import load_workbook
import xlrd

from app.core.config import settings
from app.core.exceptions import (
    DataParsingError,
    FileSizeExceededError,
    InvalidFileFormatError,
)
from app.models.dataset import ColumnInfo

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
CHUNK_SIZE = 1024 * 1024  # 1 MB chunk for streaming read


class DataLoader:
    """Handles file validation, delimiter detection, multi-sheet Excel reading, and typing."""

    @staticmethod
    def validate_and_read_stream(
        stream: BinaryIO,
        filename: str,
        max_bytes: int | None = None
    ) -> bytes:
        """Streamingly read uploaded file bytes while enforcing maximum size limits.
        
        Prevents memory exhaustion by terminating read early if limit is exceeded.
        """
        if not filename:
            raise InvalidFileFormatError("Filename cannot be empty.")
            
        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise InvalidFileFormatError(
                f"Unsupported file format '{ext}'. Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )

        limit = max_bytes or settings.max_upload_size_bytes
        buffer = bytearray()
        total_read = 0

        while True:
            chunk = stream.read(CHUNK_SIZE)
            if not chunk:
                break
            total_read += len(chunk)
            if total_read > limit:
                current_mb = total_read / (1024 * 1024)
                max_mb = limit / (1024 * 1024)
                raise FileSizeExceededError(max_size_mb=int(max_mb), current_size_mb=current_mb)
            buffer.extend(chunk)

        if len(buffer) == 0:
            raise DataParsingError("The uploaded file is empty (0 bytes).")

        return bytes(buffer)

    @staticmethod
    def detect_csv_delimiter(sample_bytes: bytes) -> str:
        """Detect the CSV delimiter using Python's csv.Sniffer with robust heuristic fallback."""
        try:
            # Decode a small sample (first 8KB)
            sample_text = sample_bytes[:8192].decode("utf-8", errors="replace")
            # If sniffer succeeds
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample_text, delimiters=[",", ";", "\t", "|"])
            if dialect.delimiter in [",", ";", "\t", "|"]:
                return dialect.delimiter
        except Exception:
            pass

        # Fallback heuristic: count delimiter frequency in first few non-empty lines
        lines = sample_bytes[:8192].decode("utf-8", errors="replace").splitlines()
        if lines:
            header = lines[0]
            counts = {
                ",": header.count(","),
                ";": header.count(";"),
                "\t": header.count("\t"),
                "|": header.count("|")
            }
            best_delim = max(counts, key=counts.get)
            if counts[best_delim] > 0:
                return best_delim

        return ","  # Default fallback

    @classmethod
    def get_excel_sheets(cls, file_bytes: bytes, filename: str) -> list[str]:
        """Inspect and return sheet names from an Excel file (.xlsx or .xls)."""
        ext = Path(filename).suffix.lower()
        try:
            if ext == ".xlsx":
                wb = load_workbook(io.BytesIO(file_bytes), read_only=True, keep_links=False)
                sheets = wb.sheetnames
                wb.close()
                return sheets
            elif ext == ".xls":
                wb = xlrd.open_workbook(file_contents=file_bytes, on_demand=True)
                sheets = wb.sheet_names()
                return sheets
            else:
                return []
        except Exception as exc:
            raise DataParsingError(f"Failed to read Excel workbook sheets: {str(exc)}")

    @classmethod
    def load_file_to_dataframe(
        cls,
        file_bytes: bytes,
        filename: str,
        sheet_name: str | None = None,
        delimiter: str | None = None
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
        """Load uploaded file bytes into a clean Pandas DataFrame with extraction metadata."""
        ext = Path(filename).suffix.lower()
        metadata: dict[str, Any] = {
            "filename": filename,
            "file_type": ext.lstrip("."),
            "file_size_bytes": len(file_bytes),
        }

        try:
            if ext == ".csv":
                chosen_delim = delimiter or cls.detect_csv_delimiter(file_bytes)
                metadata["delimiter"] = chosen_delim
                # Try reading with detected delimiter
                try:
                    df = pd.read_csv(
                        io.BytesIO(file_bytes),
                        sep=chosen_delim,
                        encoding="utf-8",
                        on_bad_lines="skip"
                    )
                except UnicodeDecodeError:
                    df = pd.read_csv(
                        io.BytesIO(file_bytes),
                        sep=chosen_delim,
                        encoding="latin1",
                        on_bad_lines="skip"
                    )

            elif ext == ".xlsx":
                sheets = cls.get_excel_sheets(file_bytes, filename)
                metadata["sheet_names"] = sheets
                active_sheet = sheet_name or (sheets[0] if sheets else None)
                metadata["active_sheet"] = active_sheet
                df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=active_sheet, engine="openpyxl")

            elif ext == ".xls":
                sheets = cls.get_excel_sheets(file_bytes, filename)
                metadata["sheet_names"] = sheets
                active_sheet = sheet_name or (sheets[0] if sheets else None)
                metadata["active_sheet"] = active_sheet
                df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=active_sheet, engine="xlrd")

            else:
                raise InvalidFileFormatError(f"Unsupported format: {ext}")

        except (InvalidFileFormatError, FileSizeExceededError, DataParsingError):
            raise
        except Exception as exc:
            raise DataParsingError(f"Unable to read file content into tabular format: {str(exc)}")

        if df.empty:
            raise DataParsingError("The dataset contains zero rows or columns after parsing.")

        # Ensure unique column names (handle duplicate columns)
        df.columns = cls._sanitize_column_names(df.columns)

        metadata["row_count"] = int(len(df))
        metadata["column_count"] = int(len(df.columns))

        return df, metadata

    @staticmethod
    def _sanitize_column_names(columns: Any) -> list[str]:
        """Sanitize column headers and ensure unique strings."""
        import re
        seen: dict[str, int] = {}
        sanitized: list[str] = []

        for col in columns:
            name = str(col).strip()
            # Normalize pandas automatic suffix (e.g. 'age.1' -> 'age')
            cleaned_base = re.sub(r"\.\d+$", "", name)
            if not cleaned_base or cleaned_base == "nan" or cleaned_base.startswith("Unnamed:"):
                cleaned_base = "col"
            if cleaned_base in seen:
                seen[cleaned_base] += 1
                sanitized.append(f"{cleaned_base}_{seen[cleaned_base]}")
            else:
                seen[cleaned_base] = 0
                sanitized.append(cleaned_base)

        return sanitized

    @classmethod
    def extract_column_info(cls, df: pd.DataFrame) -> list[ColumnInfo]:
        """Extract detailed type inference, null stats, and unique counts per column."""
        columns_info: list[ColumnInfo] = []
        total_rows = len(df)

        for col_name in df.columns:
            series = df[col_name]
            null_count = int(series.isna().sum())
            non_null_count = total_rows - null_count
            null_pct = round((null_count / total_rows * 100.0) if total_rows > 0 else 0.0, 2)
            unique_count = int(series.nunique(dropna=True))

            # Infer logical data type
            inferred_type = cls._infer_dtype(series)

            # Generate sample values safe for JSON serialization
            non_null_samples = series.dropna().head(5).tolist()
            sample_values = [cls._make_json_safe(v) for v in non_null_samples]

            columns_info.append(
                ColumnInfo(
                    name=str(col_name),
                    original_dtype=str(series.dtype),
                    inferred_type=inferred_type,
                    non_null_count=non_null_count,
                    null_count=null_count,
                    null_percentage=null_pct,
                    unique_count=unique_count,
                    sample_values=sample_values,
                )
            )

        return columns_info

    @staticmethod
    def _infer_dtype(series: pd.Series) -> str:
        """Infer semantic data type for machine learning."""
        if pd.api.types.is_bool_dtype(series):
            return "boolean"
        if pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        if pd.api.types.is_numeric_dtype(series):
            # Check if binary (0 and 1 only)
            non_null = series.dropna()
            if len(non_null) > 0 and set(non_null.unique()).issubset({0, 1, 0.0, 1.0}):
                return "boolean"
            return "numeric"
        
        # Non-numeric series: test for datetime parsing
        non_null_sample = series.dropna().astype(str).head(50)
        if len(non_null_sample) > 0:
            try:
                # If majority can be parsed as dates
                parsed = pd.to_datetime(non_null_sample, errors="coerce")
                if parsed.notna().sum() / len(non_null_sample) > 0.8:
                    return "datetime"
            except Exception:
                pass

        # Check unique ratio for categorical vs free text
        unique_cnt = series.nunique(dropna=True)
        if unique_cnt <= 20 or (len(series) > 0 and unique_cnt / len(series) < 0.2):
            return "categorical"
        
        return "text"

    @classmethod
    def get_preview_records(cls, df: pd.DataFrame, max_rows: int = 50) -> list[dict[str, Any]]:
        """Return the first `max_rows` formatted as a JSON-serializable list of row dictionaries."""
        preview_df = df.head(max_rows)
        records = []
        for _, row in preview_df.iterrows():
            record = {}
            for col, val in row.items():
                record[str(col)] = cls._make_json_safe(val)
            records.append(record)
        return records

    @staticmethod
    def _make_json_safe(val: Any) -> Any:
        """Convert numpy/pandas types, NaN, Inf, and timestamps to clean JSON values."""
        if pd.isna(val) or val is None:
            return None
        if isinstance(val, (np.floating, float)):
            if np.isnan(val) or np.isinf(val):
                return None
            return float(val)
        if isinstance(val, (np.integer, int)):
            return int(val)
        if isinstance(val, (np.bool_, bool)):
            return bool(val)
        if isinstance(val, (pd.Timestamp, np.datetime64)):
            return str(val)
        return str(val)
