// Button.tsx
import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "accent" | "danger" | "info" | "success" | "warning";
  children: React.ReactNode;
}

export default function Button({ variant = "primary", children, ...props }: ButtonProps) {
  const colorClass = {
    primary: "bg-[var(--primary)] hover:bg-blue-700",
    secondary: "bg-[var(--secondary)] hover:bg-orange-600",
    accent: "bg-[var(--accent)] hover:bg-green-600",
    danger: "bg-[var(--danger)] hover:bg-red-700",
    info: "bg-[var(--info)] hover:bg-sky-700",
    success: "bg-[var(--success)] hover:bg-green-700",
    warning: "bg-[var(--warning)] hover:bg-yellow-600",
  }[variant];

  return (
    <button
      className={`px-4 py-2 rounded text-white font-semibold transition ${colorClass}`}
      {...props}
    >
      {children}
    </button>
  );
}
