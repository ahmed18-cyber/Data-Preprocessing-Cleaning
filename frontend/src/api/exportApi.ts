
import { apiClient } from './client';

export async function downloadProcessedData(
  sessionId: string,
  type: 'train' | 'test'
): Promise<void> {
  const response = await apiClient.get('/export/data', {
    params: { session_id: sessionId, type },
    responseType: 'blob',
  });

  const blob = new Blob([response.data], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = `processed_${type}.csv`;
  document.body.appendChild(link);
  link.click();
  link.remove();

  window.URL.revokeObjectURL(url);
}

export async function downloadAuditReport(
  sessionId: string
): Promise<void> {
  const response = await apiClient.get('/export/report', {
    params: { session_id: sessionId },
    responseType: 'blob',
  });

  const blob = new Blob([response.data], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  });

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');

  link.href = url;
  link.download = 'preprocessing_audit_report.xlsx';

  document.body.appendChild(link);
  link.click();
  link.remove();

  window.URL.revokeObjectURL(url);
}
