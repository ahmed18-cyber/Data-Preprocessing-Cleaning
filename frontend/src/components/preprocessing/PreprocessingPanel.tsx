import { useState } from 'react';
import { Play, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { executePreprocessing, type PreprocessingSummary } from '../../api/preprocessingApi';

interface Props {
  sessionId: string;
}

export function PreprocessingPanel({ sessionId }: Props) {
  const [testSize, setTestSize] = useState(0.2);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<PreprocessingSummary | null>(null);
  const [error, setError] = useState('');

  const handleExecute = async () => {
    setLoading(true);
    setError('');
    setSummary(null);
    try {
      const result = await executePreprocessing({
        session_id: sessionId,
        test_size: testSize,
      });
      setSummary(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Preprocessing failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-black">
          DATA PREPROCESSING
        </h2>
        <p className="mt-1 text-sm text-black/70">
          Execute the accepted preprocessing recommendations.
        </p>
      </div>

      {/* Test size selector */}
      <div className="rounded border-3 bg-cream p-5 space-y-4 shadow-[2px_2px_0px_0px_#000000]">
        <label className="block text-sm font-semibold text-black/70">
          Test dataset proportion
        </label>
        <p className="mt-1 text-xs text-black/50">
          Select the percentage reserved for testing in supervised mode.
        </p>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="0.1"
            max="0.4"
            step="0.05"
            value={testSize}
            onChange={(e) => setTestSize(Number(e.target.value))}
            className="flex-1"
          />
          <span className="w-16 text-right font-bold text-[#FF4400]">
            {Math.round(testSize * 100)}%
          </span>
        </div>
        <button
          onClick={handleExecute}
          disabled={loading}
          className="flex items-center gap-2 rounded border-3 bg-[#FF4400] px-5 py-3 text-sm font-semibold text-white hover:bg-[#FF4400]/90 disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="animate-spin" size={18} />
          ) : (
            <Play size={18} />
          )}
          {loading ? 'Processing…' : 'Execute preprocessing'}
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 rounded border-3 border-red-600 bg-cream p-4 text-sm text-red-700">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {/* Summary */}
      {summary && (
        <div className="rounded border-3 border-green-600 bg-cream p-5 shadow-[2px_2px_0px_0px_#000000]">
          <div className="flex items-center gap-2 font-semibold text-green-800">
            <CheckCircle2 size={20} />
            Preprocessing completed successfully
          </div>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="rounded border-3 bg-cream p-4">
              <p className="text-sm text-black/70">Training rows</p>
              <p className="mt-1 text-2xl font-bold text-black">{summary.train_rows ?? '—'}</p>
            </div>
            <div className="rounded border-3 bg-cream p-4">
              <p className="text-sm text-black/70">Testing rows</p>
              <p className="mt-1 text-2xl font-bold text-black">{summary.test_rows ?? '—'}</p>
            </div>
          </div>
          {summary.dropped_columns && (
            <div className="mt-4 text-sm text-black/70">
              <strong>Dropped columns:</strong> {summary.dropped_columns.join(', ') || 'None'}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
