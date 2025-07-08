import { api } from '../client';
import type {
  Organization,
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
  PaginatedResponse,
  PaginationParams,
  ApiResponse
} from '../types';

export const organizationsApi = {
  // Get all organizations với pagination và filtering
  getOrganizations: async (params?: PaginationParams & {
    status?: 'active' | 'suspended' | 'inactive';
  }): Promise<PaginatedResponse<Organization>> => {
    const response = await api.get<PaginatedResponse<Organization>>('/admin/organizations', { params });
    return response.data;
  },

  // Get organization by ID
  getOrganization: async (orgId: string): Promise<Organization> => {
    const response = await api.get<ApiResponse<Organization>>(`/admin/organizations/${orgId}`);
    return response.data.data;
  },

  // Create new organization
  createOrganization: async (orgData: CreateOrganizationRequest): Promise<Organization> => {
    const response = await api.post<ApiResponse<Organization>>('/admin/organizations', orgData);
    return response.data.data;
  },

  // Update organization
  updateOrganization: async (orgId: string, orgData: UpdateOrganizationRequest): Promise<Organization> => {
    const response = await api.patch<ApiResponse<Organization>>(`/admin/organizations/${orgId}`, orgData);
    return response.data.data;
  },

  // Delete organization
  deleteOrganization: async (orgId: string): Promise<void> => {
    await api.delete(`/admin/organizations/${orgId}`);
  },

  // Update organization credits
  updateCredits: async (orgId: string, centicredits: number): Promise<Organization> => {
    const response = await api.patch<ApiResponse<Organization>>(`/admin/organizations/${orgId}/credits`, {
      centicredits
    });
    return response.data.data;
  },

  // Add credits to organization
  addCredits: async (orgId: string, amount: number): Promise<Organization> => {
    const response = await api.post<ApiResponse<Organization>>(`/admin/organizations/${orgId}/add-credits`, {
      amount
    });
    return response.data.data;
  },

  // Toggle webhooks for organization
  toggleWebhooks: async (orgId: string): Promise<Organization> => {
    const response = await api.patch<ApiResponse<Organization>>(`/admin/organizations/${orgId}/toggle-webhooks`);
    return response.data.data;
  },

  // Suspend organization
  suspendOrganization: async (orgId: string): Promise<Organization> => {
    const response = await api.patch<ApiResponse<Organization>>(`/admin/organizations/${orgId}/suspend`);
    return response.data.data;
  },

  // Activate organization
  activateOrganization: async (orgId: string): Promise<Organization> => {
    const response = await api.patch<ApiResponse<Organization>>(`/admin/organizations/${orgId}/activate`);
    return response.data.data;
  },

  // Get organization statistics
  getOrganizationStats: async (): Promise<{
    total_count: number;
    active_count: number;
    suspended_count: number;
    inactive_count: number;
    total_credits: number;
    webhooks_enabled_count: number;
  }> => {
    const response = await api.get<ApiResponse<any>>('/admin/organizations/stats');
    return response.data.data;
  },

  // Get organization's projects
  getOrganizationProjects: async (orgId: string): Promise<any[]> => {
    const response = await api.get<ApiResponse<any[]>>(`/admin/organizations/${orgId}/projects`);
    return response.data.data;
  },

  // Get organization's users
  getOrganizationUsers: async (orgId: string): Promise<any[]> => {
    const response = await api.get<ApiResponse<any[]>>(`/admin/organizations/${orgId}/users`);
    return response.data.data;
  }
}; 