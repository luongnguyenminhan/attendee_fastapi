import { component$, Slot, useContext } from "@builder.io/qwik";
import { CreateUserModalEventContext } from "./create-user-modal";

interface ModalProps {
  isOpen: boolean;
  title: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  class?: string;
}

export const Modal = component$<ModalProps>(({ isOpen, title, size = 'md', class: className }) => {
  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };

  const modalEvent = useContext(CreateUserModalEventContext);

  if (!isOpen) return null;

  return (
    <div class="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick$={() => modalEvent.emit("close")}
      ></div>
      {/* Modal */}
      <div class="flex min-h-full items-center justify-center p-4">
        <div class={`
          relative bg-white rounded-lg shadow-xl w-full ${sizeClasses[size]} 
          transform transition-all ${className || ''}
        `}>
          {/* Header */}
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900">{title}</h3>
              <button
                onClick$={() => modalEvent.emit("close")}
                class="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          {/* Body */}
          <div class="px-6 py-4">
            <Slot />
          </div>
        </div>
      </div>
    </div>
  );
});

export default Modal;