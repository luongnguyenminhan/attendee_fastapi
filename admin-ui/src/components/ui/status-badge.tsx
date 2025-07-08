import { component$ } from '@builder.io/qwik';

export const StatusBadge = component$<{
  status: string;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'secondary';
  class?: string;
}>((props) => {
  const variantClasses = {
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800', 
    error: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
    secondary: 'bg-gray-100 text-gray-800'
  };
  
  const variant = props.variant || 'secondary';
  const colorClass = variantClasses[variant];
  
  return (
    <span class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass} ${props.class || ''}`}>
      {props.status}
    </span>
  );
}); 