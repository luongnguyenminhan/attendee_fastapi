import React from "react";
import FormField from "./FormField";
import FormError from "./FormError";

interface Field {
  label: string;
  name: string;
  type?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  autoComplete?: string;
  required?: boolean;
  placeholder?: string;
}

interface AccountFormProps {
  fields: Field[];
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  submitLabel: string;
  error?: string;
  loading?: boolean;
  children?: React.ReactNode;
}

const AccountForm: React.FC<AccountFormProps> = ({
  fields,
  onSubmit,
  submitLabel,
  error,
  loading = false,
  children,
}) => (
  <form onSubmit={onSubmit} className="space-y-2">
    {fields.map((field) => (
      <FormField key={field.name} {...field} />
    ))}
    {error && <FormError message={error} />}
    <button
      type="submit"
      className="w-full mt-2 btn btn-primary flex items-center justify-center"
      disabled={loading}
    >
      {loading ? (
        <span className="loader mr-2"></span>
      ) : null}
      {submitLabel}
    </button>
    {children}
  </form>
);

export default AccountForm;
