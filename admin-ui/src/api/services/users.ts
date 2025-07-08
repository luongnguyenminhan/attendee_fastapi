import { api } from '../client';
import type {
  User,
  CreateUserRequest,
  UpdateUserRequest,
  PaginatedResponse,
  PaginationParams,
  ApiResponse
} from '../types';

export const usersApi = {
  // Get all users với pagination và search
  getUsers: async (params?: PaginationParams): Promise<PaginatedResponse<User>> => {
    const response = await api.get<PaginatedResponse<User>>('/admin/users', { params });
    return response.data;
  },

  // Get user by ID
  getUser: async (userId: string): Promise<User> => {
    const response = await api.get<ApiResponse<User>>(`/admin/users/${userId}`);
    return response.data.data;
  },

  // Create new user
  createUser: async (userData: CreateUserRequest): Promise<User> => {
    const response = await api.post<ApiResponse<User>>('/admin/users', userData);
    return response.data.data;
  },

  // Update user
  updateUser: async (userId: string, userData: UpdateUserRequest): Promise<User> => {
    const response = await api.patch<ApiResponse<User>>(`/admin/users/${userId}`, userData);
    return response.data.data;
  },

  // Delete user
  deleteUser: async (userId: string): Promise<void> => {
    await api.delete(`/admin/users/${userId}`);
  },

  // Toggle user status (activate/deactivate)
  toggleUserStatus: async (userId: string): Promise<User> => {
    const response = await api.patch<ApiResponse<User>>(`/admin/users/${userId}/toggle-status`);
    return response.data.data;
  },

  // Search users
  searchUsers: async (query: string): Promise<User[]> => {
    const response = await api.get<ApiResponse<User[]>>('/admin/users/search', {
      params: { q: query }
    });
    return response.data.data;
  },

  // Get user statistics
  getUserStats: async (): Promise<{
    total_users: number;
    active_users: number;
    inactive_users: number;
    superusers: number;
  }> => {
    const response = await api.get<ApiResponse<any>>('/admin/users/stats');
    return response.data.data;
  }
}; 