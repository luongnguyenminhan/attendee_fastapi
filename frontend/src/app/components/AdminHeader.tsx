// AdminHeader.tsx
import React from "react";

export default function AdminHeader() {
  return (
    <header className="admin-header w-full bg-gradient-to-r from-[var(--primary)] to-[var(--accent)] text-white p-4 flex items-center justify-between">
      <h1 className="text-xl font-bold">Admin Panel</h1>
      <div className="flex items-center gap-4">
        <span className="font-semibold">Xin chào, Admin</span>
        <button className="px-3 py-1 rounded bg-[var(--danger)] hover:bg-red-700 text-white font-semibold">Đăng xuất</button>
      </div>
    </header>
  );
}
