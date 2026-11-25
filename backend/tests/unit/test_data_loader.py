"""Unit tests for DataLoader service."""
import io
import pytest
import pandas as pd
from app.core.exceptions import DataParsingError, FileSizeExceededError, InvalidFileFormatError
from app.services.data_loader import DataLoader


def test_validate_and_read_stream_valid_csv(sample_csv_bytes):
    """Verify stream reading of valid CSV."""
    stream = io.BytesIO(sample_csv_bytes)
    result = DataLoader.validate_and_read_stream(stream, "test.csv")
    assert len(result) == len(sample_csv_bytes)


def test_validate_and_read_stream_empty_file():
    """Verify empty files (0 bytes) raise DataParsingError."""
    stream = io.BytesIO(b"")
    with pytest.raises(DataParsingError, match="empty"):
        DataLoader.validate_and_read_stream(stream, "empty.csv")


def test_validate_and_read_stream_invalid_extension():
    """Verify unsupported extensions are rejected."""
    stream = io.BytesIO(b"dummy,content\n1,2")
    with pytest.raises(InvalidFileFormatError):
        DataLoader.validate_and_read_stream(stream, "malicious.exe")


def test_validate_and_read_stream_size_limit():
    """Verify files exceeding max bytes are aborted immediately."""
    large_payload = b"A" * 1024 * 1024 * 3  # 3 MB
    stream = io.BytesIO(large_payload)
    # Enforce limit of 1 MB
    with pytest.raises(FileSizeExceededError):
        DataLoader.validate_and_read_stream(stream, "data.csv", max_bytes=1024 * 1024)


def test_detect_csv_delimiter():
    """Verify delimiter autodetection for comma, semicolon, tab, and pipe."""
    assert DataLoader.detect_csv_delimiter(b"a,b,c\n1,2,3") == ","
    assert DataLoader.detect_csv_delimiter(b"a;b;c\n1;2;3") == ";"
    assert DataLoader.detect_csv_delimiter(b"a\tb\tc\n1\t2\t3") == "\t"
    assert DataLoader.detect_csv_delimiter(b"a|b|c\n1|2|3") == "|"


def test_load_csv_dataframe(sample_csv_bytes):
    """Verify loading standard CSV into DataFrame."""
    df, meta = DataLoader.load_file_to_dataframe(sample_csv_bytes, "fraud.csv")
    assert len(df) == 5
    assert len(df.columns) == 5
    assert meta["row_count"] == 5
    assert meta["column_count"] == 5
    assert meta["delimiter"] == ","


def test_load_semicolon_csv(sample_semicolon_csv_bytes):
    """Verify auto-detection and parsing of semicolon CSV."""
    df, meta = DataLoader.load_file_to_dataframe(sample_semicolon_csv_bytes, "data.csv")
    assert len(df) == 3
    assert len(df.columns) == 3
    assert meta["delimiter"] == ";"


def test_load_xlsx_dataframe(sample_xlsx_bytes):
    """Verify multi-sheet XLSX workbook loading."""
    df, meta = DataLoader.load_file_to_dataframe(sample_xlsx_bytes, "workbook.xlsx", sheet_name="Transactions")
    assert len(df) == 3
    assert "col_a" in df.columns
    assert meta["active_sheet"] == "Transactions"
    assert "Summary" in meta["sheet_names"]


def test_column_sanitization_duplicate_names():
    """Verify duplicate column names are sanitized without data loss."""
    raw_csv = b"age,income,age\n25,50000,26\n30,60000,31"
    df, meta = DataLoader.load_file_to_dataframe(raw_csv, "duplicates.csv")
    assert list(df.columns) == ["age", "income", "age_1"]
    assert len(df) == 2


def test_extract_column_info():
    """Verify column metadata extraction and dtype inference."""
    df = pd.DataFrame({
        "num_col": [1.5, 2.7, None, 4.0],
        "cat_col": ["low", "high", "low", "high"],
        "bool_col": [True, False, True, True],
        "id_col": [1, 2, 3, 4]
    })
    infos = DataLoader.extract_column_info(df)
    info_map = {c.name: c for c in infos}

    assert info_map["num_col"].inferred_type == "numeric"
    assert info_map["num_col"].null_count == 1
    assert info_map["cat_col"].inferred_type == "categorical"
    assert info_map["bool_col"].inferred_type == "boolean"

