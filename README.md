# Data Preprocessing & Cleaning Web Application

A web-based application for exploring, analyzing, and preprocessing tabular datasets before Machine Learning workflows. It combines an interactive React frontend with a FastAPI backend to help users understand data quality, review preprocessing recommendations, and export processed datasets.

## Overview

The application provides a guided workflow:

1. Upload a CSV or Excel dataset.
2. Configure the dataset and select a supervised or unsupervised learning mode.
3. Explore dataset statistics, data quality, correlations, and visualizations.
4. Review preprocessing recommendations.
5. Apply preprocessing operations.
6. Export the processed dataset and a report.

## Features

### Dataset ingestion
- CSV, XLSX, and XLS file support.
- CSV delimiter detection.
- Excel worksheet selection.
- Dataset preview and metadata profiling.
- Column-name sanitization.
- Configurable upload-size limit.

### Exploratory Data Analysis
- Dataset overview and column statistics.
- Data-type and column profiling.
- Missing-value and duplicate analysis.
- Data-quality exploration.
- Correlation analysis.
- Data visualizations and target analysis.

### Preprocessing recommendations
- Automated, rule-based preprocessing recommendations.
- Review and decision support for suggested operations.
- Recommendations informed by dataset characteristics.

### Preprocessing and export
- Supervised and unsupervised dataset configuration.
- Preprocessing execution through the API.
- Processed dataset export.
- Report export.

### Session management
- Session-based dataset storage.
- Parquet storage for uploaded datasets.
- Session isolation.
- Automatic cleanup of expired sessions.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, TypeScript, Vite |
| UI and visualization | Tailwind CSS, Plotly.js, Lucide React |
| Frontend state and API | Zustand, Axios |
| Backend | Python, FastAPI, Pydantic |
| Data processing | Pandas, NumPy, SciPy, Scikit-learn |
| Storage | Parquet, PyArrow |
| Testing | Pytest, HTTPX |

## Architecture

The application follows a frontend–backend architecture.

- **Frontend:** Provides the interactive interface for dataset upload, exploration, recommendations, preprocessing, and export.
- **Backend:** Exposes REST API endpoints and handles dataset ingestion, profiling, recommendations, preprocessing, and export.
- **Processing layer:** Uses Python data-science libraries to analyze and transform tabular data.
- **Session storage:** Stores datasets and session-related information in isolated storage directories.

## Getting Started

### Prerequisites

Install the following tools:

- Python 3.11 or later
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/data-preprocessing-cleaning.git
cd Data-Preprocessing-Cleaning
```

Replace `YOUR_GITHUB_USERNAME` with your GitHub username.

### 2. Set up the backend

Open a terminal in the project root and run:

```powershell
cd backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env
```

Start the backend:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at:

- API: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

### 3. Set up the frontend

Open a second terminal in the project root:

```powershell
cd frontend

npm install
npm run dev
```

Open the frontend at:

`http://localhost:5173`

Keep both development servers running while using the application.

## API Reference

All application API routes use the `/api/v1` prefix.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/dataset/upload` | Upload a dataset |
| GET | `/api/v1/dataset/sheets` | Retrieve available Excel worksheets |
| POST | `/api/v1/dataset/select-sheet` | Select an Excel worksheet |
| POST | `/api/v1/dataset/configure` | Configure dataset and learning mode |
| GET | `/api/v1/dataset/metadata` | Retrieve dataset metadata |
| GET | `/api/v1/dataset/preview` | Preview dataset rows |
| GET | `/api/v1/eda/overview` | Retrieve EDA overview |
| GET | `/api/v1/eda/columns` | Retrieve column information |
| GET | `/api/v1/eda/quality` | Retrieve data-quality information |
| GET | `/api/v1/eda/correlations` | Retrieve correlation analysis |
| GET | `/api/v1/eda/visualizations/{column_name}` | Retrieve column visualizations |
| GET | `/api/v1/eda/target` | Retrieve target analysis |
| GET | `/api/v1/recommendations/` | Retrieve preprocessing recommendations |
| POST | `/api/v1/recommendations/decision` | Submit a recommendation decision |
| POST | `/api/v1/preprocessing/execute` | Execute preprocessing |
| GET | `/api/v1/preprocessing/summary` | Retrieve preprocessing summary |
| GET | `/api/v1/export/data` | Export processed data |
| GET | `/api/v1/export/report` | Export a processing report |
| GET | `/health` | Check backend health |

For request parameters, schemas, and interactive endpoint testing, use the Swagger documentation at `/docs`.

## Demo Datasets

The repository includes sample datasets for development and demonstration:

- `data/banking_fraud.csv`
- `data/generic_validation.csv`

These datasets are intended for demonstrating data ingestion, exploration, and preprocessing workflows.

## Running Tests

From the project root, activate the backend virtual environment if it is not already active, then run:

```powershell
cd backend
python -m pytest tests -v
```

## Production Build

To create a production frontend build:

```powershell
cd frontend
npm install
npm run build
```

The generated production files are placed in `frontend/dist/`.

## Project Structure

```text
Data-Preprocessing-Cleaning/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       └── router.py
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── storage/
│   │   └── main.py
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── stores/
│   │   ├── types/
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── data/
│   ├── banking_fraud.csv
│   ├── generic_validation.csv
│   └── README.md
│
├── documentation/
├── .gitignore
└── README.md
```

## Configuration

Backend configuration is provided through environment variables. Start with `backend/.env.example` and adjust values in your local `backend/.env` when necessary.

Common settings include:

- `ENVIRONMENT`: application environment.
- `DEBUG`: debug mode.
- `HOST` and `PORT`: backend host and port.
- `CORS_ORIGINS`: allowed frontend origins.
- `MAX_UPLOAD_SIZE_MB`: maximum upload size.
- `SESSION_EXPIRY_HOURS`: session expiration period.
- `SESSION_CLEANUP_INTERVAL_MINUTES`: session cleanup frequency.
- `STORAGE_DIR`: session storage directory.

Do not commit `.env` files or private datasets.

## Documentation

Additional project documentation, including architectural and implementation references, is available in the `documentation/` directory.

## License

A license has not yet been specified for this repository.