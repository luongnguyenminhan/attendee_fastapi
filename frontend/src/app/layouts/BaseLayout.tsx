// BaseLayout.tsx
import React from "react";

export default function BaseLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] font-sans">
      <header className="p-4 bg-[var(--primary)] text-white font-bold">Base Header</header>
      <main className="p-8">{children}</main>
      <footer className="p-4 bg-[var(--secondary)] text-white text-center">Base Footer</footer>
    </div>
  );
}
