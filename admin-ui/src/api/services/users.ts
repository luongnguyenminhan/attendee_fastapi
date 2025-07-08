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
  getUsers: async (params?: PaginationParams): Promise<{ users: User[]; pagination: any; user_stats: any }> => {
    const response = await api.get<{ success: boolean; data: { users: User[]; pagination: any; user_stats: any } }>('/admin/users', { params });
    return response.data.data;
  },

  // Get user by ID
  getUser: async (userId: string): Promise<User> => {
    const response = await api.get<ApiResponse<User>>(`/admin/users/${userId}`);
    return response.data.data;
  },

  // Create new user
  createUser: async (userData: CreateUserRequest): Promise<User> => {
    const formData = new FormData();
    formData.append('email', userData.email);
    formData.append('username', userData.username);
    formData.append('password', userData.password);
    if (userData.first_name) formData.append('first_name', userData.first_name);
    if (userData.last_name) formData.append('last_name', userData.last_name);
    if (userData.role) formData.append('role', userData.role);
    if (userData.organization_id) formData.append('organization_id', userData.organization_id);
    
    const response = await api.post<{ success: boolean; data: User; message?: string }>('/admin/users/create', formData);
    console.log('API Response:', response.data);
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