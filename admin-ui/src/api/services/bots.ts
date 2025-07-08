import { api } from '../client';
import type {
  Bot,
  CreateBotRequest,
  UpdateBotRequest,
  PaginatedResponse,
  PaginationParams,
  ApiResponse
} from '../types';

export const botsApi = {
  // Get all bots với pagination và filtering
  getBots: async (params?: PaginationParams & {
    status?: 'starting' | 'in_meeting' | 'ended' | 'error';
    platform?: 'zoom' | 'google_meet' | 'teams' | 'web';
    project_id?: string;
  }): Promise<PaginatedResponse<Bot>> => {
    const response = await api.get<PaginatedResponse<Bot>>('/admin/bots', { params });
    return response.data;
  },

  // Get bot by ID
  getBot: async (botId: string): Promise<Bot> => {
    const response = await api.get<ApiResponse<Bot>>(`/admin/bots/${botId}`);
    return response.data.data;
  },

  // Create new bot
  createBot: async (botData: CreateBotRequest): Promise<Bot> => {
    const response = await api.post<ApiResponse<Bot>>('/admin/bots', botData);
    return response.data.data;
  },

  // Update bot
  updateBot: async (botId: string, botData: UpdateBotRequest): Promise<Bot> => {
    const response = await api.patch<ApiResponse<Bot>>(`/admin/bots/${botId}`, botData);
    return response.data.data;
  },

  // Delete bot
  deleteBot: async (botId: string): Promise<void> => {
    await api.delete(`/admin/bots/${botId}`);
  },

  // Stop bot (if running)
  stopBot: async (botId: string): Promise<Bot> => {
    const response = await api.post<ApiResponse<Bot>>(`/admin/bots/${botId}/stop`);
    return response.data.data;
  },

  // Restart bot
  restartBot: async (botId: string): Promise<Bot> => {
    const response = await api.post<ApiResponse<Bot>>(`/admin/bots/${botId}/restart`);
    return response.data.data;
  },

  // Get bot logs
  getBotLogs: async (botId: string, params?: {
    limit?: number;
    offset?: number;
    level?: 'debug' | 'info' | 'warning' | 'error';
  }): Promise<{
    logs: Array<{
      timestamp: string;
      level: string;
      message: string;
      metadata?: Record<string, any>;
    }>;
    total: number;
  }> => {
    const response = await api.get<ApiResponse<any>>(`/admin/bots/${botId}/logs`, { params });
    return response.data.data;
  },

  // Get bot events
  getBotEvents: async (botId: string): Promise<Array<{
    id: string;
    event_type: string;
    event_subtype?: string;
    timestamp: string;
    data?: Record<string, any>;
  }>> => {
    const response = await api.get<ApiResponse<any[]>>(`/admin/bots/${botId}/events`);
    return response.data.data;
  },

  // Get bot recordings/media
  getBotMedia: async (botId: string): Promise<Array<{
    id: string;
    type: 'audio' | 'video' | 'screen';
    url: string;
    duration?: number;
    size?: number;
    created_at: string;
  }>> => {
    const response = await api.get<ApiResponse<any[]>>(`/admin/bots/${botId}/media`);
    return response.data.data;
  },

  // Get bot statistics
  getBotStats: async (): Promise<{
    total_bots: number;
    active_bots: number;
    starting_bots: number;
    ended_bots: number;
    error_bots: number;
    platform_distribution: Record<string, number>;
  }> => {
    const response = await api.get<ApiResponse<any>>('/admin/bots/stats');
    return response.data.data;
  },

  // Send command to bot
  sendCommand: async (botId: string, command: {
    type: 'mute' | 'unmute' | 'start_recording' | 'stop_recording' | 'leave_meeting';
    params?: Record<string, any>;
  }): Promise<{ success: boolean; message?: string }> => {
    const response = await api.post<ApiResponse<any>>(`/admin/bots/${botId}/command`, command);
    return response.data.data;
  },

  // Get real-time bot status
  getBotStatus: async (botId: string): Promise<{
    status: string;
    health: 'healthy' | 'warning' | 'critical';
    last_heartbeat?: string;
    current_activity?: string;
    resource_usage?: {
      cpu_percent: number;
      memory_mb: number;
      network_mb: number;
    };
  }> => {
    const response = await api.get<ApiResponse<any>>(`/admin/bots/${botId}/status`);
    return response.data.data;
  }
}; 