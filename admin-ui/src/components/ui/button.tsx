import { component$, Slot } from '@builder.io/qwik';

export const Button = component$<{
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  class?: string;
  type?: 'button' | 'submit' | 'reset';
  onClick$?: () => void;
}>((props) => {
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-500'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  const variant = props.variant || 'primary';
  const size = props.size || 'md';

  return (
    <button
      type={props.type || 'button'}
      onClick$={props.onClick$}
      class={`
        inline-flex items-center justify-center rounded-md font-medium transition-colors
        focus:outline-none focus:ring-2 focus:ring-offset-2
        ${variants[variant]}
        ${sizes[size]}
        ${props.class || ''}
      `}
    >
      <Slot />
    </button>
  );
}); 