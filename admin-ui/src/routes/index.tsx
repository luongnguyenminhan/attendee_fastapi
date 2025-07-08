import { component$, useSignal, useVisibleTask$ } from "@builder.io/qwik";
import type { DocumentHead } from "@builder.io/qwik-city";
import { StatCard, Card, CardHeader, CardBody, CardTitle, CardGrid } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { FaIcon } from '../components/ui/fa-icon';
import { 
  faUsers, 
  faBuilding, 
  faFolder, 
  faRobot 
} from '@fortawesome/free-solid-svg-icons';
import { adminApi } from '../api';

export default component$(() => {
  const stats = useSignal({
    totalUsers: 0,
    totalOrganizations: 0,
    totalProjects: 0,
    totalBots: 0
  });
  const loading = useSignal(true);
  const error = useSignal<string | null>(null);

  // Load stats từ API
  useVisibleTask$(async () => {
    try {
      const [usersResponse] = await Promise.allSettled([
        adminApi.users.getUsers()
      ]);
      
      // Update stats từ API response
      if (usersResponse.status === 'fulfilled') {
        stats.value = {
          totalUsers: usersResponse.value.items?.length || 0,
          totalOrganizations: 0, // TODO: Implement organizations API
          totalProjects: 0, // TODO: Implement projects API  
          totalBots: 0 // TODO: Implement bots API
        };
      }
    } catch (err) {
      error.value = 'Failed to load dashboard data';
      console.error('Dashboard load error:', err);
    } finally {
      loading.value = false;
    }
  });

  return (
    <div class="space-y-4 sm:space-y-6">
      {/* Page Header */}
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-sm sm:text-base text-gray-600 mt-1">Tổng quan hệ thống Attendee</p>
      </div>

      {/* Error State */}
      {error.value && (
        <Card>
          <CardBody>
            <div class="text-red-600 text-center py-4">
              <p>{error.value}</p>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Loading State */}
      {loading.value ? (
        <Card>
          <CardBody>
            <div class="text-center py-8">
              <p class="text-gray-500">Loading dashboard data...</p>
            </div>
          </CardBody>
        </Card>
      ) : (
        <>
          {/* Stats Grid */}
          <CardGrid cols="4">
            <StatCard
              title="Total Users"
              value={stats.value.totalUsers.toLocaleString()}
              icon={<FaIcon icon={faUsers} class="h-6 w-6 sm:h-8 sm:w-8" />}
              color="blue"
            />
            <StatCard
              title="Organizations"
              value={stats.value.totalOrganizations}
              icon={<FaIcon icon={faBuilding} class="h-6 w-6 sm:h-8 sm:w-8" />}
              color="green"
            />
            <StatCard
              title="Projects"
              value={stats.value.totalProjects}
              icon={<FaIcon icon={faFolder} class="h-6 w-6 sm:h-8 sm:w-8" />}
              color="purple"
            />
            <StatCard
              title="Active Bots"
              value={stats.value.totalBots}
              icon={<FaIcon icon={faRobot} class="h-6 w-6 sm:h-8 sm:w-8" />}
              color="yellow"
            />
          </CardGrid>

          <CardGrid cols="2">
            {/* System Status */}
            <Card>
              <CardHeader>
                <CardTitle>System Status</CardTitle>
              </CardHeader>
              <CardBody class="space-y-3 sm:space-y-4">
                <div class="flex justify-between items-center">
                  <span class="text-sm font-medium">API Status</span>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Online
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm font-medium">Database</span>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Connected
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm font-medium">Celery Workers</span>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    3 Active
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm font-medium">Storage</span>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                    75% Used
                  </span>
                </div>
              </CardBody>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardBody>
                <div class="text-center py-8 text-gray-500">
                  <p>No recent activities</p>
                  <p class="text-sm mt-1">Activity tracking coming soon...</p>
                </div>
              </CardBody>
            </Card>
          </CardGrid>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardBody>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
                <Button variant="outline" class="h-16 sm:h-20 flex-col gap-1 sm:gap-2 text-xs sm:text-sm">
                  <FaIcon icon={faUsers} class="h-4 w-4 sm:h-5 sm:w-5" />
                  <span>Manage Users</span>
                </Button>
                <Button variant="outline" class="h-16 sm:h-20 flex-col gap-1 sm:gap-2 text-xs sm:text-sm">
                  <FaIcon icon={faRobot} class="h-4 w-4 sm:h-5 sm:w-5" />
                  <span>View Bots</span>
                </Button>
                <Button variant="outline" class="h-16 sm:h-20 flex-col gap-1 sm:gap-2 text-xs sm:text-sm">
                  <FaIcon icon={faFolder} class="h-4 w-4 sm:h-5 sm:w-5" />
                  <span>Projects</span>
                </Button>
                <Button variant="outline" class="h-16 sm:h-20 flex-col gap-1 sm:gap-2 text-xs sm:text-sm">
                  <FaIcon icon={faBuilding} class="h-4 w-4 sm:h-5 sm:w-5" />
                  <span>Organizations</span>
                </Button>
              </div>
            </CardBody>
          </Card>
        </>
      )}
    </div>
  );
});

export const head: DocumentHead = {
  title: "Dashboard - Attendee Admin",
  meta: [
    {
      name: "description",
      content: "Attendee Admin Dashboard",
    },
  ],
};
