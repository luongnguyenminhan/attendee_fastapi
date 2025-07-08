import { component$ } from '@builder.io/qwik';
import { Card, CardHeader, CardBody, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { FaIcon } from '../../components/ui/fa-icon';
import { faBell, faClock } from '@fortawesome/free-solid-svg-icons';
import { 
  Table, 
  TableHeader, 
  TableBody, 
  TableRow, 
  TableHead, 
  TableCell, 
  StatusBadge, 
  EmptyState 
} from '../../components/ui/table';


export default component$(() => {
  const webhookStats = {
    totalSubscriptions: 24,
    successfulDeliveries: 1892,
    failedDeliveries: 12,
    pendingDeliveries: 3
  };

  const webhookSubscriptions = [
    {
      id: 'sub_123456',
      url: 'https://api.example.com/webhooks/attendee',
      project: { name: 'Enterprise CRM' },
      events: ['bot.started', 'bot.ended', 'transcription.completed'],
      isActive: true,
      lastDelivery: '2024-01-15T10:30:00Z'
    },
    {
      id: 'sub_789012',
      url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX',
      project: { name: 'Customer Analytics' },
      events: ['bot.error'],
      isActive: true,
      lastDelivery: '2024-01-14T15:20:00Z'
    },
    {
      id: 'sub_345678',
      url: 'https://webhook.site/unique-uuid-here',
      project: { name: 'Online Learning' },
      events: ['transcription.completed'],
      isActive: false,
      lastDelivery: null
    }
  ];

  const webhookDeliveries = [
    {
      id: 'del_123456',
      url: 'https://api.example.com/webhooks/attendee',
      event: 'bot.ended',
      status: 'success',
      responseCode: 200,
      attempts: 1,
      timestamp: '2024-01-15T10:30:00Z'
    },
    {
      id: 'del_789012',
      url: 'https://hooks.slack.com/services/...',
      event: 'bot.error',
      status: 'failed',
      responseCode: 500,
      attempts: 3,
      timestamp: '2024-01-15T10:25:00Z'
    }
  ];

  return (
    <div class="space-y-6">
      {/* Header */}
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Webhooks Management</h1>
          <p class="text-gray-600 mt-1">Monitor webhook subscriptions and delivery status</p>
        </div>
        <Button variant="secondary">
          <FaIcon icon={faClock} class="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats Cards */}
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardBody class="text-center">
            <div class="text-3xl font-bold text-blue-600">{webhookStats.totalSubscriptions}</div>
            <div class="text-sm text-gray-600">Total Subscriptions</div>
          </CardBody>
        </Card>
        <Card>
          <CardBody class="text-center">
            <div class="text-3xl font-bold text-green-600">{webhookStats.successfulDeliveries}</div>
            <div class="text-sm text-gray-600">Successful Deliveries</div>
          </CardBody>
        </Card>
        <Card>
          <CardBody class="text-center">
            <div class="text-3xl font-bold text-red-600">{webhookStats.failedDeliveries}</div>
            <div class="text-sm text-gray-600">Failed Deliveries</div>
          </CardBody>
        </Card>
        <Card>
          <CardBody class="text-center">
            <div class="text-3xl font-bold text-yellow-600">{webhookStats.pendingDeliveries}</div>
            <div class="text-sm text-gray-600">Pending Deliveries</div>
          </CardBody>
        </Card>
      </div>

      {/* Webhook Subscriptions */}
      <Card>
        <CardHeader>
          <div class="flex justify-between items-center">
            <CardTitle class="flex items-center gap-2">
              <FaIcon icon={faBell} class="h-5 w-5" />
              Active Webhook Subscriptions
            </CardTitle>
            <Button>
              <FaIcon icon={faBell} class="h-4 w-4 mr-2" />
              Add Subscription
            </Button>
          </div>
        </CardHeader>
        <CardBody class="p-0">
          {webhookSubscriptions.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>URL</TableHead>
                  <TableHead>Project</TableHead>
                  <TableHead>Events</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Delivery</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {webhookSubscriptions.map((subscription) => (
                  <TableRow key={subscription.id}>
                    <TableCell>
                      <code class="text-xs bg-gray-100 px-2 py-1 rounded">{subscription.id}</code>
                    </TableCell>
                    <TableCell>
                      <a 
                        href={subscription.url} 
                        target="_blank" 
                        class="text-blue-600 hover:text-blue-800 text-sm"
                        title={subscription.url}
                      >
                        {subscription.url.length > 40 ? 
                          `${subscription.url.slice(0, 40)}...` : 
                          subscription.url
                        }
                      </a>
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={subscription.project.name} variant="info" />
                    </TableCell>
                    <TableCell>
                      <div class="flex flex-wrap gap-1">
                        {subscription.events.map((event) => (
                          <StatusBadge key={event} status={event} variant="secondary" />
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      <StatusBadge 
                        status={subscription.isActive ? 'Active' : 'Inactive'} 
                        variant={subscription.isActive ? 'success' : 'danger'} 
                      />
                    </TableCell>
                    <TableCell class="text-gray-500 text-xs">
                      {subscription.lastDelivery 
                        ? new Date(subscription.lastDelivery).toLocaleDateString()
                        : 'Never'
                      }
                    </TableCell>
                    <TableCell>
                      <div class="flex gap-1">
                        <Button size="sm" variant="outline">View</Button>
                        <Button size="sm" variant="outline">Test</Button>
                        <Button size="sm" variant="outline">Edit</Button>
                        <Button size="sm" variant="outline">Delete</Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <EmptyState
              icon={<FaIcon icon={faBell} />}
              title="No webhook subscriptions"
              description="There are no webhook subscriptions configured yet."
              action={<Button>Create First Subscription</Button>}
            />
          )}
        </CardBody>
      </Card>

      {/* Recent Webhook Deliveries */}
      <Card>
        <CardHeader>
          <div class="flex justify-between items-center">
            <CardTitle class="flex items-center gap-2">
              <FaIcon icon={faClock} class="h-5 w-5" />
              Recent Webhook Deliveries
            </CardTitle>
            <div class="flex gap-2">
              <Button size="sm" variant="outline">All</Button>
              <Button size="sm" variant="outline">Success</Button>
              <Button size="sm" variant="outline">Failed</Button>
              <Button size="sm" variant="outline">Pending</Button>
            </div>
          </div>
        </CardHeader>
        <CardBody class="p-0">
          {webhookDeliveries.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>URL</TableHead>
                  <TableHead>Event</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Response Code</TableHead>
                  <TableHead>Attempts</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {webhookDeliveries.map((delivery) => (
                  <TableRow key={delivery.id}>
                    <TableCell>
                      <code class="text-xs bg-gray-100 px-2 py-1 rounded">{delivery.id}</code>
                    </TableCell>
                    <TableCell class="text-sm">
                      {delivery.url.length > 30 ? `${delivery.url.slice(0, 30)}...` : delivery.url}
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={delivery.event} variant="secondary" />
                    </TableCell>
                    <TableCell>
                      <StatusBadge 
                        status={delivery.status === 'success' ? 'Success' : 'Failed'} 
                        variant={delivery.status === 'success' ? 'success' : 'danger'} 
                      />
                    </TableCell>
                    <TableCell>
                      <span class={`px-2 py-1 rounded text-xs ${
                        delivery.responseCode >= 200 && delivery.responseCode < 300 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {delivery.responseCode}
                      </span>
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={`${delivery.attempts} attempt${delivery.attempts > 1 ? 's' : ''}`} variant="info" />
                    </TableCell>
                    <TableCell class="text-gray-500 text-xs">
                      {new Date(delivery.timestamp).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <div class="flex gap-1">
                        <Button size="sm" variant="outline">View</Button>
                        {delivery.status === 'failed' && (
                          <Button size="sm" variant="outline">Retry</Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <EmptyState
              icon={<FaIcon icon={faClock} />}
              title="No webhook deliveries"
              description="There are no webhook delivery attempts yet."
              action={<Button>View All Deliveries</Button>}
            />
          )}
        </CardBody>
      </Card>
    </div>
  );
}); 