"""Recommendation Engine

Generates evidence‑based preprocessing recommendations for a session.

The engine reads the raw dataframe and session metadata, inspects each column,
and produces a list of recommendation dictionaries that are directly consumable
by ``PreprocessingEngine._build_transformers``.

No metadata is written – callers are responsible for persisting the generated
recommendations under the ``recommendations`` key.
"""

import uuid
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy import stats

from app.storage.session_manager import SessionManager


class RecommendationEngine:
    """Utility class for generating preprocessing recommendations.

    The public interface is the static :meth:`generate` method which returns a
    list of dictionaries.  Each dictionary follows the schema expected by the
    preprocessing engine – notably it contains an ``action`` key (the engine
    looks for ``rec.get("action")``).
    """

    @staticmethod
    def _is_target_column(col: str, meta: dict) -> bool:
        """True if *col* is the supervised target column.

        The target column must never appear in feature‑level recommendations.
        """
        return meta.get("learning_mode") == "supervised" and meta.get("target_column") == col

    @staticmethod
    def _make_rec(
        rec_id: str,
        category: str,
        column: str,
        issue: str,
        evidence: Any,
        action: str,
        method: str | None = None,
        explanation: str = "",
    ) -> Dict[str, Any]:
        """Factory that builds a recommendation dict.

        ``status`` is always initialised to ``"pending"``.  The ``action`` key
        satisfies the preprocessing engine; ``suggested_action`` is retained for
        potential frontend consumption but is optional.
        """
        rec: Dict[str, Any] = {
            "id": rec_id,
            "category": category,
            "column": column,
            "issue": issue,
            "evidence": evidence,
            "action": action,
            "suggested_action": action,  # frontend friendly alias
            "explanation": explanation,
            "status": "pending",
        }
        if method:
            rec["suggested_method"] = method
        return rec

    @staticmethod
    def generate(session_id: str) -> List[Dict[str, Any]]:
        """Generate a list of recommendations for *session_id*.

        The function does **not** modify session metadata.
        """
        df: pd.DataFrame = SessionManager.get_raw_dataset(session_id)
        meta: dict = SessionManager.get_metadata(session_id)

        recommendations: List[Dict[str, Any]] = []
        constant_columns: set[str] = set()

        def new_id() -> str:
            return str(uuid.uuid4())

        # -----------------------------------------------------------------
        # 1. Missing values
        # -----------------------------------------------------------------
        for col in df.columns:
            if RecommendationEngine._is_target_column(col, meta):
                continue
            null_cnt = int(df[col].isna().sum())
            if null_cnt > 0:
                dtype = str(df[col].dtype)
                issue = f"{null_cnt} missing values"
                evidence = {
                    "missing_count": null_cnt,
                    "missing_pct": round(null_cnt / len(df) * 100, 2),
                }
                explanation = (
                    f"Column '{col}' has {null_cnt} missing entries; imputation is required."
                )
                rec = RecommendationEngine._make_rec(
                    rec_id=new_id(),
                    category="missing_values",
                    column=col,
                    issue=issue,
                    evidence=evidence,
                    action="impute",
                    explanation=explanation,
                )
                # include dtype for the preprocessing engine to decide numeric vs categorical
                rec["dtype"] = dtype
                recommendations.append(rec)

        # -----------------------------------------------------------------
        # 2. Constant columns (zero variance after dropping NaNs)
        # -----------------------------------------------------------------
        for col in df.columns:
            if RecommendationEngine._is_target_column(col, meta):
                continue
            non_null = df[col].dropna()
            if len(non_null) == 0:
                continue
            if non_null.nunique() <= 1:
                constant_columns.add(col)
                issue = "constant column (zero variance)"
                evidence = {"unique_values": non_null.unique().tolist()}
                explanation = f"Column '{col}' is constant and can be removed."
                rec = RecommendationEngine._make_rec(
                    rec_id=new_id(),
                    category="constant_columns",
                    column=col,
                    issue=issue,
                    evidence=evidence,
                    action="remove",
                    explanation=explanation,
                )
                recommendations.append(rec)

        # -----------------------------------------------------------------
        # 3. Numerical outliers (IQR method)
        # -----------------------------------------------------------------
        numeric_cols = [
            c
            for c in df.select_dtypes(include=[np.number]).columns
            if not RecommendationEngine._is_target_column(c, meta)
        ]
        for col in numeric_cols:
            series = df[col].dropna()
            if series.empty:
                continue
            q1 = float(series.quantile(0.25))
            q3 = float(series.quantile(0.75))
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outlier_mask = (series < lower) | (series > upper)
            outlier_cnt = int(outlier_mask.sum())
            if outlier_cnt > 0:
                issue = f"{outlier_cnt} outlier values (IQR method)"
                evidence = {
                    "q1": round(q1, 4),
                    "q3": round(q3, 4),
                    "iqr": round(iqr, 4),
                    "lower_bound": round(lower, 4),
                    "upper_bound": round(upper, 4),
                    "outlier_count": outlier_cnt,
                }
                explanation = (
                    f"Column '{col}' has {outlier_cnt} values outside IQR bounds; clipping recommended."
                )
                rec = RecommendationEngine._make_rec(
                    rec_id=new_id(),
                    category="numerical_outliers",
                    column=col,
                    issue=issue,
                    evidence=evidence,
                    action="clip",
                    explanation=explanation,
                )
                recommendations.append(rec)

        # -----------------------------------------------------------------
        # 4. Skewed numerical columns – safe log1p only for non‑negative data
        # -----------------------------------------------------------------
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 3:
                continue
            # Check for any non‑positive values; log1p would be unsafe
            if (series <= 0).any():
                continue
            skew = float(stats.skew(series, bias=False))
            if abs(skew) >= 1.0:
                issue = f"skewness = {round(skew, 4)}"
                evidence = {"skewness": round(skew, 4)}
                explanation = (
                    f"Column '{col}' is highly skewed; a log1p transformation is safe and suggested."
                )
                rec = RecommendationEngine._make_rec(
                    rec_id=new_id(),
                    category="skewed_numeric",
                    column=col,
                    issue=issue,
                    evidence=evidence,
                    action="transform",
                    method="log",
                    explanation=explanation,
                )
                recommendations.append(rec)

        # -----------------------------------------------------------------
        # 5. Datetime columns
        # -----------------------------------------------------------------
        for col in df.columns:
            if RecommendationEngine._is_target_column(col, meta):
                continue
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                issue = "datetime feature"
                evidence = {"dtype": str(df[col].dtype)}
                explanation = (
                    f"Column '{col}' is datetime; extracting components (year, month, …) is recommended."
                )
                rec = RecommendationEngine._make_rec(
                    rec_id=new_id(),
                    category="datetime_extraction",
                    column=col,
                    issue=issue,
                    evidence=evidence,
                    action="extract",
                    explanation=explanation,
                )
                recommendations.append(rec)

        # -----------------------------------------------------------------
        # 6. Numerical scaling – skip columns that are constant
        # -----------------------------------------------------------------
        for col in numeric_cols:
            if col in constant_columns:
                continue
            # Choose robust scaling if outliers were flagged, otherwise standard
            has_outlier = any(
                r["column"] == col and r["category"] == "numerical_outliers" for r in recommendations
            )
            method = "robust" if has_outlier else "standard"
            issue = "scaling required for numeric column"
            evidence = {"method": method}
            explanation = (
                f"Column '{col}' should be scaled using {method} scaling for comparable magnitudes."
            )
            rec = RecommendationEngine._make_rec(
                rec_id=new_id(),
                category="scaling",
                column=col,
                issue=issue,
                evidence=evidence,
                action="scale",
                method=method,
                explanation=explanation,
            )
            recommendations.append(rec)

        # -----------------------------------------------------------------
        # 7. Categorical encoding – OneHot for low cardinality, Ordinal otherwise
        # -----------------------------------------------------------------
        categorical_cols = [
            c
            for c in df.select_dtypes(include=["object", "category", "bool"]).columns
            if not RecommendationEngine._is_target_column(c, meta)
        ]
        for col in categorical_cols:
            unique_cnt = int(df[col].nunique(dropna=True))
            if unique_cnt == 0:
                continue
            # Low cardinality (<=10) -> OneHot, high -> Ordinal (both supported)
            method = "onehot" if unique_cnt <= 10 else "ordinal"
            issue = f"categorical column with {unique_cnt} distinct values"
            evidence = {"unique_values": unique_cnt}
            explanation = (
                f"Column '{col}' will be encoded using {method} encoding."
            )
            rec = RecommendationEngine._make_rec(
                rec_id=new_id(),
                category="categorical_encoding",
                column=col,
                issue=issue,
                evidence=evidence,
                action="encode",
                method=method,
                explanation=explanation,
            )
            recommendations.append(rec)

        # -----------------------------------------------------------------
        # 8. Class imbalance detection (SMOTE recommendation) – supervised classification only
        # -----------------------------------------------------------------
        learning_mode = meta.get("learning_mode", "unsupervised")
        target_col = meta.get("target_column")
        if learning_mode == "supervised" and target_col:
            # Ensure the target column is not considered a feature (already excluded in other loops)
            target_series = df[target_col].dropna()
            if not target_series.empty:
                # Determine if target is classification:
                # - non-numeric dtype => classification
                # - numeric dtype with few unique integer/boolean values (<=10) => classification
                is_classification = False
                if not pd.api.types.is_numeric_dtype(target_series):
                    is_classification = True
                else:
                    if (pd.api.types.is_integer_dtype(target_series) or pd.api.types.is_bool_dtype(target_series)) and target_series.nunique(dropna=True) <= 10:
                        is_classification = True
                if is_classification:
                    class_counts = target_series.value_counts()
                    if len(class_counts) >= 2:
                        majority = int(class_counts.max())
                        minority = int(class_counts.min())
                        if minority >= 2:
                            ratio = round(minority / majority, 4) if majority > 0 else 0
                            if ratio <= 0.30:
                                issue = "class imbalance detected"
                                evidence = {
                                    "class_counts": class_counts.to_dict(),
                                    "imbalance_ratio": ratio,
                                }
                                explanation = (
                                    f"Target column '{target_col}' exhibits class imbalance (minority/majority ratio {ratio}). "
                                    "SMOTE can generate synthetic samples for the minority class to improve classifier performance."
                                )
                                rec = RecommendationEngine._make_rec(
                                    rec_id=new_id(),
                                    category="class_imbalance",
                                    column=target_col,
                                    issue=issue,
                                    evidence=evidence,
                                    action="apply_smote",
                                    explanation=explanation,
                                )
                                recommendations.append(rec)
        return recommendations
