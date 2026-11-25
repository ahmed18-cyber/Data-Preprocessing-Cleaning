"""Unit tests for EDA Engine."""
import numpy as np
import pandas as pd
import pytest

from app.models.dataset import ColumnInfo
from app.services.eda_engine import EDAEngine


@pytest.fixture
def test_df() -> pd.DataFrame:
    """Diverse DataFrame fixture for statistical checks."""
    return pd.DataFrame({
        "num_normal": [10.0, 20.0, 30.0, 40.0, 50.0],
        "num_skewed": [1.0, 1.2, 1.1, 1.3, 100.0],
        "num_constant": [7.0, 7.0, 7.0, 7.0, 7.0],
        "num_with_null": [10.0, np.nan, 30.0, np.nan, 50.0],
        "all_null": [np.nan, np.nan, np.nan, np.nan, np.nan],
        "cat_feature": ["A", "B", "A", "A", "C"],
        "cat_constant": ["Single", "Single", "Single", "Single", "Single"],
        "date_feature": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04", "2026-01-05"]
    })


@pytest.fixture
def mock_columns_info(test_df: pd.DataFrame) -> list[ColumnInfo]:
    """ColumnInfo mock matching test_df."""
    from app.services.data_loader import DataLoader
    return DataLoader.extract_column_info(test_df)


def test_compute_overview(test_df, mock_columns_info):
    """Verify global overview calculations."""
    overview = EDAEngine.compute_overview(test_df, mock_columns_info)
    assert overview.total_rows == 5
    assert overview.total_columns == 8
    assert overview.total_missing_cells == 7  # 2 in num_with_null, 5 in all_null
    assert overview.total_duplicate_rows == 0
    assert overview.numerical_columns_count >= 3
    assert "B" in overview.memory_usage_formatted or "KB" in overview.memory_usage_formatted


def test_numerical_stats_normal(test_df):
    """Verify descriptive statistics on a standard numeric column."""
    stats = EDAEngine.compute_numerical_stats(test_df["num_normal"], "num_normal")
    assert stats.count == 5
    assert stats.missing_count == 0
    assert stats.mean == 30.0
    assert stats.median == 30.0
    assert stats.min == 10.0
    assert stats.max == 50.0
    assert stats.q1 == 20.0
    assert stats.q3 == 40.0
    assert stats.iqr == 20.0
    assert stats.is_constant is False


def test_numerical_stats_constant(test_df):
    """Verify handling of zero-variance constant numeric feature."""
    stats = EDAEngine.compute_numerical_stats(test_df["num_constant"], "num_constant")
    assert stats.is_constant is True
    assert stats.unique_count == 1
    assert stats.std == 0.0


def test_numerical_stats_all_null(test_df):
    """Verify all-null column does not cause divide-by-zero or crash."""
    stats = EDAEngine.compute_numerical_stats(test_df["all_null"], "all_null")
    assert stats.count == 0
    assert stats.missing_count == 5
    assert stats.missing_percentage == 100.0
    assert stats.mean is None
    assert stats.std is None


def test_categorical_stats(test_df):
    """Verify categorical frequency analysis and mode detection."""
    stats = EDAEngine.compute_categorical_stats(test_df["cat_feature"], "cat_feature")
    assert stats.count == 5
    assert stats.unique_count == 3
    assert stats.mode == "A"
    assert stats.mode_frequency == 3
    assert stats.mode_percentage == 60.0
    assert len(stats.top_categories) == 3
    assert stats.is_constant is False


def test_datetime_stats(test_df):
    """Verify date range metrics."""
    stats = EDAEngine.compute_datetime_stats(test_df["date_feature"], "date_feature")
    assert stats.count == 5
    assert stats.unique_count == 5
    assert "2026-01-01" in str(stats.min_date)
    assert "2026-01-05" in str(stats.max_date)


def test_compute_quality_overview(test_df, mock_columns_info):
    """Verify quality issues detection: missingness, constant cols, all-null cols."""
    quality = EDAEngine.compute_quality_overview(test_df, mock_columns_info)
    assert "all_null" in quality.all_null_columns
    assert "num_constant" in quality.constant_columns
    assert "cat_constant" in quality.constant_columns
    assert any(m.column == "all_null" and m.missing_percentage == 100.0 for m in quality.columns_with_missing_values)
    assert any(issue.issue_type == "constant_column" for issue in quality.quality_issues)


def test_correlations_pearson_and_spearman(test_df, mock_columns_info):
    """Verify correlation computation safely filters constant columns."""
    pearson = EDAEngine.compute_correlations(test_df, mock_columns_info, method="pearson")
    assert pearson.method == "pearson"
    # Constant columns (num_constant) must be excluded from correlation matrix
    assert "num_constant" not in pearson.columns
    assert "all_null" not in pearson.columns
    assert "num_normal" in pearson.columns
    assert len(pearson.matrix) == len(pearson.columns)

    spearman = EDAEngine.compute_correlations(test_df, mock_columns_info, method="spearman")
    assert spearman.method == "spearman"
    assert len(spearman.columns) == len(pearson.columns)


def test_target_analysis_classification():
    """Verify target analysis for categorical classification target."""
    df = pd.DataFrame({"target": ["cat", "dog", "cat", "cat", "bird"]})
    analysis = EDAEngine.compute_target_analysis(df, "target", "categorical")
    assert analysis.is_classification is True
    assert analysis.summary_stats["unique_classes"] == 3
    assert analysis.summary_stats["majority_class"] == "cat"


def test_target_analysis_regression():
    """Verify target analysis for continuous regression target."""
    df = pd.DataFrame({"house_price": [250000.5, 310000.2, 420000.0, 180000.7, 500000.3, 390000.9]})
    analysis = EDAEngine.compute_target_analysis(df, "house_price", "numeric")
    assert analysis.is_classification is False
    assert analysis.summary_stats["mean"] is not None
    assert len(analysis.distribution) == 20  # 20 histogram bins
