
"""Preprocessing engine that builds a scikit-learn Pipeline based on accepted recommendations.

It respects leakage prevention rules: for supervised mode it separates the target column,
splits the data into train/test before fitting any transformer, and never uses the target
values to compute transformer parameters.
"""

from typing import Any, Dict, List, Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
    OneHotEncoder,
    OrdinalEncoder,
    FunctionTransformer,
)
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE, SMOTENC
from sklearn.model_selection import train_test_split

from app.storage.session_manager import SessionManager
from app.core.config import settings


class PreprocessingEngine:
    """Build and execute a preprocessing pipeline."""

    @staticmethod
    def _get_target_info(
        df: pd.DataFrame, meta: dict
    ) -> Tuple[pd.Series | None, pd.DataFrame, str | None]:
        """Extract the target column without modifying the original DataFrame."""

        learning_mode = meta.get("learning_mode", "unsupervised")
        target_col = meta.get("target_column")

        if learning_mode == "supervised" and target_col and target_col in df.columns:
            y = df[target_col].copy()
            X = df.drop(columns=[target_col])
            return y, X, target_col

        return None, df.copy(), None

    @staticmethod
    def _build_transformers(
        accepted: List[Dict[str, Any]],
        include_imputers: bool = True,
        skip_datetime_extraction: bool = False,
    ) -> Tuple[ColumnTransformer, List[str]]:
        """Build transformers from accepted recommendations."""

        numeric_cols: List[str] = []
        categorical_cols: List[str] = []
        datetime_cols: List[str] = []
        drop_cols: List[str] = []
        transformers: List[Tuple[str, Any, List[str]]] = []

        for rec in accepted:
            cat = rec.get("category")
            col = rec.get("column")
            action = rec.get("action")

            if not col:
                continue

            if cat == "constant_columns" and action == "remove":
                drop_cols.append(col)
                continue

            if cat == "missing_values":
                dtype = rec.get("dtype")
                if dtype in ("int64", "float64", "numeric"):
                    numeric_cols.append(col)
                else:
                    categorical_cols.append(col)

            elif cat == "numerical_outliers" and action == "clip":
                numeric_cols.append(col)

            elif cat == "skewed_numeric" and action == "transform":
                numeric_cols.append(col)

            elif cat == "scaling" and action == "scale":
                numeric_cols.append(col)

            elif cat == "categorical_encoding" and action == "encode":
                categorical_cols.append(col)

            elif cat == "datetime_extraction":
                datetime_cols.append(col)

        # Remove duplicate column names from the lists.
        numeric_cols = list(dict.fromkeys(numeric_cols))
        categorical_cols = list(dict.fromkeys(categorical_cols))
        datetime_cols = list(dict.fromkeys(datetime_cols))

                # Numeric pipeline.
        if numeric_cols:
            steps: List[Tuple[str, Any]] = []

            # --- Imputer step (optional) ---
            if include_imputers:
                steps.append(("imputer", SimpleImputer(strategy="median")))

            scaling_methods = {
                "standard": StandardScaler(),
                "minmax": MinMaxScaler(),
                "robust": RobustScaler(),
            }

            scale_method = None
            for rec in accepted:
                if (
                    rec.get("category") == "scaling"
                    and rec.get("action") == "scale"
                ):
                    scale_method = rec.get("suggested_method")
                    break

            if scale_method in scaling_methods:
                steps.append(("scaler", scaling_methods[scale_method]))

            outlier_cols = [
                rec["column"]
                for rec in accepted
                if rec.get("category") == "numerical_outliers"
                and rec.get("action") == "clip"
                and rec.get("column")
            ]

            if outlier_cols:
                def clip_iqr(arr):
                    import numpy as np

                    q1 = np.percentile(arr, 25, axis=0)
                    q3 = np.percentile(arr, 75, axis=0)
                    iqr = q3 - q1

                    lower = q1 - settings.OUTLIER_IQR_FACTOR * iqr
                    upper = q3 + settings.OUTLIER_IQR_FACTOR * iqr

                    return np.clip(arr, lower, upper)

                steps.append(("outlier_clip", FunctionTransformer(clip_iqr)))

            skew_cols = [
                rec["column"]
                for rec in accepted
                if rec.get("category") == "skewed_numeric"
                and rec.get("action") == "transform"
                and rec.get("column")
            ]

            transformers.append(("num", Pipeline(steps=steps), numeric_cols))



        # Categorical pipeline.
        if categorical_cols:
            enc_type = None

            for rec in accepted:
                if (
                    rec.get("category") == "categorical_encoding"
                    and rec.get("action") == "encode"
                ):
                    enc_type = rec.get("suggested_method")
                    break

            if enc_type == "onehot":
                try:
                    encoder = OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False,
                    )
                except TypeError:
                    encoder = OneHotEncoder(
                        handle_unknown="ignore",
                        sparse=False,
                    )
            else:
                encoder = OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                )

            cat_pipe = Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", encoder),
                ]
            )

            transformers.append(
                ("cat", cat_pipe, categorical_cols)
            )

        # Datetime feature extraction.
        if datetime_cols:

            def extract_datetime(df):
                out = {}

                for col in datetime_cols:
                    series = pd.to_datetime(df[col], errors="coerce")

                    out[f"{col}_year"] = series.dt.year
                    out[f"{col}_month"] = series.dt.month
                    out[f"{col}_day"] = series.dt.day
                    out[f"{col}_weekday"] = series.dt.weekday
                    out[f"{col}_hour"] = series.dt.hour

                return pd.DataFrame(out, index=df.index)

            dt_transformer = FunctionTransformer(
                extract_datetime,
                validate=False,
            )

            transformers.append(
                ("datetime", dt_transformer, datetime_cols)
            )

        column_transformer = ColumnTransformer(
            transformers=transformers,
            remainder="passthrough",
            sparse_threshold=0,
        )

        return column_transformer, drop_cols

    @staticmethod
    def run(session_id: str, test_size: float = 0.2) -> Dict[str, Any]:
        """Execute preprocessing and save the resulting datasets."""

        # 1. Load the original dataset and session metadata.
        raw_df = SessionManager.get_raw_dataset(session_id)
        meta = SessionManager.get_metadata(session_id)

        accepted = meta.get("accepted_recommendations", [])

        # 2. Separate the target column in supervised mode.
        y, X, target_name = PreprocessingEngine._get_target_info(
            raw_df, meta
        )

        # 3. Build the preprocessing transformer.
        transformer, cols_to_drop = (
            PreprocessingEngine._build_transformers(accepted)
        )

        drop_cols = list(cols_to_drop)

        # 4. Remove accepted columns from the feature dataset.
        if drop_cols:
            X = X.drop(
                columns=[col for col in drop_cols if col in X.columns]
            )

        # 5. Split supervised data BEFORE fitting transformers.
        if y is not None:
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=test_size,
                random_state=42,
                stratify=y if y.nunique() > 1 else None,
            )
        else:
            X_train = X.copy()
            X_test = None
            y_train = None
            y_test = None

        # 6. Fit only on training features.
        transformer.fit(X_train)

        X_train_t = transformer.transform(X_train)

        # ------------------------------------------------------------
        # SMOTE handling – apply only when the user accepted the class
        # imbalance recommendation.
        # ------------------------------------------------------------
        smote_applied = False
        smote_method = None
        smote_original_distribution = None
        smote_resampled_distribution = None
        smote_skip_reason = None

        # Check for accepted SMOTE recommendation
        if any(rec.get("category") == "class_imbalance" and rec.get("action") == "apply_smote" for rec in accepted):
            # Validate supervised classification mode and target
            if meta.get("learning_mode") != "supervised":
                smote_skip_reason = "SMOTE requires supervised mode"
            elif target_name is None:
                smote_skip_reason = "No target column defined for SMOTE"
            elif y_train is None:
                smote_skip_reason = "Target column not found in data"
            else:
                # Ensure the target is categorical (binary/multi-class)
                if y_train.nunique() < 2:
                    smote_skip_reason = "Target has less than 2 classes"
                else:
                    # Prepare DataFrame of transformed training features
                    try:
                        feature_names = list(transformer.get_feature_names_out())
                    except Exception:
                        n_features = X_train_t.shape[1]
                        feature_names = [f"feature_{i}" for i in range(n_features)]
                    X_train_feat = pd.DataFrame(X_train_t, columns=feature_names, index=X_train.index)

                    # Record original class distribution
                    smote_original_distribution = y_train.value_counts().to_dict()

                    # Apply SMOTE (numeric only). For simplicity we use SMOTE; if categorical columns were needed we could switch to SMOTENC.
                    try:
                        smote = SMOTE(random_state=42)
                        X_resampled, y_resampled = smote.fit_resample(X_train_feat, y_train)
                        smote_applied = True
                        smote_method = "SMOTE"
                        smote_resampled_distribution = pd.Series(y_resampled).value_counts().to_dict()
                        # Replace training data for downstream steps
                        X_train_t = X_resampled.values
                        y_train = pd.Series(y_resampled, index=X_resampled.index)
                    except Exception as exc:
                        smote_skip_reason = f"SMOTE failed: {exc}"
        else:
            smote_skip_reason = "SMOTE recommendation not accepted"

        # 7. Transform test features without fitting again.
        X_test_t = (
            transformer.transform(X_test)
            if X_test is not None
            else None
        )

        # 8. Get transformed feature names.
        try:
            feature_names = list(
                transformer.get_feature_names_out()
            )
        except Exception:
            n_features = X_train_t.shape[1]
            feature_names = [
                f"feature_{i}" for i in range(n_features)
            ]

        # 9. Create the training DataFrame.
        # 9. Create the training DataFrame.
        train_df = pd.DataFrame(
            X_train_t,
            columns=feature_names,
            index=X_train.index,
        )

        # 10. Create the test DataFrame when supervised mode is used.
        test_df = None

        if X_test_t is not None:
            test_df = pd.DataFrame(
                X_test_t,
                columns=feature_names,
                index=X_test.index,
            )

        # 11. Re-attach the target column.
        if y is not None:
            train_df[target_name] = y_train.reindex(
                train_df.index
            )

            test_df[target_name] = y_test.reindex(
                test_df.index
            )

        # 12. Save processed datasets.
        sess_dir = settings.storage_path / session_id
        sess_dir.mkdir(parents=True, exist_ok=True)

        processed_train_path = (
            sess_dir / "processed_train.parquet"
        )

        processed_test_path = (
            sess_dir / "processed_test.parquet"
            if test_df is not None
            else None
        )

        train_df.to_parquet(
            processed_train_path,
            engine="pyarrow",
        )

        if test_df is not None:
            test_df.to_parquet(
                processed_test_path,
                engine="pyarrow",
            )

        # 13. Store preprocessing summary in session metadata.
        # 13. Store preprocessing summary in session metadata.
        summary = {
            "train_rows": len(train_df),
            "test_rows": len(test_df) if test_df is not None else 0,
            "train_path": str(processed_train_path),
            "test_path": (
                str(processed_test_path)
                if processed_test_path
                else None
            ),
            "dropped_columns": drop_cols,
            "applied_transformers": [
                name
                for name, _, _ in transformer.transformers
            ],
            # SMOTE metadata (may be absent if not applied)
            "smote_applied": smote_applied,
            "smote_method": smote_method,
            "smote_original_distribution": smote_original_distribution,
            "smote_resampled_distribution": smote_resampled_distribution,
            "smote_skip_reason": smote_skip_reason,
        }





        meta["preprocess_summary"] = summary

        SessionManager.update_metadata(session_id, meta)

        return summary
