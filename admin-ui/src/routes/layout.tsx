import { component$, Slot } from '@builder.io/qwik';
import { AdminLayout } from '../components/layout/admin-layout';

export default component$(() => {
  return (
    <AdminLayout>
      <Slot />
    </AdminLayout>
  );
}); 