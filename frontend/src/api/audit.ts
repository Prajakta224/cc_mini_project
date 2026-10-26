import { apiClient } from './client';
import type { AuditEvent } from '../types';

export interface AuditListResponse {
  events: AuditEvent[];
  total: number;
}

export const auditApi = {
  list: (params?: { limit?: number; offset?: number; event_type?: string }) =>
    apiClient.get<AuditListResponse>('/audit', { params }),
};
