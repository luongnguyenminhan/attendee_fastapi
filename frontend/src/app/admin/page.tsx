// page.tsx (Admin page)
import AdminLayout from "../layouts/AdminLayout";
import Button from "../components/Button";

export default function AdminPage() {
  return (
    <AdminLayout>
      <h1 className="text-3xl font-bold mb-4">Admin Dashboard</h1>
      <Button variant="accent">Go to Settings</Button>
    </AdminLayout>
  );
}
