"""Exploratory Data Analysis (EDA) engine providing statistics, quality profiling, and correlations."""
import math
from typing import Any
import numpy as np
import pandas as pd
from scipy import stats

from app.models.dataset import ColumnInfo
from app.models.eda import (
    CategoricalColumnStats,
    CategoricalValueFrequency,
    ColumnQualityIssue,
    ColumnVisualizationData,
    CorrelationMatrix,
    DatasetOverview,
    DatetimeColumnStats,
    MissingFeatureInfo,
    NumericalColumnStats,
    QualityOverview,
    TargetAnalysis,
)


class EDAEngine:
    """Core analytical service for calculating dataset and feature-level statistics."""

    @staticmethod
    def _format_memory(bytes_val: int) -> str:
        """Format bytes to human readable string (KB, MB, GB)."""
        if bytes_val < 1024:
            return f"{bytes_val} B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val / 1024:.2f} KB"
        elif bytes_val < 1024 * 1024 * 1024:
            return f"{bytes_val / (1024 * 1024):.2f} MB"
        else:
            return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"

    @staticmethod
    def _clean_num(val: Any) -> float | None:
        """Sanitize floating point numbers, handling NaN, Inf, and non-numeric types."""
        if val is None or pd.isna(val):
            return None
        try:
            f = float(val)
            if math.isnan(f) or math.isinf(f):
                return None
            return round(f, 4)
        except (ValueError, TypeError):
            return None

    @classmethod
    def compute_overview(
        cls,
        df: pd.DataFrame,
        columns_info: list[ColumnInfo]
    ) -> DatasetOverview:
        """Calculate global dataset metrics."""
        total_rows = len(df)
        total_cols = len(df.columns)

        type_counts = {
            "numeric": 0,
            "categorical": 0,
            "datetime": 0,
            "boolean": 0,
            "text": 0
        }
        for c in columns_info:
            if c.inferred_type in type_counts:
                type_counts[c.inferred_type] += 1
            else:
                type_counts["categorical"] += 1

        total_cells = total_rows * total_cols
        total_missing_cells = int(df.isna().sum().sum())
        missing_pct = round((total_missing_cells / total_cells * 100.0) if total_cells > 0 else 0.0, 2)

        total_duplicates = int(df.duplicated().sum())
        duplicate_pct = round((total_duplicates / total_rows * 100.0) if total_rows > 0 else 0.0, 2)

        mem_bytes = int(df.memory_usage(deep=True).sum())

        return DatasetOverview(
            total_rows=total_rows,
            total_columns=total_cols,
            numerical_columns_count=type_counts["numeric"],
            categorical_columns_count=type_counts["categorical"],
            datetime_columns_count=type_counts["datetime"],
            boolean_columns_count=type_counts["boolean"],
            text_columns_count=type_counts["text"],
            total_missing_cells=total_missing_cells,
            missing_cells_percentage=missing_pct,
            total_duplicate_rows=total_duplicates,
            duplicate_rows_percentage=duplicate_pct,
            memory_usage_bytes=mem_bytes,
            memory_usage_formatted=cls._format_memory(mem_bytes)
        )

    @classmethod
    def compute_numerical_stats(cls, series: pd.Series, name: str) -> NumericalColumnStats:
        """Calculate descriptive metrics for a numeric column."""
        total = len(series)
        valid = series.dropna()
        missing_count = total - len(valid)
        missing_pct = round((missing_count / total * 100.0) if total > 0 else 0.0, 2)
        unique_cnt = int(valid.nunique())

        if len(valid) == 0:
            return NumericalColumnStats(
                name=name,
                dtype=str(series.dtype),
                count=0,
                missing_count=missing_count,
                missing_percentage=missing_pct,
                unique_count=0,
                is_constant=False
            )

        # Convert to float series for safety
        numeric_valid = pd.to_numeric(valid, errors="coerce").dropna()
        if len(numeric_valid) == 0:
            return NumericalColumnStats(
                name=name,
                dtype=str(series.dtype),
                count=0,
                missing_count=missing_count,
                missing_percentage=missing_pct,
                unique_count=0,
                is_constant=False
            )

        mean_val = cls._clean_num(numeric_valid.mean())
        median_val = cls._clean_num(numeric_valid.median())
        std_val = cls._clean_num(numeric_valid.std(ddof=1)) if len(numeric_valid) > 1 else 0.0
        min_val = cls._clean_num(numeric_valid.min())
        max_val = cls._clean_num(numeric_valid.max())

        q1 = cls._clean_num(numeric_valid.quantile(0.25))
        q3 = cls._clean_num(numeric_valid.quantile(0.75))
        iqr = cls._clean_num((q3 - q1) if (q3 is not None and q1 is not None) else None)

        # Skewness calculation
        skew_val = None
        if len(numeric_valid) >= 3 and std_val is not None and std_val > 0:
            try:
                skew_val = cls._clean_num(stats.skew(numeric_valid, bias=False))
            except Exception:
                skew_val = cls._clean_num(numeric_valid.skew())

        is_const = bool(unique_cnt <= 1 and len(valid) > 0)

        return NumericalColumnStats(
            name=name,
            dtype=str(series.dtype),
            count=len(numeric_valid),
            missing_count=missing_count,
            missing_percentage=missing_pct,
            unique_count=unique_cnt,
            mean=mean_val,
            median=median_val,
            std=std_val,
            min=min_val,
            max=max_val,
            q1=q1,
            q3=q3,
            iqr=iqr,
            skewness=skew_val,
            is_constant=is_const
        )

    @classmethod
    def compute_categorical_stats(cls, series: pd.Series, name: str) -> CategoricalColumnStats:
        """Calculate descriptive metrics for categorical/text/boolean features."""
        total = len(series)
        valid = series.dropna()
        missing_count = total - len(valid)
        missing_pct = round((missing_count / total * 100.0) if total > 0 else 0.0, 2)
        unique_cnt = int(valid.nunique())

        if len(valid) == 0:
            return CategoricalColumnStats(
                name=name,
                dtype=str(series.dtype),
                count=0,
                missing_count=missing_count,
                missing_percentage=missing_pct,
                unique_count=0,
                is_constant=False,
                is_high_cardinality=False
            )

        val_counts = valid.astype(str).value_counts()
        mode_val = str(val_counts.index[0]) if len(val_counts) > 0 else None
        mode_freq = int(val_counts.iloc[0]) if len(val_counts) > 0 else None
        mode_pct = round((mode_freq / len(valid) * 100.0) if (mode_freq and len(valid) > 0) else 0.0, 2)

        top_cats = [
            CategoricalValueFrequency(
                value=str(cat),
                count=int(cnt),
                percentage=round((cnt / len(valid) * 100.0), 2)
            )
            for cat, cnt in val_counts.head(20).items()
        ]

        is_const = bool(unique_cnt <= 1 and len(valid) > 0)
        is_high_card = bool(unique_cnt > 20 and (total > 0 and (unique_cnt / total) > 0.30))

        return CategoricalColumnStats(
            name=name,
            dtype=str(series.dtype),
            count=len(valid),
            missing_count=missing_count,
            missing_percentage=missing_pct,
            unique_count=unique_cnt,
            mode=mode_val,
            mode_frequency=mode_freq,
            mode_percentage=mode_pct,
            top_categories=top_cats,
            is_constant=is_const,
            is_high_cardinality=is_high_card
        )

    @classmethod
    def compute_datetime_stats(cls, series: pd.Series, name: str) -> DatetimeColumnStats:
        """Calculate min, max, and unique timestamps for date features."""
        total = len(series)
        parsed = pd.to_datetime(series, errors="coerce")
        valid = parsed.dropna()
        missing_count = total - len(valid)
        missing_pct = round((missing_count / total * 100.0) if total > 0 else 0.0, 2)
        unique_cnt = int(valid.nunique())

        min_d = str(valid.min()) if len(valid) > 0 else None
        max_d = str(valid.max()) if len(valid) > 0 else None

        return DatetimeColumnStats(
            name=name,
            dtype=str(series.dtype),
            count=len(valid),
            missing_count=missing_count,
            missing_percentage=missing_pct,
            unique_count=unique_cnt,
            min_date=min_d,
            max_date=max_d
        )

    @classmethod
    def compute_quality_overview(
        cls,
        df: pd.DataFrame,
        columns_info: list[ColumnInfo]
    ) -> QualityOverview:
        """Detect missingness, duplicates, constant columns, and cardinality issues."""
        total_rows = len(df)
        total_cols = len(df.columns)
        total_duplicates = int(df.duplicated().sum())
        dup_pct = round((total_duplicates / total_rows * 100.0) if total_rows > 0 else 0.0, 2)

        missing_list: list[MissingFeatureInfo] = []
        constant_cols: list[str] = []
        high_card_cols: list[str] = []
        all_null_cols: list[str] = []
        issues: list[ColumnQualityIssue] = []

        if total_duplicates > 0:
            issues.append(
                ColumnQualityIssue(
                    column="<dataset>",
                    issue_type="constant_column",  # reuse issue category
                    description=f"{total_duplicates} duplicate rows detected ({dup_pct}% of total records).",
                    severity="medium" if dup_pct < 10 else "high",
                    metric_value=total_duplicates
                )
            )

        for col in columns_info:
            series = df[col.name]
            null_count = int(series.isna().sum())
            null_pct = round((null_count / total_rows * 100.0) if total_rows > 0 else 0.0, 2)
            unique_cnt = int(series.nunique(dropna=True))

            # Missingness checks
            if null_count > 0:
                missing_list.append(
                    MissingFeatureInfo(
                        column=col.name,
                        missing_count=null_count,
                        missing_percentage=null_pct
                    )
                )
                if null_count == total_rows:
                    all_null_cols.append(col.name)
                    issues.append(
                        ColumnQualityIssue(
                            column=col.name,
                            issue_type="all_null",
                            description=f"Column is completely empty (100% missing values).",
                            severity="high",
                            metric_value=100.0
                        )
                    )
                elif null_pct >= 50.0:
                    issues.append(
                        ColumnQualityIssue(
                            column=col.name,
                            issue_type="high_missingness",
                            description=f"High missingness ratio of {null_pct}%.",
                            severity="high",
                            metric_value=null_pct
                        )
                    )
                elif null_pct >= 20.0:
                    issues.append(
                        ColumnQualityIssue(
                            column=col.name,
                            issue_type="high_missingness",
                            description=f"Moderate missingness ratio of {null_pct}%.",
                            severity="medium",
                            metric_value=null_pct
                        )
                    )

            # Constant column checks
            if unique_cnt <= 1 and (total_rows - null_count) > 0:
                constant_cols.append(col.name)
                issues.append(
                    ColumnQualityIssue(
                        column=col.name,
                        issue_type="constant_column",
                        description="Feature has zero variance (constant single value throughout).",
                        severity="medium",
                        metric_value=unique_cnt
                    )
                )

            # High cardinality in non-numeric features
            if col.inferred_type in ["categorical", "text"] and unique_cnt > 25:
                ratio = unique_cnt / total_rows if total_rows > 0 else 0.0
                if ratio > 0.35:
                    high_card_cols.append(col.name)
                    issues.append(
                        ColumnQualityIssue(
                            column=col.name,
                            issue_type="high_cardinality",
                            description=f"High cardinality detected ({unique_cnt} distinct values, {ratio * 100:.1f}% unique ratio). Possible identifier.",
                            severity="low",
                            metric_value=round(ratio * 100, 1)
                        )
                    )

        # Sort missingness by percentage descending
        missing_list.sort(key=lambda x: x.missing_percentage, reverse=True)

        return QualityOverview(
            total_rows=total_rows,
            total_columns=total_cols,
            duplicate_rows=total_duplicates,
            duplicate_percentage=dup_pct,
            columns_with_missing_values=missing_list,
            constant_columns=constant_cols,
            high_cardinality_columns=high_card_cols,
            all_null_columns=all_null_cols,
            quality_issues=issues
        )

    @classmethod
    def compute_correlations(
        cls,
        df: pd.DataFrame,
        columns_info: list[ColumnInfo],
        method: str = "pearson"
    ) -> CorrelationMatrix:
        """Compute Pearson or Spearman correlation matrix for numerical features."""
        if method not in ["pearson", "spearman"]:
            method = "pearson"

        # Filter active numerical columns that have variance
        num_cols = [
            c.name for c in columns_info
            if c.inferred_type == "numeric" and c.name in df.columns
        ]

        # Exclude constant or all-null columns to prevent division by zero in correlation
        valid_num_cols: list[str] = []
        for col in num_cols:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(series) > 1 and series.nunique() > 1 and series.std() > 0:
                valid_num_cols.append(col)

        if len(valid_num_cols) < 2:
            return CorrelationMatrix(method=method, columns=[], matrix=[])

        # Compute pairwise correlation
        subset = df[valid_num_cols].apply(pd.to_numeric, errors="coerce")
        corr_df = subset.corr(method=method)

        matrix: list[list[float | None]] = []
        for row_col in valid_num_cols:
            row_vals: list[float | None] = []
            for col_col in valid_num_cols:
                val = corr_df.loc[row_col, col_col]
                row_vals.append(cls._clean_num(val))
            matrix.append(row_vals)

        return CorrelationMatrix(
            method=method,
            columns=valid_num_cols,
            matrix=matrix
        )

    @classmethod
    def compute_visualization_data(
        cls,
        df: pd.DataFrame,
        column_name: str,
        inferred_type: str,
        max_samples: int = 5000
    ) -> ColumnVisualizationData:
        """Compute histogram bins, box metrics, or category distributions for Plotly."""
        if column_name not in df.columns:
            return ColumnVisualizationData(column=column_name, inferred_type=inferred_type)

        series = df[column_name]
        valid = series.dropna()

        if inferred_type in ["numeric", "boolean"]:
            numeric_valid = pd.to_numeric(valid, errors="coerce").dropna()
            if len(numeric_valid) == 0:
                return ColumnVisualizationData(column=column_name, inferred_type=inferred_type)

            # Sample if dataset is massive to keep Plotly client lightweight
            if len(numeric_valid) > max_samples:
                sample_data = numeric_valid.sample(n=max_samples, random_state=42).tolist()
            else:
                sample_data = numeric_valid.tolist()

            # Histogram bins via numpy
            counts, bin_edges = np.histogram(numeric_valid, bins="auto" if len(numeric_valid) < 1000 else 30)

            # Box plot Tukey statistics
            q1 = float(np.percentile(numeric_valid, 25))
            median = float(np.percentile(numeric_valid, 50))
            q3 = float(np.percentile(numeric_valid, 75))
            iqr = q3 - q1
            lower_fence = q1 - 1.5 * iqr
            upper_fence = q3 + 1.5 * iqr

            within_fences = numeric_valid[(numeric_valid >= lower_fence) & (numeric_valid <= upper_fence)]
            box_min = float(within_fences.min()) if len(within_fences) > 0 else float(numeric_valid.min())
            box_max = float(within_fences.max()) if len(within_fences) > 0 else float(numeric_valid.max())

            outliers = numeric_valid[(numeric_valid < lower_fence) | (numeric_valid > upper_fence)]
            outlier_sample = [cls._clean_num(x) for x in outliers.head(100).tolist() if cls._clean_num(x) is not None]

            return ColumnVisualizationData(
                column=column_name,
                inferred_type=inferred_type,
                histogram_bins=[cls._clean_num(b) for b in bin_edges.tolist()],
                histogram_counts=[int(c) for c in counts.tolist()],
                sample_values=[cls._clean_num(x) for x in sample_data[:1000]],
                box_min=cls._clean_num(box_min),
                box_q1=cls._clean_num(q1),
                box_median=cls._clean_num(median),
                box_q3=cls._clean_num(q3),
                box_max=cls._clean_num(box_max),
                box_outliers=outlier_sample
            )

        elif inferred_type in ["categorical", "text"]:
            val_counts = valid.astype(str).value_counts().head(20)
            return ColumnVisualizationData(
                column=column_name,
                inferred_type=inferred_type,
                categories=[str(c) for c in val_counts.index.tolist()],
                category_counts=[int(cnt) for cnt in val_counts.values.tolist()]
            )

        else:
            # Datetime
            val_counts = valid.astype(str).value_counts().head(20)
            return ColumnVisualizationData(
                column=column_name,
                inferred_type=inferred_type,
                categories=[str(c) for c in val_counts.index.tolist()],
                category_counts=[int(cnt) for cnt in val_counts.values.tolist()]
            )

    @classmethod
    def compute_target_analysis(
        cls,
        df: pd.DataFrame,
        target_col: str,
        inferred_type: str
    ) -> TargetAnalysis:
        """Profile target feature distribution and classify as classification vs regression."""
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataset.")

        series = df[target_col]
        valid = series.dropna()
        unique_cnt = int(valid.nunique())

        # Determine classification vs regression
        is_classification = False
        if inferred_type in ["categorical", "boolean"]:
            is_classification = True
        elif inferred_type == "numeric":
            numeric_valid = pd.to_numeric(valid, errors="coerce").dropna()
            # If values have decimal components, it is continuous regression
            has_decimals = bool((numeric_valid % 1 != 0).any()) if len(numeric_valid) > 0 else False
            if has_decimals:
                is_classification = False
            elif unique_cnt <= 15 and (len(valid) <= 5 or (unique_cnt / len(valid)) <= 0.25):
                is_classification = True
            else:
                is_classification = False

        if is_classification:
            val_counts = valid.astype(str).value_counts()
            distribution = [
                {
                    "class": str(k),
                    "count": int(v),
                    "percentage": round((v / len(valid) * 100.0) if len(valid) > 0 else 0.0, 2)
                }
                for k, v in val_counts.items()
            ]
            summary_stats = {
                "total_count": len(valid),
                "unique_classes": unique_cnt,
                "missing_count": int(series.isna().sum()),
                "majority_class": str(val_counts.index[0]) if len(val_counts) > 0 else None,
                "majority_percentage": round((val_counts.iloc[0] / len(valid) * 100.0) if len(val_counts) > 0 else 0.0, 2)
            }
        else:
            # Numeric continuous target (Regression)
            numeric_valid = pd.to_numeric(valid, errors="coerce").dropna()
            counts, bin_edges = np.histogram(numeric_valid, bins=20)
            distribution = [
                {
                    "bin_start": cls._clean_num(bin_edges[i]),
                    "bin_end": cls._clean_num(bin_edges[i+1]),
                    "count": int(counts[i])
                }
                for i in range(len(counts))
            ]
            summary_stats = {
                "total_count": len(numeric_valid),
                "mean": cls._clean_num(numeric_valid.mean()),
                "std": cls._clean_num(numeric_valid.std(ddof=1)) if len(numeric_valid) > 1 else 0.0,
                "median": cls._clean_num(numeric_valid.median()),
                "min": cls._clean_num(numeric_valid.min()),
                "max": cls._clean_num(numeric_valid.max()),
                "skewness": cls._clean_num(numeric_valid.skew()) if len(numeric_valid) >= 3 else None
            }

        return TargetAnalysis(
            target_column=target_col,
            inferred_type="categorical" if is_classification else "numeric",
            is_classification=is_classification,
            summary_stats=summary_stats,
            distribution=distribution
        )
