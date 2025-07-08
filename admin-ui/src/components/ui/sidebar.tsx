import { component$, Slot } from '@builder.io/qwik';
import { Link } from '@builder.io/qwik-city';

export const Sidebar = component$(() => {
  return (
    <div class="flex h-full flex-col bg-gray-900">
      <Slot />
    </div>
  );
});

export const SidebarHeader = component$(() => {
  return (
    <div class="p-4 border-b border-gray-800">
      <Slot />
    </div>
  );
});

export const SidebarBody = component$(() => {
  return (
    <div class="flex-1 overflow-y-auto p-4">
      <Slot />
    </div>
  );
});

export const SidebarFooter = component$(() => {
  return (
    <div class="p-4 border-t border-gray-800">
      <Slot />
    </div>
  );
});

export const SidebarSection = component$<{ class?: string }>((props) => {
  return (
    <div class={`space-y-1 ${props.class || ''}`}>
      <Slot />
    </div>
  );
});

export const SidebarItem = component$<{ href: string; class?: string }>((props) => {
  return (
    <Link
      href={props.href}
      class={`flex items-center gap-3 px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white rounded-md transition-colors ${props.class || ''}`}
    >
      <Slot />
    </Link>
  );
});

export const SidebarLabel = component$(() => {
  return (
    <span>
      <Slot />
    </span>
  );
});

export const SidebarHeading = component$(() => {
  return (
    <h3 class="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
      <Slot />
    </h3>
  );
});

export const SidebarSpacer = component$(() => {
  return <div class="flex-1" />;
}); 