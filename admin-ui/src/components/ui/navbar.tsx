import { component$, Slot } from '@builder.io/qwik';
import { Link } from '@builder.io/qwik-city';

export const Navbar = component$(() => {
  return (
    <nav class="flex items-center justify-between bg-white border-b border-gray-200 px-4 py-3">
      <Slot />
    </nav>
  );
});

export const NavbarSection = component$<{ class?: string }>((props) => {
  return (
    <div class={`flex items-center gap-4 ${props.class || ''}`}>
      <Slot />
    </div>
  );
});

export const NavbarItem = component$<{ href?: string; 'aria-label'?: string; class?: string }>((props) => {
  const baseClass = "flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors";
  
  if (props.href) {
    return (
      <Link
        href={props.href}
        aria-label={props['aria-label']}
        class={`${baseClass} ${props.class || ''}`}
      >
        <Slot />
      </Link>
    );
  }
  
  return (
    <button
      aria-label={props['aria-label']}
      class={`${baseClass} ${props.class || ''}`}
    >
      <Slot />
    </button>
  );
});

export const NavbarLabel = component$(() => {
  return (
    <span>
      <Slot />
    </span>
  );
});

export const NavbarSpacer = component$(() => {
  return <div class="flex-1" />;
});

export const NavbarDivider = component$<{ class?: string }>((props) => {
  return <div class={`h-6 w-px bg-gray-300 ${props.class || ''}`} />;
}); 