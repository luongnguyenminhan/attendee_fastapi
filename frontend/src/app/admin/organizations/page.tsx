// page.tsx (Admin Organizations page)
import AdminLayout from "../../layouts/AdminLayout";

export default function AdminOrganizationsPage() {
  return (
    <AdminLayout>
      <h2 className="text-2xl font-bold mb-6">Organizations Management</h2>
      <div className="card bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-bold text-lg text-[var(--primary)]">Organizations List</h3>
          <button className="btn-admin bg-[var(--primary)] text-white px-4 py-2 rounded hover:bg-blue-700">Add Organization</button>
        </div>
        <div className="text-gray-500 text-center py-8">No organizations found.</div>
      </div>
      {/* Organization Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="stat-card border-l-4 border-[var(--primary)] bg-white rounded-lg p-6 shadow">
          <div className="stat-number text-3xl font-bold text-gray-800 mb-2">0</div>
          <div className="stat-label text-gray-500 uppercase text-xs tracking-wider">Total</div>
        </div>
        <div className="stat-card border-l-4 border-[var(--success)] bg-white rounded-lg p-6 shadow">
          <div className="stat-number text-3xl font-bold text-gray-800 mb-2">0</div>
          <div className="stat-label text-gray-500 uppercase text-xs tracking-wider">Active</div>
        </div>
      </div>
    </AdminLayout>
  );
}
