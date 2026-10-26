import { apiClient } from './client';
import type { CloudStatus, DashboardStats } from '../types';

export interface HealthResponse {
  status: string;
  api: boolean;
  database: boolean;
  database_message: string;
  timestamp: string;
  version: string;
  app: string;
  environment: string;
}

export interface TestResult {
  provider: string;
  test_passed: boolean;
  errors: string[];
  timestamp: string;
}

export const cloudApi = {
  health: () => apiClient.get<HealthResponse>('/health'),
  status: () => apiClient.get<CloudStatus>('/cloud/status'),
  test: () => apiClient.post<TestResult>('/cloud/test'),
  stats: () => apiClient.get<DashboardStats>('/cloud/stats'),
};
