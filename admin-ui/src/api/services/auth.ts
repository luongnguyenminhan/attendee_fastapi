import { api } from '../client';
import type { LoginRequest, LoginResponse, RefreshTokenRequest, User, ApiResponse } from '../types';

export const authApi = {
  // Login
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<ApiResponse<LoginResponse>>('/admin/auth/login', credentials);
    return response.data.data;
  },

  // Logout
  logout: async (): Promise<void> => {
    await api.post('/admin/auth/logout');
    localStorage.removeItem('auth_token');
  },

  // Refresh token
  refreshToken: async (refreshData: RefreshTokenRequest): Promise<LoginResponse> => {
    const response = await api.post<ApiResponse<LoginResponse>>('/admin/auth/refresh', refreshData);
    return response.data.data;
  },

  // Get current user profile
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<ApiResponse<User>>('/admin/auth/me');
    return response.data.data;
  },

  // Verify token
  verifyToken: async (): Promise<{ valid: boolean; user?: User }> => {
    try {
      const response = await api.get<ApiResponse<any>>('/admin/auth/verify');
      return response.data.data;
    } catch {
      // If verification fails, remove the token and redirect
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
      return { valid: false };
    }
  }
}; 