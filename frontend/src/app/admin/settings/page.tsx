// page.tsx (Admin Settings page)
import AdminLayout from "../../layouts/AdminLayout";

export default function AdminSettingsPage() {
  return (
    <AdminLayout>
      <h2 className="text-2xl font-bold mb-6">System Settings</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="card bg-white rounded-lg shadow p-6">
          <h3 className="font-bold text-lg mb-4 text-[var(--primary)]">System Configuration</h3>
          <div className="text-gray-500">No configuration available.</div>
        </div>
        <div className="card bg-white rounded-lg shadow p-6">
          <h3 className="font-bold text-lg mb-4 text-[var(--primary)]">Transcription Providers</h3>
          <div className="text-gray-500">No providers configured.</div>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="card bg-white rounded-lg shadow p-6">
          <h3 className="font-bold text-lg mb-4 text-[var(--primary)]">Database Settings</h3>
          <div className="text-gray-500">No database settings.</div>
        </div>
        <div className="card bg-white rounded-lg shadow p-6">
          <h3 className="font-bold text-lg mb-4 text-[var(--primary)]">Cache & Queue</h3>
          <div className="text-gray-500">No cache/queue info.</div>
        </div>
      </div>
      <div className="card bg-white rounded-lg shadow p-6">
        <h3 className="font-bold text-lg mb-4 text-[var(--primary)]">System Logs</h3>
        <div className="text-gray-500">No logs available.</div>
      </div>
    </AdminLayout>
  );
}
