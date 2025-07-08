/* eslint-disable qwik/no-use-visible-task */
import { component$, useSignal, useVisibleTask$, $ } from "@builder.io/qwik";
import type { DocumentHead } from "@builder.io/qwik-city";
import { Card, CardHeader, CardBody, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { 
  Table,
  TableHeader, 
  TableBody, 
  TableRow, 
  TableHead, 
  TableCell,
  MobileTable,
  DesktopTable,
  StatusBadge,
  SearchInput,
  EmptyState
} from '../../components/ui/table';
import { FaIcon } from '../../components/ui/fa-icon';
import { CreateUserModal } from '../../components/ui/create-user-modal';
import { 
  faUsers,
  faPlus,
  faEye,
  faPencil,
  faTrash
} from '@fortawesome/free-solid-svg-icons';
import { adminApi } from '../../api';
import type { User } from '../../api/types';

export default component$(() => {
  const users = useSignal<User[]>([]);
  const loading = useSignal(true);
  const error = useSignal<string | null>(null);
  const searchQuery = useSignal("");
  const statusFilter = useSignal("all");
  const showCreateModal = useSignal(false);

  // Load users từ API
  useVisibleTask$(async () => {
    try {
      const response = await adminApi.users.getUsers();
      users.value = response.users || [];
    } catch (err) {
      error.value = 'Failed to load users';
      console.error('Users load error:', err);
    } finally {
      loading.value = false;
    }
  });

  const filteredUsers = users.value.filter(user => {
    const matchesSearch = user.name?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesStatus = statusFilter.value === "all" || user.is_active === (statusFilter.value === "active");
    return matchesSearch && matchesStatus;
  });

  // Handler functions
  const handleOpenCreateModal = $(() => {
    showCreateModal.value = true;
  });

  const handleCloseCreateModal = $(() => {
    showCreateModal.value = false;
  });

  const handleUserCreated = $(async () => {
    // Reload users list
    try {
      loading.value = true;
      const response = await adminApi.users.getUsers();
      users.value = response.users || [];
    } catch (err) {
      console.error('Reload users error:', err);
    } finally {
      loading.value = false;
    }
  });

  // Mobile card render function
  const renderMobileUserCard = $((user: User) => (
    <div class="space-y-3">
      <div class="flex justify-between items-start">
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">{user.name || user.email}</p>
          <p class="text-xs text-gray-500 truncate">{user.email}</p>
        </div>
        <StatusBadge 
          status={user.is_active ? 'active' : 'inactive'}
          variant={user.is_active ? 'success' : 'secondary'}
        />
      </div>
      
      <div class="grid grid-cols-2 gap-2 text-xs">
        <div>
          <span class="text-gray-500">Role:</span>
          <p class="font-medium text-gray-900">{user.is_superuser ? 'Admin' : 'User'}</p>
        </div>
        <div>
          <span class="text-gray-500">Created:</span>
          <p class="font-medium text-gray-900">{new Date(user.created_at).toLocaleDateString()}</p>
        </div>
      </div>
      
      <div class="flex justify-end gap-2 pt-2 border-t border-gray-100">
        <Button size="sm" variant="outline" class="text-xs px-2 py-1">
          <FaIcon icon={faEye} class="h-3 w-3" />
        </Button>
        <Button size="sm" variant="outline" class="text-xs px-2 py-1">
          <FaIcon icon={faPencil} class="h-3 w-3" />
        </Button>
        <Button size="sm" variant="outline" class="text-xs px-2 py-1 text-red-600 hover:text-red-700">
          <FaIcon icon={faTrash} class="h-3 w-3" />
        </Button>
      </div>
    </div>
  ));

  if (loading.value) {
    return (
      <div class="space-y-4 sm:space-y-6">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Users</h1>
          <p class="text-sm sm:text-base text-gray-600 mt-1">Quản lý người dùng hệ thống</p>
        </div>
        <Card>
          <CardBody>
            <div class="text-center py-8">
              <p class="text-gray-500">Loading users...</p>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  if (error.value) {
    return (
      <div class="space-y-4 sm:space-y-6">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Users</h1>
          <p class="text-sm sm:text-base text-gray-600 mt-1">Quản lý người dùng hệ thống</p>
        </div>
        <Card>
          <CardBody>
            <div class="text-red-600 text-center py-8">
              <p>{error.value}</p>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div class="space-y-4 sm:space-y-6">
      {/* Page Header */}
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Users</h1>
          <p class="text-sm sm:text-base text-gray-600 mt-1">Quản lý người dùng hệ thống</p>
        </div>
        <Button 
          class="w-full sm:w-auto"
          onClick$={handleOpenCreateModal}
        >
          <FaIcon icon={faPlus} class="h-4 w-4 sm:mr-2" />
          <span class="hidden sm:inline">Add User</span>
          <span class="sm:hidden">Add</span>
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardBody>
          <div class="flex flex-col sm:flex-row gap-4">
            <div class="flex-1">
              <SearchInput 
                placeholder="Search users..."
                value={searchQuery.value}
                onInput$={(e: Event) => searchQuery.value = (e.target as HTMLInputElement).value}
              />
            </div>
            <div class="sm:w-48">
              <select 
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                value={statusFilter.value}
                onChange$={(e) => statusFilter.value = (e.target as HTMLSelectElement).value}
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Users Table/Cards */}
      <Card>
        <CardHeader class="pb-0 sm:pb-4">
          <CardTitle>Users ({filteredUsers.length})</CardTitle>
        </CardHeader>
        <CardBody class="pt-0 sm:pt-4">
          {filteredUsers.length === 0 ? (
            <EmptyState
              icon={<FaIcon icon={faUsers} class="h-12 w-12" />}
              title="No users found"
              description="No users match your current filters."
            />
          ) : (
            <>
              {/* Mobile View */}
              <MobileTable 
                items={filteredUsers}
                renderItem={renderMobileUserCard}
              />

              {/* Desktop View */}
              <DesktopTable>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead class="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers.map((user) => (
                      <TableRow key={user.id} hover>
                        <TableCell class="font-medium">{user.name || user.email}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>{user.is_superuser ? 'Admin' : 'User'}</TableCell>
                        <TableCell>
                          <StatusBadge 
                            status={user.is_active ? 'active' : 'inactive'}
                            variant={user.is_active ? 'success' : 'secondary'}
                          />
                        </TableCell>
                        <TableCell>{new Date(user.created_at).toLocaleDateString()}</TableCell>
                        <TableCell class="text-right">
                          <div class="flex justify-end gap-2">
                            <Button size="sm" variant="outline">
                              <FaIcon icon={faEye} class="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="outline">
                              <FaIcon icon={faPencil} class="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="outline" class="text-red-600 hover:text-red-700">
                              <FaIcon icon={faTrash} class="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </DesktopTable>
            </>
          )}
        </CardBody>
      </Card>

      {/* Create User Modal */}
      <CreateUserModal 
        isOpen={showCreateModal.value}
        onClose$={handleCloseCreateModal}
        onUserCreated$={handleUserCreated}
      />
    </div>
  );
});

export const head: DocumentHead = {
  title: "Users - Attendee Admin",
  meta: [
    {
      name: "description",
      content: "Manage system users",
    },
  ],
}; 