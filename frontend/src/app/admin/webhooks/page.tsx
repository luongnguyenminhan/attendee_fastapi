// page.tsx (Admin Webhooks page)
import AdminLayout from "../../layouts/AdminLayout";

export default function AdminWebhooksPage() {
  return (
    <AdminLayout>
      <h2 className="text-2xl font-bold mb-6">Webhooks Management</h2>
      <div className="card bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-bold text-lg text-[var(--primary)]">Webhooks List</h3>
          <button className="btn-admin bg-[var(--primary)] text-white px-4 py-2 rounded hover:bg-blue-700">Add Webhook</button>
        </div>
        <div className="text-gray-500 text-center py-8">No webhooks found.</div>
      </div>
      {/* Recent Webhook Deliveries */}
      <div className="card bg-white rounded-lg shadow p-6">
        <h3 className="font-bold text-lg mb-4 text-[var(--primary)]">Recent Deliveries</h3>
        <div className="text-gray-500">No recent deliveries.</div>
      </div>
    </AdminLayout>
  );
}
