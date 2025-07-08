import { api } from '../client';
import type {
  Project,
  CreateProjectRequest,
  UpdateProjectRequest,
  ApiKey,
  PaginatedResponse,
  PaginationParams,
  ApiResponse
} from '../types';

export const projectsApi = {
  // Get all projects với pagination và filtering
  getProjects: async (params?: PaginationParams & {
    status?: 'active' | 'archived';
    organization_id?: string;
  }): Promise<PaginatedResponse<Project>> => {
    const response = await api.get<PaginatedResponse<Project>>('/admin/projects', { params });
    return response.data;
  },

  // Get project by ID
  getProject: async (projectId: string): Promise<Project> => {
    const response = await api.get<ApiResponse<Project>>(`/admin/projects/${projectId}`);
    return response.data.data;
  },

  // Create new project
  createProject: async (projectData: CreateProjectRequest): Promise<Project> => {
    const response = await api.post<ApiResponse<Project>>('/admin/projects', projectData);
    return response.data.data;
  },

  // Update project
  updateProject: async (projectId: string, projectData: UpdateProjectRequest): Promise<Project> => {
    const response = await api.patch<ApiResponse<Project>>(`/admin/projects/${projectId}`, projectData);
    return response.data.data;
  },

  // Delete project
  deleteProject: async (projectId: string): Promise<void> => {
    await api.delete(`/admin/projects/${projectId}`);
  },

  // Archive project
  archiveProject: async (projectId: string): Promise<Project> => {
    const response = await api.patch<ApiResponse<Project>>(`/admin/projects/${projectId}/archive`);
    return response.data.data;
  },

  // Activate project
  activateProject: async (projectId: string): Promise<Project> => {
    const response = await api.patch<ApiResponse<Project>>(`/admin/projects/${projectId}/activate`);
    return response.data.data;
  },

  // Get project statistics
  getProjectStats: async (): Promise<{
    total_count: number;
    active_count: number;
    archived_count: number;
  }> => {
    const response = await api.get<ApiResponse<any>>('/admin/projects/stats');
    return response.data.data;
  },

  // API Keys management
  
  // Get project's API keys
  getProjectApiKeys: async (projectId: string): Promise<ApiKey[]> => {
    const response = await api.get<ApiResponse<ApiKey[]>>(`/admin/projects/${projectId}/api-keys`);
    return response.data.data;
  },

  // Create new API key for project
  createApiKey: async (projectId: string, keyData: { name: string }): Promise<ApiKey & { key: string }> => {
    const response = await api.post<ApiResponse<ApiKey & { key: string }>>(
      `/admin/projects/${projectId}/api-keys`, 
      keyData
    );
    return response.data.data;
  },

  // Delete API key
  deleteApiKey: async (projectId: string, keyId: string): Promise<void> => {
    await api.delete(`/admin/projects/${projectId}/api-keys/${keyId}`);
  },

  // Get project's bots
  getProjectBots: async (projectId: string): Promise<any[]> => {
    const response = await api.get<ApiResponse<any[]>>(`/admin/projects/${projectId}/bots`);
    return response.data.data;
  },

  // Get project's webhooks
  getProjectWebhooks: async (projectId: string): Promise<any[]> => {
    const response = await api.get<ApiResponse<any[]>>(`/admin/projects/${projectId}/webhooks`);
    return response.data.data;
  }
}; 