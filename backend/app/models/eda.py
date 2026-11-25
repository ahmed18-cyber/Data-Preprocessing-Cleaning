"""Pydantic schemas and models for Exploratory Data Analysis (EDA)."""
from typing import Any, Literal
from pydantic import BaseModel, Field


class DatasetOverview(BaseModel):
    """Global summary metrics of the dataset."""
    total_rows: int
    total_columns: int
    numerical_columns_count: int
    categorical_columns_count: int
    datetime_columns_count: int
    boolean_columns_count: int
    text_columns_count: int
    total_missing_cells: int
    missing_cells_percentage: float = Field(..., ge=0.0, le=100.0)
    total_duplicate_rows: int
    duplicate_rows_percentage: float = Field(..., ge=0.0, le=100.0)
    memory_usage_bytes: int
    memory_usage_formatted: str


class NumericalColumnStats(BaseModel):
    """Descriptive statistics for numerical features."""
    name: str
    dtype: str
    count: int
    missing_count: int
    missing_percentage: float
    unique_count: int
    mean: float | None = None
    median: float | None = None
    std: float | None = None
    min: float | None = None
    max: float | None = None
    q1: float | None = None
    q3: float | None = None
    iqr: float | None = None
    skewness: float | None = None
    is_constant: bool = False


class CategoricalValueFrequency(BaseModel):
    """Category value with occurrence count and ratio."""
    value: str
    count: int
    percentage: float


class CategoricalColumnStats(BaseModel):
    """Descriptive statistics for categorical features."""
    name: str
    dtype: str
    count: int
    missing_count: int
    missing_percentage: float
    unique_count: int
    mode: str | None = None
    mode_frequency: int | None = None
    mode_percentage: float | None = None
    top_categories: list[CategoricalValueFrequency] = Field(default_factory=list)
    is_constant: bool = False
    is_high_cardinality: bool = False


class DatetimeColumnStats(BaseModel):
    """Descriptive statistics for datetime features."""
    name: str
    dtype: str
    count: int
    missing_count: int
    missing_percentage: float
    unique_count: int
    min_date: str | None = None
    max_date: str | None = None


class ColumnQualityIssue(BaseModel):
    """Descriptive issue identified on a column."""
    column: str
    issue_type: Literal["constant_column", "high_missingness", "high_cardinality", "all_null"]
    description: str
    severity: Literal["low", "medium", "high"]
    metric_value: float | str | None = None


class MissingFeatureInfo(BaseModel):
    """Per-feature missingness info."""
    column: str
    missing_count: int
    missing_percentage: float


class QualityOverview(BaseModel):
    """Dataset quality diagnostics."""
    total_rows: int
    total_columns: int
    duplicate_rows: int
    duplicate_percentage: float
    columns_with_missing_values: list[MissingFeatureInfo] = Field(default_factory=list)
    constant_columns: list[str] = Field(default_factory=list)
    high_cardinality_columns: list[str] = Field(default_factory=list)
    all_null_columns: list[str] = Field(default_factory=list)
    quality_issues: list[ColumnQualityIssue] = Field(default_factory=list)


class CorrelationMatrix(BaseModel):
    """Correlation matrix results for numerical columns."""
    method: Literal["pearson", "spearman"]
    columns: list[str]
    matrix: list[list[float | None]]  # 2D grid of values


class ColumnVisualizationData(BaseModel):
    """Pre-computed or sampled data points for Plotly visualizations."""
    column: str
    inferred_type: str
    # Histogram / Distribution
    histogram_bins: list[float] | None = None
    histogram_counts: list[int] | None = None
    sample_values: list[float | int | str] | None = None
    # Box plot
    box_min: float | None = None
    box_q1: float | None = None
    box_median: float | None = None
    box_q3: float | None = None
    box_max: float | None = None
    box_outliers: list[float] | None = None
    # Categorical bars
    categories: list[str] | None = None
    category_counts: list[int] | None = None


class TargetAnalysis(BaseModel):
    """Supervised target feature distribution and properties."""
    target_column: str
    inferred_type: Literal["numeric", "categorical", "boolean"]
    is_classification: bool
    summary_stats: dict[str, Any]
    distribution: list[dict[str, Any]]

