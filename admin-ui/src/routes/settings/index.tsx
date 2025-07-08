import { component$ } from '@builder.io/qwik';
import { Card, CardHeader, CardBody, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { FaIcon } from '../../components/ui/fa-icon';
import { 
  faCog, 
  faMicrophone, 
  faDatabase, 
  faCheck 
} from '@fortawesome/free-solid-svg-icons';
import { StatusBadge } from '../../components/ui/table';

export default component$(() => {
  // Mock data - trong thực tế sẽ fetch từ API
  const systemConfig = {
    maxBotsPerProject: 10,
    defaultCredits: 500,
    enableWebhooks: true,
    autoCleanupBots: true
  };

  const transcriptionProviders = [
    {
      name: 'Deepgram',
      description: 'Real-time speech recognition',
      enabled: true,
      status: 'connected'
    },
    {
      name: 'Google Speech-to-Text',
      description: 'Google Cloud speech recognition',
      enabled: false,
      status: 'disconnected'
    },
    {
      name: 'AWS Transcribe',
      description: 'Amazon speech recognition service',
      enabled: false,
      status: 'disconnected'
    },
    {
      name: 'Azure Speech Services',
      description: 'Microsoft speech recognition',
      enabled: false,
      status: 'disconnected'
    }
  ];

  const databaseInfo = {
    status: 'connected',
    type: 'PostgreSQL',
    version: '15.2',
    poolSize: 20,
    activeConnections: 5
  };

  const cacheInfo = {
    redisStatus: 'online',
    memoryUsage: '156 MB',
    totalKeys: 1234,
    activeWorkers: 3,
    pendingTasks: 7,
    processedToday: 1456
  };

  return (
    <div class="space-y-6">
      {/* Header */}
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">System Settings</h1>
          <p class="text-gray-600 mt-1">Configure system parameters and integrations</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Configuration */}
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <FaIcon icon={faCog} class="h-5 w-5" />
              System Configuration
            </CardTitle>
          </CardHeader>
          <CardBody class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Max Bots per Project
              </label>
              <input
                type="number"
                value={systemConfig.maxBotsPerProject}
                min="1"
                max="100"
                class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <p class="text-xs text-gray-500 mt-1">
                Maximum number of concurrent bots allowed per project.
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Default Credits for New Organizations
              </label>
              <input
                type="number"
                value={systemConfig.defaultCredits}
                min="0"
                step="100"
                class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <p class="text-xs text-gray-500 mt-1">
                Credits automatically assigned to new organizations (in centicredits).
              </p>
            </div>

            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-sm">Enable Webhooks</div>
                  <div class="text-xs text-gray-500">Allow organizations to configure webhook subscriptions.</div>
                </div>
                <input
                  type="checkbox"
                  checked={systemConfig.enableWebhooks}
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>

              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-sm">Auto Cleanup Completed Bots</div>
                  <div class="text-xs text-gray-500">Automatically remove bot pods after meetings end.</div>
                </div>
                <input
                  type="checkbox"
                  checked={systemConfig.autoCleanupBots}
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>
            </div>

            <div class="pt-4">
              <Button>
                <FaIcon icon={faCheck} class="h-4 w-4 mr-2" />
                Save Configuration
              </Button>
            </div>
          </CardBody>
        </Card>

        {/* Transcription Providers */}
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <FaIcon icon={faMicrophone} class="h-5 w-5" />
              Transcription Providers
            </CardTitle>
          </CardHeader>
          <CardBody>
            <div class="space-y-3">
              {transcriptionProviders.map((provider) => (
                <div key={provider.name} class="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div>
                    <div class="font-semibold text-sm">{provider.name}</div>
                    <div class="text-xs text-gray-500">{provider.description}</div>
                  </div>
                  <div class="flex items-center gap-2">
                    <StatusBadge 
                      status={provider.enabled ? 'Enabled' : 'Disabled'} 
                      variant={provider.enabled ? 'success' : 'secondary'} 
                    />
                    <Button size="sm" variant="outline">Configure</Button>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Database Information */}
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <FaIcon icon={faDatabase} class="h-5 w-5" />
              Database Information
            </CardTitle>
          </CardHeader>
          <CardBody>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="font-medium">Connection Status:</span>
                <StatusBadge status="Connected" variant="success" />
              </div>
              <div class="flex justify-between">
                <span class="font-medium">Database Type:</span>
                <span>{databaseInfo.type}</span>
              </div>
              <div class="flex justify-between">
                <span class="font-medium">Version:</span>
                <span>{databaseInfo.version}</span>
              </div>
              <div class="flex justify-between">
                <span class="font-medium">Pool Size:</span>
                <span>{databaseInfo.poolSize} connections</span>
              </div>
              <div class="flex justify-between">
                <span class="font-medium">Active Connections:</span>
                <span>{databaseInfo.activeConnections}</span>
              </div>
            </div>

            <div class="pt-4 space-y-2">
              <Button variant="outline" class="w-full">
                Test Connection
              </Button>
              <Button variant="outline" class="w-full">
                View Migrations
              </Button>
            </div>
          </CardBody>
        </Card>

        {/* Cache & Queue Status */}
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <FaIcon icon={faCog} class="h-5 w-5" />
              Cache & Queue Status
            </CardTitle>
          </CardHeader>
          <CardBody>
            <div class="space-y-4">
              <div>
                <h4 class="font-semibold text-sm mb-2">Redis Cache</h4>
                <div class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <span class="font-medium">Status:</span>
                    <StatusBadge status="Online" variant="success" />
                  </div>
                  <div class="flex justify-between">
                    <span class="font-medium">Memory Usage:</span>
                    <span>{cacheInfo.memoryUsage}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="font-medium">Keys:</span>
                    <span>{cacheInfo.totalKeys.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 class="font-semibold text-sm mb-2">Celery Workers</h4>
                <div class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <span class="font-medium">Active Workers:</span>
                    <span>{cacheInfo.activeWorkers}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="font-medium">Pending Tasks:</span>
                    <span>{cacheInfo.pendingTasks}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="font-medium">Processed Today:</span>
                    <span>{cacheInfo.processedToday.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}); 