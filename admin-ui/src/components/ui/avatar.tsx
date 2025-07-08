import { component$ } from '@builder.io/qwik';

export const Avatar = component$<{
  src?: string;
  initials?: string;
  square?: boolean;
  class?: string;
  alt?: string;
}>((props) => {
  const baseClass = `inline-flex items-center justify-center font-semibold text-white ${
    props.square ? 'rounded' : 'rounded-full'
  } ${props.class?.includes('size-') ? '' : 'h-8 w-8'} ${props.class || ''}`;

  if (props.src) {
    return (
      <img
        width={100}
        height={100}
        src={props.src}
        alt={props.alt || ''}
        class={`${baseClass} object-cover`}
      />
    );
  }

  if (props.initials) {
    return (
      <div class={`${baseClass} bg-gray-500 text-sm`}>
        {props.initials}
      </div>
    );
  }

  return (
    <div class={`${baseClass} bg-gray-500`}>
      <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
        <path
          fill-rule="evenodd"
          d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
          clip-rule="evenodd"
        />
      </svg>
    </div>
  );
}); 