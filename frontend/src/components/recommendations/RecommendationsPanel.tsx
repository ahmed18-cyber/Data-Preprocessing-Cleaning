import { useCallback, useEffect, useState } from 'react';
import { Check, X, RefreshCw, Sparkles, AlertCircle, Loader2 } from 'lucide-react';

import {
  fetchRecommendations,
  submitRecommendationDecision,
  type Recommendation,
} from '../../api/recommendationsApi';

interface Props {
  sessionId: string;
}

export function RecommendationsPanel({ sessionId }: Props) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [processingId, setProcessingId] = useState<string | null>(null);

  const loadRecommendations = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchRecommendations(sessionId);
      setRecommendations(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load recommendations.');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    loadRecommendations();
  }, [loadRecommendations]);

  const handleDecision = async (recommendation: Recommendation, decision: 'accept' | 'reject') => {
    setProcessingId(recommendation.id);
    setError('');
    try {
      await submitRecommendationDecision({
        session_id: sessionId,
        recommendation_id: recommendation.id,
        decision,
      });
      await loadRecommendations();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to update recommendation.');
    } finally {
      setProcessingId(null);
    }
  };

  const pendingCount = recommendations.filter((r) => r.status === 'pending').length;

  if (loading) {
    return (
      <div className="flex items-center justify-center gap-3 p-12 text-black bg-cream">
        <Loader2 className="animate-spin text-[#FF4400]" size={22} />
        Loading recommendations…
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="flex items-center gap-2 text-2xl font-bold text-black">
            <Sparkles className="text-[#FF4400]" />
            <span>INTELLIGENT RECOMMENDATIONS</span>
            <span className="ml-2 text-sm font-mono uppercase text-[#FF4400]">MODULE // 03</span>
          </h2>
          <p className="mt-1 text-sm text-black/70">
            Review the suggested preprocessing actions before applying them.
          </p>
        </div>
        <button
          onClick={loadRecommendations}
          className="flex items-center gap-2 rounded border-3 border-black bg-cream px-4 py-2 text-sm font-medium text-black hover:bg-[#FF4400] hover:text-white transition"
        >
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 rounded border-3 border-red-600 bg-cream p-3 text-sm text-red-700">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded border-3 bg-cream p-4 shadow-[2px_2px_0px_0px_#000000]">
          <p className="text-sm text-black/70">Total recommendations</p>
          <p className="mt-1 text-2xl font-bold text-black">{recommendations.length}</p>
        </div>
        <div className="rounded border-3 bg-cream p-4 shadow-[2px_2px_0px_0px_#000000]">
          <p className="text-sm text-black/70">Pending review</p>
          <p className="mt-1 text-2xl font-bold text-[#FF4400]">{pendingCount}</p>
        </div>
        <div className="rounded border-3 bg-cream p-4 shadow-[2px_2px_0px_0px_#000000]">
          <p className="text-sm text-black/70">Accepted</p>
          <p className="mt-1 text-2xl font-bold text-[#0047AB]">
            {recommendations.filter((r) => r.status === 'accepted' || r.status === 'modified').length}
          </p>
        </div>
      </div>

      {/* Recommendations list */}
      {recommendations.length === 0 ? (
        <div className="rounded border-3 border-dashed bg-cream p-10 text-center">
          <Sparkles className="mx-auto mb-3 text-[#FF4400]" size={32} />
          <p className="font-semibold text-black">No recommendations found</p>
          <p className="mt-1 text-sm text-black/70">
            Your dataset may not require any of the supported preprocessing actions.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec) => {
            const busy = processingId === rec.id;
            const resolved = rec.status !== 'pending';
            return (
              <div
                key={rec.id}
                className="rounded border-3 bg-cream p-5 shadow-[2px_2px_0px_0px_#000000]"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <span className="rounded-full bg-[#0047AB] text-white px-3 py-1 text-xs font-mono uppercase">
                      {rec.category.replaceAll('_', ' ')}
                    </span>
                    <h3 className="mt-3 font-bold text-black text-lg">
                      {rec.column}
                    </h3>
                    <p className="mt-1 text-sm text-black/70">{rec.issue}</p>
                  </div>
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-mono uppercase border-3 ${
                      rec.status === 'accepted' || rec.status === 'modified'
                        ? 'bg-[#0047AB] text-white'
                        : rec.status === 'rejected'
                        ? 'bg-red-600 text-white'
                        : 'bg-[#FF4400] text-white'
                    }`}
                  >
                    {rec.status}
                  </span>
                </div>
                <p className="mt-4 text-sm leading-6 text-black/70">{rec.explanation}</p>
                <div className="mt-3 rounded bg-cream p-3 text-sm border-3 border-black">
                  <span className="font-semibold text-black">Suggested action:</span>{' '}
                  <span className="text-black/80">
                    {rec.action}
                    {rec.suggested_method ? ` (${rec.suggested_method})` : ''}
                  </span>
                </div>
                {rec.evidence && (
                  <details className="mt-3 text-sm">
                    <summary className="cursor-pointer font-medium text-black/70">View statistical evidence</summary>
                    <pre className="mt-2 overflow-x-auto rounded bg-cream p-3 text-xs text-black/70 border-3 border-black">
                      {JSON.stringify(rec.evidence, null, 2)}
                    </pre>
                  </details>
                )}
                {!resolved && (
                  <div className="mt-4 flex flex-wrap gap-3">
                    <button
                      disabled={busy}
                      onClick={() => handleDecision(rec, 'accept')}
                      className="flex items-center gap-2 rounded border-3 bg-[#FF4400] px-4 py-2 text-sm font-medium text-white hover:bg-[#FF4400]/90 disabled:opacity-50"
                    >
                      <Check size={16} /> Accept
                    </button>
                    <button
                      disabled={busy}
                      onClick={() => handleDecision(rec, 'reject')}
                      className="flex items-center gap-2 rounded border-3 bg-[#0047AB] px-4 py-2 text-sm font-medium text-white hover:bg-[#0047AB]/90 disabled:opacity-50"
                    >
                      <X size={16} /> Reject
                    </button>
                    {busy && (
                      <Loader2 size={18} className="animate-spin self-center text-[#FF4400]" />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
