import { component$ } from '@builder.io/qwik';
import { Card, CardHeader, CardBody, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { FaIcon } from '../../components/ui/fa-icon';
import { 
  faMicrophone, 
  faRobot, 
  faClock, 
  faCheck, 
  faXmark 
} from '@fortawesome/free-solid-svg-icons';
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
  // Mock data - trong thực tế sẽ fetch từ API
  const transcriptionStats = {
    totalTranscriptions: 1542,
    processing: 8,
    completed: 1498,
    failed: 36
  };

  const transcriptions = [
    {
      id: 'trans_123456',
      bot: {
        name: 'Sales Team Bot',
        project: { name: 'Enterprise CRM' }
      },
      provider: 'deepgram',
      status: 'completed',
      durationSeconds: 3600, // 1 hour
      wordCount: 8450,
      language: 'en',
      createdAt: '2024-01-15T10:30:00Z'
    },
    {
      id: 'trans_789012',
      bot: {
        name: 'Support Bot',
        project: { name: 'Customer Analytics' }
      },
      provider: 'google',
      status: 'processing',
      durationSeconds: 1800, // 30 minutes
      wordCount: null,
      language: 'en',
      createdAt: '2024-01-15T11:15:00Z'
    },
    {
      id: 'trans_345678',
      bot: {
        name: 'Education Bot',
        project: { name: 'Online Learning' }
      },
      provider: 'aws',
      status: 'failed',
      durationSeconds: 2400, // 40 minutes
      wordCount: null,
      language: 'en',
      createdAt: '2024-01-15T09:45:00Z'
    },
    {
      id: 'trans_901234',
      bot: {
        name: 'Meeting Bot',
        project: { name: 'Team Collaboration' }
      },
      provider: 'deepgram',
      status: 'queued',
      durationSeconds: null,
      wordCount: null,
      language: 'auto',
      createdAt: '2024-01-15T12:00:00Z'
    }
  ];

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return '-';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const providerBadge = (provider: string) => {
    switch (provider) {
      case 'deepgram':
        return <StatusBadge status="Deepgram" variant="info" />;
      case 'google':
        return <StatusBadge status="Google" variant="success" />;
      case 'aws':
        return <StatusBadge status="AWS" variant="warning" />;
      case 'azure':
        return <StatusBadge status="Azure" variant="secondary" />;
      default:
        return <StatusBadge status={provider} variant="secondary" />;
    }
  };

  const statusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <StatusBadge status="Completed" variant="success">
            <FaIcon icon={faCheck} class="h-3 w-3 mr-1" />
          </StatusBadge>
        );
      case 'processing':
        return (
          <StatusBadge status="Processing" variant="warning">
            <FaIcon icon={faClock} class="h-3 w-3 mr-1" />
          </StatusBadge>
        );
      case 'failed':
        return (
          <StatusBadge status="Failed" variant="danger">
            <FaIcon icon={faXmark} class="h-3 w-3 mr-1" />
          </StatusBadge>
        );
      case 'queued':
        return (
          <StatusBadge status="Queued" variant="info">
            <FaIcon icon={faClock} class="h-3 w-3 mr-1" />
          </StatusBadge>
        );
      default:
        return <StatusBadge status={status} variant="secondary" />;
    }
  };

  return (
    <div class="space-y-6">
      {/* Header */}
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Transcriptions Management</h1>
          <p class="text-gray-600 mt-1">Monitor transcription jobs and processing status</p>
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
            <div class="text-3xl font-bold text-blue-600">{transcriptionStats.totalTranscriptions}</div>
            <div class="text-sm text-gray-600">Total Transcriptions</div>
          </CardBody>
        </Card>
        <Card>
          <CardBody class="text-center">
            <div class="text-3xl font-bold text-yellow-600">{transcriptionStats.processing}</div>
            <div class="text-sm text-gray-600">Processing</div>
          </CardBody>
        </Card>
        <Card>
          <CardBody class="text-center">
            <div class="text-3xl font-bold text-green-600">{transcriptionStats.completed}</div>
            <div class="text-sm text-gray-600">Completed</div>
          </CardBody>
        </Card>
        <Card>
          <CardBody class="text-center">
            <div class="text-3xl font-bold text-red-600">{transcriptionStats.failed}</div>
            <div class="text-sm text-gray-600">Failed</div>
          </CardBody>
        </Card>
      </div>

      {/* Transcription Jobs */}
      <Card>
        <CardHeader>
          <div class="flex justify-between items-center">
            <CardTitle class="flex items-center gap-2">
              <FaIcon icon={faMicrophone} class="h-5 w-5" />
              Recent Transcription Jobs
            </CardTitle>
            <div class="flex gap-2">
              <Button size="sm" variant="outline">All</Button>
              <Button size="sm" variant="outline">Processing</Button>
              <Button size="sm" variant="outline">Completed</Button>
              <Button size="sm" variant="outline">Failed</Button>
            </div>
          </div>
        </CardHeader>
        <CardBody class="p-0">
          {transcriptions.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Bot</TableHead>
                  <TableHead>Provider</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Words</TableHead>
                  <TableHead>Language</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {transcriptions.map((transcription) => (
                  <TableRow key={transcription.id}>
                    <TableCell>
                      <code class="text-xs bg-gray-100 px-2 py-1 rounded">{transcription.id}</code>
                    </TableCell>
                    <TableCell>
                      <div class="flex items-center gap-3">
                        <FaIcon icon={faRobot} class="h-4 w-4 text-gray-400" />
                        <div>
                          <div class="font-semibold text-sm">{transcription.bot.name}</div>
                          <div class="text-xs text-gray-500">{transcription.bot.project.name}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      {providerBadge(transcription.provider)}
                    </TableCell>
                    <TableCell>
                      {statusBadge(transcription.status)}
                    </TableCell>
                    <TableCell class="text-gray-500 text-sm">
                      {formatDuration(transcription.durationSeconds)}
                    </TableCell>
                    <TableCell>
                      {transcription.wordCount ? (
                        <StatusBadge status={`${transcription.wordCount} words`} variant="info" />
                      ) : (
                        <span class="text-gray-500">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <StatusBadge 
                        status={transcription.language.toUpperCase()} 
                        variant="secondary" 
                      />
                    </TableCell>
                    <TableCell class="text-gray-500 text-xs">
                      {new Date(transcription.createdAt).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <div class="flex gap-1">
                        <Button size="sm" variant="outline">View</Button>
                        {transcription.status === 'completed' && (
                          <Button size="sm" variant="outline">Download</Button>
                        )}
                        {transcription.status === 'failed' && (
                          <Button size="sm" variant="outline">Retry</Button>
                        )}
                        <Button size="sm" variant="outline">Delete</Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <EmptyState
              icon={<FaIcon icon={faMicrophone} />}
              title="No transcriptions found"
              description="There are no transcription jobs yet."
              action={<Button>View All Jobs</Button>}
            />
          )}
        </CardBody>
      </Card>
    </div>
  );
}); 