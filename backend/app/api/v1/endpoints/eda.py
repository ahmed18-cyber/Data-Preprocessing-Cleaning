"""FastAPI endpoints for Exploratory Data Analysis (EDA)."""
from typing import Any, Literal
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import validate_session_query
from app.core.exceptions import ValidationError
from app.models.eda import (
    ColumnVisualizationData,
    CorrelationMatrix,
    DatasetOverview,
    QualityOverview,
    TargetAnalysis,
)
from app.services.data_loader import DataLoader
from app.services.eda_engine import EDAEngine
from app.storage.session_manager import SessionManager

router = APIRouter(prefix="/eda", tags=["Exploratory Data Analysis"])


@router.get(
    "/overview",
    response_model=DatasetOverview,
    summary="Get global dataset overview",
    description="Returns total row count, column breakdown by type, missing cell counts, and memory usage."
)
async def get_dataset_overview(
    session_id: str = Depends(validate_session_query)
) -> DatasetOverview:
    """Compute and return dataset-level metrics."""
    df = SessionManager.get_raw_dataset(session_id)
    cols_info = DataLoader.extract_column_info(df)
    return EDAEngine.compute_overview(df, cols_info)


@router.get(
    "/columns",
    summary="Get descriptive statistics for features",
    description="Returns detailed univariate metrics (mean, std, median, skewness for numeric; mode, value counts for categorical)."
)
async def get_column_stats(
    session_id: str = Depends(validate_session_query),
    column_name: str | None = Query(None, description="Optional column name to filter")
) -> dict[str, Any]:
    """Return descriptive profiling for a specific column or all columns."""
    df = SessionManager.get_raw_dataset(session_id)
    cols_info = DataLoader.extract_column_info(df)
    cols_dict = {c.name: c for c in cols_info}

    if column_name:
        if column_name not in df.columns:
            raise ValidationError(f"Column '{column_name}' does not exist in dataset.")
        col_info = cols_dict[column_name]
        if col_info.inferred_type in ["numeric", "boolean"]:
            stats = EDAEngine.compute_numerical_stats(df[column_name], column_name)
        elif col_info.inferred_type == "datetime":
            stats = EDAEngine.compute_datetime_stats(df[column_name], column_name)
        else:
            stats = EDAEngine.compute_categorical_stats(df[column_name], column_name)
        return {"column": column_name, "stats": stats.model_dump()}

    # All columns profiling
    results: dict[str, Any] = {}
    for col in cols_info:
        if col.inferred_type in ["numeric", "boolean"]:
            results[col.name] = EDAEngine.compute_numerical_stats(df[col.name], col.name).model_dump()
        elif col.inferred_type == "datetime":
            results[col.name] = EDAEngine.compute_datetime_stats(df[col.name], col.name).model_dump()
        else:
            results[col.name] = EDAEngine.compute_categorical_stats(df[col.name], col.name).model_dump()

    return {"columns_stats": results}


@router.get(
    "/quality",
    response_model=QualityOverview,
    summary="Get dataset quality diagnostics",
    description="Identifies missingness distributions, duplicate rows, constant columns, and high-cardinality features."
)
async def get_data_quality(
    session_id: str = Depends(validate_session_query)
) -> QualityOverview:
    """Compute and return quality diagnostics."""
    df = SessionManager.get_raw_dataset(session_id)
    cols_info = DataLoader.extract_column_info(df)
    return EDAEngine.compute_quality_overview(df, cols_info)


@router.get(
    "/correlations",
    response_model=CorrelationMatrix,
    summary="Compute correlation matrix",
    description="Returns pairwise Pearson or Spearman correlation values between non-constant numerical columns."
)
async def get_correlations(
    session_id: str = Depends(validate_session_query),
    method: Literal["pearson", "spearman"] = Query("pearson", description="Correlation method: pearson or spearman")
) -> CorrelationMatrix:
    """Calculate correlation matrix for numeric features."""
    df = SessionManager.get_raw_dataset(session_id)
    cols_info = DataLoader.extract_column_info(df)
    return EDAEngine.compute_correlations(df, cols_info, method=method)


@router.get(
    "/visualizations/{column_name}",
    response_model=ColumnVisualizationData,
    summary="Get column visualization data",
    description="Generates histogram bins, box plot bounds, or frequency categories for interactive Plotly charts."
)
async def get_column_visualization(
    column_name: str,
    session_id: str = Depends(validate_session_query)
) -> ColumnVisualizationData:
    """Retrieve pre-computed visualization coordinates and samples."""
    df = SessionManager.get_raw_dataset(session_id)
    if column_name not in df.columns:
        raise ValidationError(f"Column '{column_name}' does not exist in dataset.")
    
    cols_info = DataLoader.extract_column_info(df)
    col_info = next((c for c in cols_info if c.name == column_name), None)
    inferred_type = col_info.inferred_type if col_info else "numeric"

    return EDAEngine.compute_visualization_data(df, column_name, inferred_type)


@router.get(
    "/target",
    summary="Get target variable analysis",
    description="Returns distribution and summary metrics for the target variable when in Supervised mode."
)
async def get_target_analysis(
    session_id: str = Depends(validate_session_query)
) -> dict[str, Any]:
    """Analyze target variable distribution and problem formulation."""
    meta = SessionManager.get_metadata(session_id)
    learning_mode = meta.get("learning_mode", "unsupervised")
    target_column = meta.get("target_column")

    if learning_mode != "supervised" or not target_column:
        return {
            "has_target": False,
            "message": "Dataset is currently in Unsupervised mode or no target variable has been set."
        }

    df = SessionManager.get_raw_dataset(session_id)
    if target_column not in df.columns:
        raise ValidationError(f"Target column '{target_column}' is missing from dataset.")

    cols_info = DataLoader.extract_column_info(df)
    col_info = next((c for c in cols_info if c.name == target_column), None)
    inferred_type = col_info.inferred_type if col_info else "categorical"

    target_data = EDAEngine.compute_target_analysis(df, target_column, inferred_type)
    return {
        "has_target": True,
        "target": target_data.model_dump()
    }

