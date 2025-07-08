import { component$ } from "@builder.io/qwik";
import type { DocumentHead } from "@builder.io/qwik-city";
import { Card, CardHeader, CardBody, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { FaIcon } from '../../components/ui/fa-icon';
import { 
  faRobot,
  faPlus
} from '@fortawesome/free-solid-svg-icons';

export default component$(() => {
  return (
    <div class="space-y-4 sm:space-y-6">
      {/* Page Header */}
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Bots</h1>
          <p class="text-sm sm:text-base text-gray-600 mt-1">Theo dõi và quản lý bot meetings</p>
        </div>
        <Button class="w-full sm:w-auto opacity-50 pointer-events-none">
          <FaIcon icon={faPlus} class="h-4 w-4 sm:mr-2" />
          <span class="hidden sm:inline">Create Bot</span>
          <span class="sm:hidden">Create</span>
        </Button>
      </div>

      {/* Not Implemented Notice */}
      <Card>
        <CardBody class="text-center py-16">
          <FaIcon icon={faRobot} class="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">Bots API Coming Soon</h3>
          <p class="text-gray-500 mb-4">
            Bots management features are being developed.<br/>
            API endpoints will be available in the next update.
          </p>
          <p class="text-sm text-gray-400">
            Current status: API endpoints not implemented on backend
          </p>
        </CardBody>
      </Card>
    </div>
  );
});

export const head: DocumentHead = {
  title: "Bots - Attendee Admin",
  meta: [
    {
      name: "description",
      content: "Bots management",
    },
  ],
}; 