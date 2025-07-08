import { api } from '../client';
import type { SystemStats, SystemConfig, ApiResponse } from '../types';

export const dashboardApi = {
  // Get system statistics
  getSystemStats: async (): Promise<SystemStats> => {
    const response = await api.get<ApiResponse<SystemStats>>('/admin/dashboard/stats');
    return response.data.data;
  },

  // Get system configuration
  getSystemConfig: async (): Promise<SystemConfig> => {
    const response = await api.get<ApiResponse<SystemConfig>>('/admin/dashboard/config');
    return response.data.data;
  },

  // Update system configuration
  updateSystemConfig: async (config: Partial<SystemConfig>): Promise<SystemConfig> => {
    const response = await api.patch<ApiResponse<SystemConfig>>('/admin/dashboard/config', config);
    return response.data.data;
  },

  // Get recent activity
  getRecentActivity: async (limit: number = 10): Promise<Array<{
    id: string;
    type: 'user' | 'bot' | 'project' | 'organization' | 'transcription' | 'webhook';
    action: string;
    description: string;
    timestamp: string;
    metadata?: Record<string, any>;
  }>> => {
    const response = await api.get<ApiResponse<any[]>>('/admin/dashboard/activity', {
      params: { limit }
    });
    return response.data.data;
  },

  // Get system health check
  getHealthCheck: async (): Promise<{
    status: 'healthy' | 'warning' | 'critical';
    services: Record<string, {
      status: 'up' | 'down' | 'degraded';
      response_time_ms?: number;
      last_check: string;
    }>;
    uptime_seconds: number;
  }> => {
    const response = await api.get<ApiResponse<any>>('/admin/dashboard/health');
    return response.data.data;
  }
}; 