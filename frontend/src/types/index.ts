// TypeScript type definitions for AFES

export interface User {
  id: number;
  name: string;
  email: string;
  role: 'user' | 'admin';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface FileRecord {
  id: number;
  original_filename: string;
  original_size: number;
  content_type?: string;
  encrypted_object_key: string;
  encrypted_size?: number;
  encryption_algorithm: string;
  format_version: number;
  storage_provider: string;
  upload_timestamp: string;
  status: string;
}

export interface FileListResponse {
  files: FileRecord[];
  total: number;
}

export interface EncryptResponse {
  file_id: number;
  original_filename: string;
  encrypted_object_key: string;
  encryption_algorithm: string;
  original_size: number;
  encrypted_size: number;
  storage_provider: string;
  upload_timestamp: string;
  message: string;
}

export interface AuditEvent {
  id: number;
  user_id?: number;
  event_type: string;
  timestamp: string;
  success: boolean;
  ip_address?: string;
  correlation_id?: string;
  details?: string;
}

export interface CloudStatus {
  provider: string;
  connected: boolean;
  bucket?: string;
  object_count?: number;
  total_bytes?: number;
  message: string;
  warning?: string;
  mode?: string;
}

export interface DashboardStats {
  total_files: number;
  total_original_bytes: number;
  total_encrypted_bytes: number;
  encrypt_operations: number;
  successful_decryptions: number;
  failed_decryptions: number;
  recent_uploads: Array<{
    id: number;
    filename: string;
    size: number;
    uploaded: string;
  }>;
  storage_provider: string;
}

export interface ApiError {
  detail: string;
}
