// Common API response types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// User types
export interface User {
  id: string;
  email: string;
  name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
  organization_id?: string;
  organization?: Organization;
}

export interface CreateUserRequest {
  email: string;
  name?: string;
  password: string;
  is_active?: boolean;
  organization_id?: string;
}

export interface UpdateUserRequest {
  name?: string;
  is_active?: boolean;
  organization_id?: string;
}

// Organization types
export interface Organization {
  id: string;
  name: string;
  status: 'active' | 'suspended' | 'inactive';
  centicredits: number;
  is_webhooks_enabled: boolean;
  created_at: string;
  updated_at: string;
  version?: string;
}

export interface CreateOrganizationRequest {
  name: string;
  centicredits?: number;
  is_webhooks_enabled?: boolean;
}

export interface UpdateOrganizationRequest {
  name?: string;
  status?: 'active' | 'suspended' | 'inactive';
  centicredits?: number;
  is_webhooks_enabled?: boolean;
}

// Project types
export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'archived';
  organization_id: string;
  organization?: Organization;
  created_at: string;
  updated_at: string;
  api_keys?: ApiKey[];
}

export interface ApiKey {
  id: string;
  name: string;
  key_hash: string;
  created_at: string;
  last_used_at?: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  organization_id: string;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: 'active' | 'archived';
}

// Bot types
export interface Bot {
  id: string;
  name?: string;
  description?: string;
  project_id?: string;
  project?: Project;
  platform?: 'zoom' | 'google_meet' | 'teams' | 'web';
  status: 'starting' | 'in_meeting' | 'ended' | 'error';
  meeting_url?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CreateBotRequest {
  name?: string;
  description?: string;
  project_id?: string;
  platform?: 'zoom' | 'google_meet' | 'teams' | 'web';
  meeting_url?: string;
  metadata?: Record<string, any>;
}

export interface UpdateBotRequest {
  name?: string;
  description?: string;
  status?: 'starting' | 'in_meeting' | 'ended' | 'error';
  metadata?: Record<string, any>;
}

// Transcription types
export interface Transcription {
  id: string;
  bot_id?: string;
  bot?: Bot;
  provider: 'deepgram' | 'google' | 'aws' | 'azure';
  status: 'queued' | 'processing' | 'completed' | 'failed';
  duration_seconds?: number;
  word_count?: number;
  language?: string;
  content?: string;
  created_at: string;
  updated_at: string;
}

export interface TranscriptionStats {
  total_transcriptions: number;
  processing: number;
  completed: number;
  failed: number;
}

// Webhook types
export interface WebhookSubscription {
  id: string;
  url: string;
  project_id?: string;
  project?: Project;
  events: string[];
  is_active: boolean;
  secret?: string;
  last_delivery?: string;
  created_at: string;
  updated_at: string;
}

export interface WebhookDelivery {
  id: string;
  subscription_id: string;
  url: string;
  event: string;
  status: 'success' | 'failed' | 'pending';
  response_code?: number;
  attempts: number;
  payload?: Record<string, any>;
  response_body?: string;
  timestamp: string;
}

export interface WebhookStats {
  total_subscriptions: number;
  successful_deliveries: number;
  failed_deliveries: number;
  pending_deliveries: number;
}

export interface CreateWebhookRequest {
  url: string;
  project_id?: string;
  events: string[];
  secret?: string;
  is_active?: boolean;
}

export interface UpdateWebhookRequest {
  url?: string;
  events?: string[];
  is_active?: boolean;
  secret?: string;
}

// System types
export interface SystemStats {
  total_users: number;
  total_organizations: number;
  total_projects: number;
  total_bots: number;
  active_bots: number;
  total_transcriptions: number;
  system_health: 'healthy' | 'warning' | 'critical';
}

export interface SystemConfig {
  max_bots_per_project: number;
  default_credits: number;
  enable_webhooks: boolean;
  auto_cleanup_bots: boolean;
}

// Error types
export interface ApiError {
  detail: string;
  status_code: number;
  timestamp: string;
}

export interface ValidationError {
  field: string;
  message: string;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

 