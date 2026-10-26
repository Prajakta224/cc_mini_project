import { apiClient } from './client';
import type { User, TokenResponse } from '../types';

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  confirm_password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export const authApi = {
  register: (data: RegisterData) =>
    apiClient.post<User>('/auth/register', data),

  login: (data: LoginData) =>
    apiClient.post<TokenResponse>('/auth/login', data),

  logout: () =>
    apiClient.post('/auth/logout'),

  me: () =>
    apiClient.get<User>('/auth/me'),
};
