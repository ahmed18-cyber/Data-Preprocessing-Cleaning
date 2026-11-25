import React, { useRef, useState } from 'react';
import { UploadCloud, AlertCircle, Loader2, CheckCircle2, FileSpreadsheet, ArrowUpRight } from 'lucide-react';
import { useDatasetStore } from '../../stores/datasetStore';

const MAX_SIZE_MB = 50;
const ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls'];

export const FileDropzone: React.FC = () => {
  const { upload, isUploading, uploadProgress, error, successMessage, clearError } = useDatasetStore();
  const [isDragOver, setIsDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndUpload = (file: File) => {
    setValidationError(null);
    clearError();

    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setValidationError(`Unsupported file format. Please upload a CSV, XLSX, or XLS file.`);
      return;
    }

    const sizeMb = file.size / (1024 * 1024);
    if (sizeMb > MAX_SIZE_MB) {
      setValidationError(`File size (${sizeMb.toFixed(1)} MB) exceeds the ${MAX_SIZE_MB} MB limit.`);
      return;
    }

    upload(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndUpload(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndUpload(e.target.files[0]);
    }
  };

  return (
    <div className="w-full my-6">
      <div
        data-dropzone="true"
        tabIndex={0}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        onKeyDown={(e) => {
          if ((e.key === 'Enter' || e.key === ' ') && !isUploading) {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        className={`relative w-full border-4 transition-all duration-150 cursor-pointer p-8 md:p-12 text-center select-none outline-none ${
          isDragOver
            ? 'border-cobalt bg-cobalt/10 shadow-[8px_8px_0px_0px_#0047AB] scale-[1.01]'
            : 'border-black bg-cream hover:bg-[#F4EEDB] hover:shadow-[8px_8px_0px_0px_#000000] focus:border-cobalt focus:shadow-[8px_8px_0px_0px_#0047AB]'
        } ${isUploading ? 'pointer-events-none opacity-90' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileInput}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center gap-4 max-w-2xl mx-auto">
          {/* Neo-brutalist Icon Box */}
          <div className="w-20 h-20 border-3 border-black bg-white flex items-center justify-center shadow-[4px_4px_0px_0px_#000000]">
            {isUploading ? (
              <Loader2 className="h-10 w-10 text-orange animate-spin stroke-[2.5]" />
            ) : (
              <UploadCloud className="h-10 w-10 text-black stroke-[2.5]" />
            )}
          </div>

          {/* Heading */}
          <div className="space-y-2">
            <h2 className="text-3xl md:text-4xl font-black tracking-tight text-black uppercase font-mono">
              {isUploading ? 'INGESTING DATASET...' : 'DROP YOUR DATA HERE.'}
            </h2>
            <p className="text-sm md:text-base font-medium text-black/80 max-w-lg mx-auto">
              Drag and drop your raw tabular file or browse from local storage. Standard CSV and Excel formats supported up to {MAX_SIZE_MB} MB.
            </p>
          </div>

          {/* Supported Format Tags */}
          {!isUploading && (
            <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
              <span className="px-3 py-1 text-xs font-mono font-bold bg-white text-black border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                .CSV
              </span>
              <span className="px-3 py-1 text-xs font-mono font-bold bg-white text-black border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                .XLSX
              </span>
              <span className="px-3 py-1 text-xs font-mono font-bold bg-white text-black border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                .XLS
              </span>
              <span className="px-3 py-1 text-xs font-mono font-bold bg-cream text-black/70 border border-black/40">
                MAX {MAX_SIZE_MB}MB
              </span>
            </div>
          )}

          {/* Action Trigger Button */}
          {!isUploading && (
            <div className="pt-2">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
                className="inline-flex items-center gap-2 px-6 py-3 bg-orange text-white font-mono font-bold text-sm uppercase tracking-wider border-2 border-black shadow-[4px_4px_0px_0px_#000000] hover:bg-orange/90 hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[3px_3px_0px_0px_#000000] active:translate-x-[4px] active:translate-y-[4px] active:shadow-none transition-all"
              >
                <FileSpreadsheet className="h-4 w-4 stroke-[2.5]" />
                <span>Browse Files</span>
                <ArrowUpRight className="h-4 w-4 stroke-[2.5]" />
              </button>
            </div>
          )}

          {/* Upload Progress Bar */}
          {isUploading && (
            <div className="w-full max-w-md mt-4 p-4 border-2 border-black bg-white shadow-[4px_4px_0px_0px_#000000]">
              <div className="flex justify-between items-center text-xs font-mono font-bold text-black uppercase mb-2">
                <span>Streaming & Parsing...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full h-4 border-2 border-black bg-cream p-0.5 overflow-hidden">
                <div
                  className="bg-orange h-full border-r border-black transition-all duration-200"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error Banner */}
      {(validationError || error) && (
        <div className="mt-4 p-4 border-3 border-black bg-red-100 text-black shadow-[4px_4px_0px_0px_#000000] flex items-start gap-3">
          <div className="p-1 bg-red-500 text-white border border-black shrink-0 mt-0.5">
            <AlertCircle className="h-4 w-4 stroke-[3]" />
          </div>
          <div className="flex-1 font-mono text-xs md:text-sm">
            <span className="font-black uppercase tracking-wider block text-red-700">
              [UPLOAD FAILED]
            </span>
            <span className="font-semibold text-black/90">
              {validationError || error}
            </span>
          </div>
        </div>
      )}

      {/* Success Banner */}
      {successMessage && !validationError && !error && (
        <div className="mt-4 p-4 border-3 border-black bg-emerald-100 text-black shadow-[4px_4px_0px_0px_#000000] flex items-start gap-3">
          <div className="p-1 bg-emerald-600 text-white border border-black shrink-0 mt-0.5">
            <CheckCircle2 className="h-4 w-4 stroke-[3]" />
          </div>
          <div className="flex-1 font-mono text-xs md:text-sm">
            <span className="font-black uppercase tracking-wider block text-emerald-800">
              [INGESTION COMPLETE]
            </span>
            <span className="font-semibold text-black/90">
              {successMessage}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
