import { api } from '../client';
import type {
  WebhookSubscription,
  WebhookDelivery,
  WebhookStats,
  CreateWebhookRequest,
  UpdateWebhookRequest,
  PaginatedResponse,
  PaginationParams,
  ApiResponse
} from '../types';

export const webhooksApi = {
  // Get all webhook subscriptions
  getWebhookSubscriptions: async (params?: PaginationParams & {
    project_id?: string;
    is_active?: boolean;
  }): Promise<PaginatedResponse<WebhookSubscription>> => {
    const response = await api.get<PaginatedResponse<WebhookSubscription>>('/admin/webhooks/subscriptions', { params });
    return response.data;
  },

  // Get webhook subscription by ID
  getWebhookSubscription: async (subscriptionId: string): Promise<WebhookSubscription> => {
    const response = await api.get<ApiResponse<WebhookSubscription>>(`/admin/webhooks/subscriptions/${subscriptionId}`);
    return response.data.data;
  },

  // Create new webhook subscription
  createWebhookSubscription: async (webhookData: CreateWebhookRequest): Promise<WebhookSubscription> => {
    const response = await api.post<ApiResponse<WebhookSubscription>>('/admin/webhooks/subscriptions', webhookData);
    return response.data.data;
  },

  // Update webhook subscription
  updateWebhookSubscription: async (subscriptionId: string, webhookData: UpdateWebhookRequest): Promise<WebhookSubscription> => {
    const response = await api.patch<ApiResponse<WebhookSubscription>>(`/admin/webhooks/subscriptions/${subscriptionId}`, webhookData);
    return response.data.data;
  },

  // Delete webhook subscription
  deleteWebhookSubscription: async (subscriptionId: string): Promise<void> => {
    await api.delete(`/admin/webhooks/subscriptions/${subscriptionId}`);
  },

  // Toggle webhook subscription status
  toggleWebhookSubscription: async (subscriptionId: string): Promise<WebhookSubscription> => {
    const response = await api.patch<ApiResponse<WebhookSubscription>>(`/admin/webhooks/subscriptions/${subscriptionId}/toggle`);
    return response.data.data;
  },

  // Test webhook subscription
  testWebhookSubscription: async (subscriptionId: string): Promise<{
    success: boolean;
    response_code?: number;
    response_body?: string;
    response_time_ms?: number;
    error?: string;
  }> => {
    const response = await api.post<ApiResponse<any>>(`/admin/webhooks/subscriptions/${subscriptionId}/test`);
    return response.data.data;
  },

  // Webhook Deliveries

  // Get all webhook deliveries
  getWebhookDeliveries: async (params?: PaginationParams & {
    subscription_id?: string;
    status?: 'success' | 'failed' | 'pending';
    event?: string;
  }): Promise<PaginatedResponse<WebhookDelivery>> => {
    const response = await api.get<PaginatedResponse<WebhookDelivery>>('/admin/webhooks/deliveries', { params });
    return response.data;
  },

  // Get webhook delivery by ID
  getWebhookDelivery: async (deliveryId: string): Promise<WebhookDelivery> => {
    const response = await api.get<ApiResponse<WebhookDelivery>>(`/admin/webhooks/deliveries/${deliveryId}`);
    return response.data.data;
  },

  // Retry failed webhook delivery
  retryWebhookDelivery: async (deliveryId: string): Promise<WebhookDelivery> => {
    const response = await api.post<ApiResponse<WebhookDelivery>>(`/admin/webhooks/deliveries/${deliveryId}/retry`);
    return response.data.data;
  },

  // Get webhook delivery details with full payload
  getWebhookDeliveryDetails: async (deliveryId: string): Promise<{
    delivery: WebhookDelivery;
    request_headers: Record<string, string>;
    request_payload: Record<string, any>;
    response_headers?: Record<string, string>;
    response_body?: string;
    error_details?: string;
  }> => {
    const response = await api.get<ApiResponse<any>>(`/admin/webhooks/deliveries/${deliveryId}/details`);
    return response.data.data;
  },

  // Statistics and Analytics

  // Get webhook statistics
  getWebhookStats: async (): Promise<WebhookStats> => {
    const response = await api.get<ApiResponse<WebhookStats>>('/admin/webhooks/stats');
    return response.data.data;
  },

  // Get delivery success rate by subscription
  getDeliverySuccessRate: async (subscriptionId?: string): Promise<{
    success_rate: number;
    total_deliveries: number;
    successful_deliveries: number;
    failed_deliveries: number;
    avg_response_time_ms: number;
    last_24h_stats: {
      deliveries: number;
      success_rate: number;
    };
  }> => {
    const params = subscriptionId ? { subscription_id: subscriptionId } : {};
    const response = await api.get<ApiResponse<any>>('/admin/webhooks/success-rate', { params });
    return response.data.data;
  },

  // Get webhook events analytics
  getWebhookEventAnalytics: async (params?: {
    date_from?: string;
    date_to?: string;
    project_id?: string;
  }): Promise<{
    events_by_type: Record<string, number>;
    deliveries_by_day: Array<{
      date: string;
      successful: number;
      failed: number;
    }>;
    top_failing_endpoints: Array<{
      url: string;
      failure_rate: number;
      total_attempts: number;
    }>;
  }> => {
    const response = await api.get<ApiResponse<any>>('/admin/webhooks/analytics', { params });
    return response.data.data;
  },

  // Configuration and Management

  // Get available webhook events
  getAvailableEvents: async (): Promise<Array<{
    event_type: string;
    description: string;
    payload_schema: Record<string, any>;
  }>> => {
    const response = await api.get<ApiResponse<any[]>>('/admin/webhooks/events');
    return response.data.data;
  },

  // Validate webhook URL
  validateWebhookUrl: async (url: string): Promise<{
    valid: boolean;
    reachable: boolean;
    response_time_ms?: number;
    error?: string;
  }> => {
    const response = await api.post<ApiResponse<any>>('/admin/webhooks/validate-url', { url });
    return response.data.data;
  },

  // Get webhook delivery logs for debugging
  getWebhookLogs: async (params?: {
    subscription_id?: string;
    level?: 'debug' | 'info' | 'warning' | 'error';
    limit?: number;
    offset?: number;
  }): Promise<{
    logs: Array<{
      timestamp: string;
      level: string;
      message: string;
      subscription_id?: string;
      delivery_id?: string;
      metadata?: Record<string, any>;
    }>;
    total: number;
  }> => {
    const response = await api.get<ApiResponse<any>>('/admin/webhooks/logs', { params });
    return response.data.data;
  }
}; 