"""Centralized threshold configuration for diagnostics and recommendations."""
from pydantic import BaseModel


class RecommendationRulesConfig(BaseModel):
    """Configurable thresholds for anomaly detection and recommendations."""
    
    # Missingness
    HIGH_MISSINGNESS_THRESHOLD: float = 0.50       # >= 50% missingness triggers review/drop warning
    LOW_MISSINGNESS_THRESHOLD: float = 0.05        # <= 5% missingness triggers simple imputation
    
    # Skewness
    SKEWNESS_EXTREME_THRESHOLD: float = 1.5        # |skew| > 1.5 triggers Robust/Power scaling
    SKEWNESS_MODERATE_THRESHOLD: float = 0.5       # 0.5 < |skew| <= 1.5
    
    # Outliers
    IQR_MULTIPLIER: float = 1.5                    # Standard Tukey IQR fences
    Z_SCORE_THRESHOLD: float = 3.0                 # Standard Z-score cutoff
    OUTLIER_RATIO_ALERT: float = 0.02              # > 2% outliers triggers alert
    
    # Categoricals
    ONE_HOT_MAX_CARDINALITY: int = 15              # Unique categories <= 15 for OneHotEncoding
    HIGH_CARDINALITY_RATIO: float = 0.30           # Cardinality / rows > 30% flags potential identifier


rules_config = RecommendationRulesConfig()

