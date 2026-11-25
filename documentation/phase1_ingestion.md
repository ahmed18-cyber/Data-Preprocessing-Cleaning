# Phase 1 Documentation: Ingestion, Session Architecture & Preview

## 1. Overview

Phase 1 provides the core ingestion engine, session isolation, and dataset preview for the Data Preprocessing & Cleaning Web Application.

---

## 2. Implemented Capabilities

### A. Data Ingestion (`backend/app/services/data_loader.py`)
- **Formats Supported**: CSV, Excel 2007+ (`.xlsx`), Legacy Excel 97-2003 (`.xls`).
- **CSV Delimiter Sniffing**: Automatically identifies `,`, `;`, `\t`, or `|` delimiters using `csv.Sniffer` with fallback frequency heuristics.
- **Excel Multi-Sheet Support**: Detects all worksheets, supports dynamic sheet switching while preserving the original uploaded binary file.
- **Streaming Upload Guard**: Incrementally reads incoming file chunks (1 MB chunks). If the accumulated payload exceeds `MAX_UPLOAD_SIZE_MB` (default 50 MB), the connection is immediately aborted with HTTP 413, preventing server memory saturation.
- **Duplicate Column Sanitization**: Automatically renames duplicate columns (`col`, `col_1`, `col_2`) without data loss.
- **Semantic Type Inference**: Automatically categorizes columns into:
  - `numeric`: Integers, floats (excluding binary flags).
  - `boolean`: True/false, 0/1 binary flags.
  - `categorical`: Low-cardinality discrete values.
  - `datetime`: ISO and standard calendar dates.
  - `text`: Free-form high-cardinality strings.
- **Null & Cardinality Profiling**: Computes non-null count, null count, null percentage, and unique values per feature.

### B. Session Isolation & Parquet Storage (`backend/app/storage/session_manager.py`)
- **UUIDv4 Session Identification**: Validates identifiers with standard UUIDv4 format, rejecting path traversal attempts.
- **Directory Isolation**: Every session maintains its own directory at `backend/storage_data/sessions/{session_id}/`.
- **Immutable Raw Storage**: Parsed DataFrames are stored as `raw.parquet` via PyArrow with Snappy compression, preserving exact datatypes and optimizing I/O.
- **Session Janitor (Lifespan Task)**: Automatically purges sessions inactive for more than 2 hours every 30 minutes.

### C. Learning Paradigm & Leakage Guard (`backend/app/api/v1/endpoints/dataset.py`)
- **Unsupervised Mode**: For clustering, dimensionality reduction, or outlier detection.
- **Supervised Mode**: Requires specifying a target column. The backend validates target column existence and isolates it from subsequent feature transformations to prevent holdout data leakage.

---

## 3. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/dataset/upload` | Multipart file upload (CSV/XLSX/XLS). Creates session, saves Parquet, returns preview. |
| `GET` | `/api/v1/dataset/sheets` | Lists available Excel worksheets for active session. |
| `POST` | `/api/v1/dataset/select-sheet` | Switches active Excel sheet and reloads dataset. |
| `POST` | `/api/v1/dataset/configure` | Sets Supervised/Unsupervised mode and validates target variable. |
| `GET` | `/api/v1/dataset/preview` | Retrieves first N rows and column metadata. |
| `GET` | `/api/v1/dataset/metadata` | Retrieves current session configuration and shape metadata. |
| `GET` | `/health` | Server health check and configuration report. |

---

## 4. How to Run

### Backend (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Swagger API Documentation: `http://localhost:8000/docs`

### Frontend (React + Vite)
```bash
cd frontend
npm run dev
```
Application URL: `http://localhost:5173`

### Run Backend Test Suite
```bash
python -m pytest backend/tests -v
```

### Build Frontend for Production
```bash
cd frontend
npm run build
```

