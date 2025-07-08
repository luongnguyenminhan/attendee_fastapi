import { component$, Slot, useSignal, $ } from '@builder.io/qwik';

export const SidebarLayout = component$<{
  sidebar?: any;
  navbar?: any;
}>((props) => {
  const mobileMenuOpen = useSignal(false);

  const toggleMobileMenu = $(() => {
    mobileMenuOpen.value = !mobileMenuOpen.value;
  });

  const closeMobileMenu = $(() => {
    mobileMenuOpen.value = false;
  });

  return (
    <div class="flex h-screen bg-gray-100">
      {/* Desktop Sidebar */}
      <div class="hidden lg:flex lg:w-64 lg:flex-col">
        {props.sidebar}
      </div>

      {/* Mobile Sidebar Overlay */}
      {mobileMenuOpen.value && (
        <div class="fixed inset-0 z-40 lg:hidden">
          {/* Backdrop */}
          <div 
            class="fixed inset-0 bg-gray-600 bg-opacity-75"
            onClick$={closeMobileMenu}
          />
          
          {/* Mobile Sidebar */}
          <div class="relative flex w-full max-w-xs flex-col bg-white">
            <div class="absolute top-0 right-0 -mr-12 pt-2">
              <button
                type="button"
                class="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                onClick$={closeMobileMenu}
              >
                <span class="sr-only">Close sidebar</span>
                <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {props.sidebar}
          </div>
        </div>
      )}

      {/* Main content */}
      <div class="flex flex-1 flex-col overflow-hidden">
        {/* Mobile Header với Hamburger */}
        <div class="lg:hidden bg-white border-b border-gray-200 px-4 py-3">
          <div class="flex items-center justify-between">
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-md p-2 text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
              onClick$={toggleMobileMenu}
            >
              <span class="sr-only">Open main menu</span>
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            
            <div class="flex items-center gap-3">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
                <span class="text-sm font-bold text-white">A</span>
              </div>
              <span class="text-lg font-semibold text-gray-900">Attendee Admin</span>
            </div>
            
            <div class="w-10" /> {/* Spacer for balance */}
          </div>
        </div>

        {/* Desktop Navbar */}
        <div class="relative z-10 flex-shrink-0 hidden lg:block">
          {props.navbar}
        </div>

        {/* Page content */}
        <main class="flex-1 overflow-y-auto p-3 sm:p-4 lg:p-6">
          <Slot />
        </main>
      </div>
    </div>
  );
}); 