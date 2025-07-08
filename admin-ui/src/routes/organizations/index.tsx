import { component$ } from '@builder.io/qwik';
import type { DocumentHead } from "@builder.io/qwik-city";
import { Card, CardBody } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { FaIcon } from '../../components/ui/fa-icon';
import { 
  faBuilding, 
} from '@fortawesome/free-solid-svg-icons';

export default component$(() => {
  return (
    <div class="space-y-6">
      {/* Header */}
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Organizations Management</h1>
          <p class="text-gray-600 mt-1">Quản lý tổ chức, credits và quyền hạn</p>
        </div>
        <Button class="opacity-50 pointer-events-none">
          <FaIcon icon={faBuilding} class="h-4 w-4 mr-2" />
          Add Organization
        </Button>
      </div>

      {/* Not Implemented Notice */}
      <Card>
        <CardBody class="text-center py-16">
          <FaIcon icon={faBuilding} class="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">Organizations API Coming Soon</h3>
          <p class="text-gray-500 mb-4">
            Organizations management features are being developed.<br/>
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
  title: "Organizations - Attendee Admin",
  meta: [
    {
      name: "description",
      content: "Organizations management",
    },
  ],
}; 