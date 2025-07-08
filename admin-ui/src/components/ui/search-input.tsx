import { component$ } from '@builder.io/qwik';

export const SearchInput = component$<{
  placeholder?: string;
  value?: string;
  onInput$?: (e: Event) => void;
  class?: string;
}>((props) => {
  return (
    <div class="relative">
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      <input
        type="text"
        placeholder={props.placeholder}
        value={props.value}
        onInput$={props.onInput$}
        class={`block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 ${props.class || ''}`}
      />
    </div>
  );
}); 