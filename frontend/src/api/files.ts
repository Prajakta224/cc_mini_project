import { apiClient } from './client';
import type { FileRecord, FileListResponse, EncryptResponse } from '../types';

export type { FileRecord, FileListResponse };

export const filesApi = {
  encrypt: (file: File, onUploadProgress?: (pct: number) => void) => {
    const form = new FormData();
    form.append('file', file);
    return apiClient.post<EncryptResponse>('/files/encrypt', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (evt) => {
        if (evt.total && onUploadProgress) {
          onUploadProgress(Math.round((evt.loaded / evt.total) * 100));
        }
      },
    });
  },

  list: () =>
    apiClient.get<FileListResponse>('/files'),

  getOne: (id: number) =>
    apiClient.get<FileRecord>(`/files/${id}`),

  decrypt: (id: number) =>
    apiClient.post(`/files/${id}/decrypt`, {}, { responseType: 'blob' }),

  delete: (id: number) =>
    apiClient.delete(`/files/${id}`),

  tamperTest: (id: number) =>
    apiClient.post<{ tamper_detected: boolean; message: string }>(`/files/${id}/tamper-test`),
};
