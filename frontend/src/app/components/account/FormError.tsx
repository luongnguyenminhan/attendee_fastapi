import React from "react";

interface FormErrorProps {
  message?: string;
}

const FormError: React.FC<FormErrorProps> = ({ message }) => {
  if (!message) return null;
  return (
    <div className="mt-2 text-sm text-red-500 bg-red-50 dark:bg-red-900/30 rounded px-3 py-2">
      {message}
    </div>
  );
};

export default FormError;
