// page.tsx (Admin Dashboard page)
import AdminLayout from "../../layouts/AdminLayout";

export default function AdminDashboardPage() {
  return (
    <AdminLayout>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
        {/* Statistics Cards */}
        <div className="stat-card border-l-4 border-[var(--primary)] bg-white rounded-lg p-6 shadow">
          <div className="stat-number text-3xl font-bold text-gray-800 mb-2">123</div>
          <div className="stat-label text-gray-500 uppercase text-xs tracking-wider">Active Bots</div>
        </div>
        <div className="stat-card border-l-4 border-[var(--success)] bg-white rounded-lg p-6 shadow">
          <div className="stat-number text-3xl font-bold text-gray-800 mb-2">45</div>
          <div className="stat-label text-gray-500 uppercase text-xs tracking-wider">Organizations</div>
        </div>
        <div className="stat-card border-l-4 border-[var(--warning)] bg-white rounded-lg p-6 shadow">
          <div className="stat-number text-3xl font-bold text-gray-800 mb-2">12</div>
          <div className="stat-label text-gray-500 uppercase text-xs tracking-wider">Projects</div>
        </div>
        <div className="stat-card border-l-4 border-[var(--danger)] bg-white rounded-lg p-6 shadow">
          <div className="stat-number text-3xl font-bold text-gray-800 mb-2">99</div>
          <div className="stat-label text-gray-500 uppercase text-xs tracking-wider">Users</div>
        </div>
      </div>
      {/* System Status & Recent Activity */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
        <div className="card bg-white rounded-lg shadow p-6">
          <h3 className="font-bold text-lg mb-4 text-[var(--primary)]">System Status</h3>
          <div className="text-gray-500">All systems operational.</div>
        </div>
        <div className="card bg-white rounded-lg shadow p-6">
          <h3 className="font-bold text-lg mb-4 text-[var(--primary)]">Recent Activity</h3>
          <div className="text-gray-500">No recent activity.</div>
        </div>
      </div>
      {/* Quick Actions */}
      <div className="card bg-white rounded-lg shadow p-6">
        <h3 className="font-bold text-lg mb-4 text-[var(--primary)]">Quick Actions</h3>
        <div className="flex gap-4">
          <button className="btn-admin bg-[var(--primary)] text-white px-4 py-2 rounded hover:bg-blue-700">Add Bot</button>
          <button className="btn-admin bg-[var(--success)] text-white px-4 py-2 rounded hover:bg-green-700">Add Organization</button>
          <button className="btn-admin bg-[var(--warning)] text-white px-4 py-2 rounded hover:bg-yellow-600">Add Project</button>
        </div>
      </div>
    </AdminLayout>
  );
}
