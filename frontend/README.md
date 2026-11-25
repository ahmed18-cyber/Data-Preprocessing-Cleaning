# Frontend — Data Preprocessing & Cleaning

The frontend of the Data Preprocessing & Cleaning Web Application is a React-based interface for uploading datasets, exploring data quality, reviewing preprocessing recommendations, and exporting processed data.

## Technology Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Zustand
- Axios
- Plotly.js
- Lucide React

## Development Setup

From the `frontend` directory:

```bash
npm install
npm run dev
```

The development server is available at:

`http://localhost:5173`

## Production Build

```bash
npm run build
```

The production build is generated in the `dist/` directory.

## Backend Connection

The frontend communicates with the FastAPI backend through the API client in `src/api/`.

Start the backend separately before using the complete application.

Backend API documentation:

`http://127.0.0.1:8000/docs`

## Project Structure

```text
src/
├── api/           # Backend API clients
├── components/    # Reusable UI components
│   ├── common/
│   ├── dashboard/
│   ├── eda/
│   ├── export/
│   ├── ingestion/
│   ├── layout/
│   ├── preprocessing/
│   └── recommendations/
├── stores/        # Application state management
├── types/         # TypeScript definitions
├── App.tsx
└── main.tsx
```