import { component$ } from '@builder.io/qwik';

export const EmptyState = component$<{
  icon?: any;
  title: string;
  description?: string;
  action?: any;
  class?: string;
}>((props) => {
  return (
    <div class={`text-center py-12 ${props.class || ''}`}>
      {props.icon && (
        <div class="mx-auto h-12 w-12 text-gray-400 mb-4">
          {props.icon}
        </div>
      )}
      <h3 class="text-sm font-medium text-gray-900 mb-2">{props.title}</h3>
      {props.description && (
        <p class="text-sm text-gray-500 mb-6">{props.description}</p>
      )}
      {props.action && (
        <div>{props.action}</div>
      )}
    </div>
  );
}); 