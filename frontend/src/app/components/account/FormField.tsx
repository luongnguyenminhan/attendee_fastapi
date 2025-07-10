import React from "react";

interface FormFieldProps {
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

const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  type = "text",
  value,
  onChange,
  error,
  autoComplete,
  required = false,
  placeholder,
}) => (
  <div className="mb-4">
    <label htmlFor={name} className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-200">
      {label}
    </label>
    <input
      id={name}
      name={name}
      type={type}
      value={value}
      onChange={onChange}
      autoComplete={autoComplete}
      required={required}
      placeholder={placeholder}
      className={`form-input w-full px-3 py-2 border rounded-md bg-white dark:bg-neutral-900 border-gray-300 dark:border-neutral-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary transition ${error ? "border-red-500" : ""}`}
    />
    {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
  </div>
);

export default FormField;
