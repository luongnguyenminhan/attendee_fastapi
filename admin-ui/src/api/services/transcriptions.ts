import { api } from '../client';
import type {
  Transcription,
  TranscriptionStats,
  PaginatedResponse,
  PaginationParams,
  ApiResponse
} from '../types';

export const transcriptionsApi = {
  // Get all transcriptions với pagination và filtering
  getTranscriptions: async (params?: PaginationParams & {
    status?: 'queued' | 'processing' | 'completed' | 'failed';
    provider?: 'deepgram' | 'google' | 'aws' | 'azure';
    bot_id?: string;
    project_id?: string;
  }): Promise<PaginatedResponse<Transcription>> => {
    const response = await api.get<PaginatedResponse<Transcription>>('/admin/transcriptions', { params });
    return response.data;
  },

  // Get transcription by ID
  getTranscription: async (transcriptionId: string): Promise<Transcription> => {
    const response = await api.get<ApiResponse<Transcription>>(`/admin/transcriptions/${transcriptionId}`);
    return response.data.data;
  },

  // Delete transcription
  deleteTranscription: async (transcriptionId: string): Promise<void> => {
    await api.delete(`/admin/transcriptions/${transcriptionId}`);
  },

  // Retry failed transcription
  retryTranscription: async (transcriptionId: string): Promise<Transcription> => {
    const response = await api.post<ApiResponse<Transcription>>(`/admin/transcriptions/${transcriptionId}/retry`);
    return response.data.data;
  },

  // Download transcription content
  downloadTranscription: async (transcriptionId: string, format: 'txt' | 'srt' | 'vtt' | 'json' = 'txt'): Promise<Blob> => {
    const response = await api.get(`/admin/transcriptions/${transcriptionId}/download`, {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  },

  // Get transcription content (raw text)
  getTranscriptionContent: async (transcriptionId: string): Promise<{
    content: string;
    word_count: number;
    duration_seconds: number;
    language: string;
    confidence_score?: number;
  }> => {
    const response = await api.get<ApiResponse<any>>(`/admin/transcriptions/${transcriptionId}/content`);
    return response.data.data;
  },

  // Get transcription with timestamps
  getTranscriptionWithTimestamps: async (transcriptionId: string): Promise<{
    segments: Array<{
      start_time: number;
      end_time: number;
      text: string;
      confidence?: number;
      speaker_id?: string;
    }>;
    metadata: {
      total_duration: number;
      word_count: number;
      language: string;
      provider: string;
    };
  }> => {
    const response = await api.get<ApiResponse<any>>(`/admin/transcriptions/${transcriptionId}/timestamps`);
    return response.data.data;
  },

  // Get transcription statistics
  getTranscriptionStats: async (): Promise<TranscriptionStats> => {
    const response = await api.get<ApiResponse<TranscriptionStats>>('/admin/transcriptions/stats');
    return response.data.data;
  },

  // Get provider statistics
  getProviderStats: async (): Promise<Record<string, {
    total_transcriptions: number;
    success_rate: number;
    avg_processing_time: number;
    total_duration_hours: number;
  }>> => {
    const response = await api.get<ApiResponse<any>>('/admin/transcriptions/provider-stats');
    return response.data.data;
  },

  // Search transcriptions by content
  searchTranscriptions: async (query: string, params?: {
    bot_id?: string;
    project_id?: string;
    date_from?: string;
    date_to?: string;
  }): Promise<Array<{
    transcription_id: string;
    bot_name?: string;
    project_name?: string;
    matches: Array<{
      text: string;
      start_time?: number;
      end_time?: number;
      confidence?: number;
    }>;
    created_at: string;
  }>> => {
    const response = await api.get<ApiResponse<any[]>>('/admin/transcriptions/search', {
      params: { q: query, ...params }
    });
    return response.data.data;
  },

  // Get transcription processing queue status
  getQueueStatus: async (): Promise<{
    queued_count: number;
    processing_count: number;
    estimated_wait_time_minutes: number;
    active_workers: number;
    providers_status: Record<string, {
      status: 'online' | 'offline' | 'degraded';
      queue_length: number;
      avg_processing_time: number;
    }>;
  }> => {
    const response = await api.get<ApiResponse<any>>('/admin/transcriptions/queue-status');
    return response.data.data;
  },

  // Manually trigger transcription processing
  processTranscription: async (transcriptionId: string, provider?: 'deepgram' | 'google' | 'aws' | 'azure'): Promise<Transcription> => {
    const response = await api.post<ApiResponse<Transcription>>(`/admin/transcriptions/${transcriptionId}/process`, {
      provider
    });
    return response.data.data;
  }
}; 