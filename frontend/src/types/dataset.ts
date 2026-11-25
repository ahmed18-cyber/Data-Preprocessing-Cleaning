export type InferredType = 'numeric' | 'categorical' | 'datetime' | 'boolean' | 'text';

export interface ColumnInfo {
  name: string;
  original_dtype: string;
  inferred_type: InferredType;
  non_null_count: int;
  null_count: int;
  null_percentage: number;
  unique_count: int;
  sample_values: any[];
}

export type int = number;

export interface DatasetMetadata {
  session_id: string;
  filename: string;
  file_type: 'csv' | 'xlsx' | 'xls';
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  sheet_names?: string[] | null;
  active_sheet?: string | null;
  delimiter?: string | null;
  learning_mode: 'supervised' | 'unsupervised';
  target_column?: string | null;
  created_at: string;
  last_accessed: string;
}

export interface DatasetUploadResponse {
  success: boolean;
  session_id: string;
  metadata: DatasetMetadata;
  columns: ColumnInfo[];
  preview: Record<string, any>[];
}

export interface ConfigureDatasetResponse {
  success: boolean;
  metadata: DatasetMetadata;
}

export interface SheetListResponse {
  success: boolean;
  sheets: string[];
  active_sheet: string;
}

