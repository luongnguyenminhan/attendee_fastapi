// page.tsx (Base page)
import BaseLayout from "../layouts/BaseLayout";
import Button from "../components/Button";

export default function BasePage() {
  return (
    <BaseLayout>
      <h1 className="text-3xl font-bold mb-4">Welcome to Base Page</h1>
      <Button variant="primary">Primary Button</Button>
    </BaseLayout>
  );
}
