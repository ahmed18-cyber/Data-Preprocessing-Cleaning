export interface DatasetOverview {
  total_rows: number;
  total_columns: number;
  numerical_columns_count: number;
  categorical_columns_count: number;
  datetime_columns_count: number;
  boolean_columns_count: number;
  text_columns_count: number;
  total_missing_cells: number;
  missing_cells_percentage: number;
  total_duplicate_rows: number;
  duplicate_rows_percentage: number;
  memory_usage_bytes: number;
  memory_usage_formatted: string;
}

export interface NumericalColumnStats {
  name: string;
  dtype: string;
  count: number;
  missing_count: number;
  missing_percentage: number;
  unique_count: number;
  mean: number | null;
  median: number | null;
  std: number | null;
  min: number | null;
  max: number | null;
  q1: number | null;
  q3: number | null;
  iqr: number | null;
  skewness: number | null;
  is_constant: boolean;
}

export interface CategoricalValueFrequency {
  value: string;
  count: number;
  percentage: number;
}

export interface CategoricalColumnStats {
  name: string;
  dtype: string;
  count: number;
  missing_count: number;
  missing_percentage: number;
  unique_count: number;
  mode: string | null;
  mode_frequency: number | null;
  mode_percentage: number | null;
  top_categories: CategoricalValueFrequency[];
  is_constant: boolean;
  is_high_cardinality: boolean;
}

export interface DatetimeColumnStats {
  name: string;
  dtype: string;
  count: number;
  missing_count: number;
  missing_percentage: number;
  unique_count: number;
  min_date: string | null;
  max_date: string | null;
}

export interface MissingFeatureInfo {
  column: string;
  missing_count: number;
  missing_percentage: number;
}

export interface ColumnQualityIssue {
  column: string;
  issue_type: 'constant_column' | 'high_missingness' | 'high_cardinality' | 'all_null';
  description: string;
  severity: 'low' | 'medium' | 'high';
  metric_value?: number | string | null;
}

export interface QualityOverview {
  total_rows: number;
  total_columns: number;
  duplicate_rows: number;
  duplicate_percentage: number;
  columns_with_missing_values: MissingFeatureInfo[];
  constant_columns: string[];
  high_cardinality_columns: string[];
  all_null_columns: string[];
  quality_issues: ColumnQualityIssue[];
}

export interface CorrelationMatrix {
  method: 'pearson' | 'spearman';
  columns: string[];
  matrix: (number | null)[][];
}

export interface ColumnVisualizationData {
  column: string;
  inferred_type: string;
  histogram_bins?: number[] | null;
  histogram_counts?: number[] | null;
  sample_values?: (number | string)[] | null;
  box_min?: number | null;
  box_q1?: number | null;
  box_median?: number | null;
  box_q3?: number | null;
  box_max?: number | null;
  box_outliers?: number[] | null;
  categories?: string[] | null;
  category_counts?: number[] | null;
}

export interface TargetAnalysis {
  target_column: string;
  inferred_type: 'numeric' | 'categorical' | 'boolean';
  is_classification: boolean;
  summary_stats: Record<string, any>;
  distribution: Record<string, any>[];
}

export interface TargetAnalysisResponse {
  has_target: boolean;
  message?: string;
  target?: TargetAnalysis;
}

