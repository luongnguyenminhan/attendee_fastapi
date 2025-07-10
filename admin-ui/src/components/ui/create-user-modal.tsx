import { component$, useSignal, $ } from "@builder.io/qwik";
import { Modal } from "./modal";
import { Button } from "./button";
import { adminApi } from "../../api";
import type { CreateUserRequest } from "../../api/types";
import { useContext, createContextId } from "@builder.io/qwik";

interface CreateUserModalProps {
  isOpen: boolean;
  onClose$: () => void;
}

export const CreateUserModalEventContext = createContextId<any>("create-user-modal-event");

export const CreateUserModal = component$<CreateUserModalProps>(({ isOpen }) => {
  const isLoading = useSignal(false);
  const error = useSignal<string | null>(null);
  const success = useSignal<string | null>(null);
  
  // Form signals
  const email = useSignal("");
  const username = useSignal("");
  const password = useSignal("");
  const firstName = useSignal("");
  const lastName = useSignal("");
  const role = useSignal("user");
  const organizationId = useSignal("");

  const modalEvent = useContext(CreateUserModalEventContext);

  const handleSubmit = $(async (e: Event) => {
    e.preventDefault();
    
    // Reset states
    error.value = null;
    success.value = null;
    isLoading.value = true;
    
    try {
      // Validate required fields
      if (!email.value || !username.value || !password.value) {
        throw new Error("Email, username và password là bắt buộc");
      }
      
      if (password.value.length < 6) {
        throw new Error("Password phải có ít nhất 6 ký tự");
      }
      const userData: CreateUserRequest = {
        email: email.value.trim(),
        username: username.value.trim(),
        password: password.value,
        first_name: firstName.value.trim(),
        last_name: lastName.value.trim(),
        role: role.value as "user" | "admin",
      };
      if (organizationId.value.trim()) {
        userData.organization_id = organizationId.value.trim();
      }
      const result = await adminApi.users.createUser(userData);
      // context7: kiểm tra lỗi trả về dạng object {message, ...} hoặc throw nếu không phải user
      if (typeof result !== 'object' || !result || Array.isArray(result)) {
        throw new Error("Phản hồi không hợp lệ từ server");
      }
      if ('message' in result && typeof result.message === 'string') {
        throw new Error(result.message);
      }
      console.log('Create user result:', result);
      
      success.value = `User '${username.value}' được tạo thành công!`;
      // Dùng signal để trigger callback ngoài scope $()
      setTimeout(() => {
        resetAndClose();
      }, 1500);
    } catch (err: any) {
      console.error('Create user error:', err);
      console.error('Error response:', err.response?.data);
      
      // Better error message handling
      let errorMessage = "Lỗi khi tạo user";
      if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      error.value = errorMessage;
    } finally {
      isLoading.value = false;
    }
  });

  // Refactor: emit custom events thay vì truyền callback function props để tránh lỗi Qwik serialization
  const resetAndClose = $(() => {
    email.value = "";
    username.value = "";
    password.value = "";
    firstName.value = "";
    lastName.value = "";
    role.value = "user";
    organizationId.value = "";
    error.value = null;
    success.value = null;
    // Emit event thay vì gọi callback
    modalEvent.emit("userCreated");
    modalEvent.emit("close");
  });

  const handleClose = $(() => {
    resetAndClose();
  });

  return (
    <Modal 
      isOpen={isOpen} 
      title="Tạo người dùng mới" 
      size="lg"
    >
      <form onSubmit$={handleSubmit} class="space-y-4">
        {/* Error/Success Messages */}
        {error.value && (
          <div class="bg-red-50 border border-red-200 rounded-md p-3">
            <p class="text-sm text-red-800">{error.value}</p>
          </div>
        )}
        {success.value && (
          <div class="bg-green-50 border border-green-200 rounded-md p-3">
            <p class="text-sm text-green-800">{success.value}</p>
          </div>
        )}

        {/* Form Fields */}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Email */}
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email Address *
            </label>
            <input
              type="email"
              required
              value={email.value}
              onInput$={(e) => email.value = (e.target as HTMLInputElement).value}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="user@example.com"
            />
          </div>

          {/* Username */}
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Username *
            </label>
            <input
              type="text"
              required
              value={username.value}
              onInput$={(e) => username.value = (e.target as HTMLInputElement).value}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="username"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* First Name */}
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              First Name
            </label>
            <input
              type="text"
              value={firstName.value}
              onInput$={(e) => firstName.value = (e.target as HTMLInputElement).value}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Tên"
            />
          </div>

          {/* Last Name */}
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Last Name
            </label>
            <input
              type="text"
              value={lastName.value}
              onInput$={(e) => lastName.value = (e.target as HTMLInputElement).value}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Họ"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Password */}
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Password *
            </label>
            <input
              type="password"
              required
              minLength={6}
              value={password.value}
              onInput$={(e) => password.value = (e.target as HTMLInputElement).value}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Tối thiểu 6 ký tự"
            />
            <p class="text-xs text-gray-500 mt-1">Tối thiểu 6 ký tự</p>
          </div>

          {/* Role */}
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Role
            </label>
            <select
              value={role.value}
              onChange$={(e) => role.value = (e.target as HTMLSelectElement).value}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>
        </div>

        {/* Organization ID */}
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Organization ID (Tùy chọn)
          </label>
          <input
            type="text"
            value={organizationId.value}
            onInput$={(e) => organizationId.value = (e.target as HTMLInputElement).value}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="UUID của organization"
          />
          <p class="text-xs text-gray-500 mt-1">Để trống nếu user không thuộc organization nào</p>
        </div>

        {/* Footer Buttons */}
        <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <Button 
            type="button" 
            variant="outline" 
            onClick$={handleClose}
            class={isLoading.value ? 'opacity-50 pointer-events-none' : ''}
          >
            Hủy
          </Button>
          <Button 
            type="submit" 
            class={`min-w-[120px] ${isLoading.value ? 'opacity-50 pointer-events-none' : ''}`}
          >
            {isLoading.value ? (
              <div class="flex items-center gap-2">
                <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Đang tạo...</span>
              </div>
            ) : (
              "Tạo User"
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
});

export default CreateUserModal;