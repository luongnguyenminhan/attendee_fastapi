// Export API client
export { apiClient, api } from './client';

// Export types
export type * from './types';

// Import services
import { usersApi } from './services/users';
import { organizationsApi } from './services/organizations';
import { projectsApi } from './services/projects';
import { botsApi } from './services/bots';
import { transcriptionsApi } from './services/transcriptions';
import { webhooksApi } from './services/webhooks';
import { dashboardApi } from './services/dashboard';
import { authApi } from './services/auth';

// Export all services
export { usersApi, organizationsApi, projectsApi, botsApi, transcriptionsApi, webhooksApi, dashboardApi, authApi };

// Export combined API object
export const adminApi = {
  auth: authApi,
  users: usersApi,
  organizations: organizationsApi,
  projects: projectsApi,
  bots: botsApi,
  transcriptions: transcriptionsApi,
  webhooks: webhooksApi,
  dashboard: dashboardApi,
} as const;

export default adminApi; 