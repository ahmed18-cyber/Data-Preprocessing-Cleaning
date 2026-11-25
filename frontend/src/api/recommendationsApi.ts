
import { apiClient } from './client';

export interface Recommendation {
  id: string;
  category: string;
  column: string;
  issue: string;
  evidence: Record<string, unknown>;
  action: string;
  suggested_action?: string;
  suggested_method?: string;
  explanation: string;
  status: 'pending' | 'accepted' | 'rejected' | 'modified';
  dtype?: string;
}

export interface RecommendationDecision {
  session_id: string;
  recommendation_id: string;
  decision: 'accept' | 'reject' | 'modify';
  modified_action?: string;
  modified_method?: string;
}

export async function fetchRecommendations(
  sessionId: string
): Promise<Recommendation[]> {
  const response = await apiClient.get<Recommendation[]>(
    '/recommendations/',
    { params: { session_id: sessionId } }
  );

  return response.data;
}

export async function submitRecommendationDecision(
  decision: RecommendationDecision
): Promise<{ detail: string }> {
  const response = await apiClient.post<{ detail: string }>(
    '/recommendations/decision',
    decision
  );

  return response.data;
}
