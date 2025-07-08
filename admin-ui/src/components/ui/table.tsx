import { component$, Slot } from '@builder.io/qwik';

export const Table = component$<{ class?: string }>((props) => {
  return (
    <div class="overflow-x-auto">
      <table class={`min-w-full divide-y divide-gray-200 ${props.class || ''}`}>
        <Slot />
      </table>
    </div>
  );
});

export const TableHeader = component$<{ class?: string }>((props) => {
  return (
    <thead class={`bg-gray-50 ${props.class || ''}`}>
      <Slot />
    </thead>
  );
});

export const TableBody = component$<{ class?: string }>((props) => {
  return (
    <tbody class={`bg-white divide-y divide-gray-200 ${props.class || ''}`}>
      <Slot />
    </tbody>
  );
});

export const TableRow = component$<{ class?: string; hover?: boolean }>((props) => {
  const hoverClass = props.hover ? 'hover:bg-gray-50' : '';
  return (
    <tr class={`${hoverClass} ${props.class || ''}`}>
      <Slot />
    </tr>
  );
});

export const TableHead = component$<{ class?: string; sortable?: boolean }>((props) => {
  const sortableClass = props.sortable ? 'cursor-pointer hover:bg-gray-100' : '';
  return (
    <th class={`px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${sortableClass} ${props.class || ''}`}>
      <Slot />
    </th>
  );
});

export const TableCell = component$<{ class?: string }>((props) => {
  return (
    <td class={`px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-900 ${props.class || ''}`}>
      <Slot />
    </td>
  );
});

export const EmptyState = component$<{ 
  icon?: any; 
  title: string; 
  description: string; 
  action?: any;
}>((props) => {
  return (
    <div class="text-center py-12">
      <div class="text-gray-400 text-6xl mb-4">
        {props.icon}
      </div>
      <h3 class="text-lg font-semibold text-gray-900 mb-2">{props.title}</h3>
      <p class="text-gray-500 mb-6">{props.description}</p>
      {props.action}
    </div>
  );
});

export const SearchInput = component$<{
  placeholder?: string;
  value?: string;
  onInput$?: (e: Event) => void;
}>((props) => {
  return (
    <div class="relative">
      <input
        type="text"
        placeholder={props.placeholder || "Search..."}
        value={props.value || ""}
        onInput$={props.onInput$}
        class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
      />
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg class="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M12.9 14.32a8 8 0 111.414-1.414l5.387 5.387a1 1 0 01-1.414 1.414l-5.387-5.387zM8 14A6 6 0 108 2a6 6 0 000 12z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>
  );
});

export const StatusBadge = component$<{
  status: string;
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'secondary';
}>((props) => {
  const variants = {
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
    secondary: 'bg-gray-100 text-gray-800'
  };

  const variant = props.variant || 'secondary';

  return (
    <span class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]}`}>
      {props.status}
    </span>
  );
});

// Mobile-friendly table với cards
export const MobileTable = component$<{ 
  class?: string;
  items: any[];
  renderItem: (item: any, index: number) => any;
}>((props) => {
  return (
    <div class="sm:hidden">
      <div class={`space-y-3 ${props.class || ''}`}>
        {props.items.map((item, index) => (
          <div key={index} class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            {props.renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  );
});

// Desktop table wrapper
export const DesktopTable = component$<{ class?: string }>((props) => {
  return (
    <div class={`hidden sm:block ${props.class || ''}`}>
      <Slot />
    </div>
  );
}); 