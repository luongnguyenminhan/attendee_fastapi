// AdminSidebar.tsx
import React from "react";
import Link from "next/link";

const navLinks = [
  { href: "/admin/dashboard", icon: "bi-speedometer2", label: "Dashboard" },
  { href: "/admin/bots", icon: "bi-robot", label: "Bots" },
  { href: "/admin/organizations", icon: "bi-people", label: "Organizations" },
  { href: "/admin/projects", icon: "bi-kanban", label: "Projects" },
  { href: "/admin/users", icon: "bi-person", label: "Users" },
  { href: "/admin/transcriptions", icon: "bi-mic", label: "Transcriptions" },
  { href: "/admin/webhooks", icon: "bi-link-45deg", label: "Webhooks" },
  { href: "/admin/settings", icon: "bi-gear", label: "Settings" },
];

export default function AdminSidebar() {
  return (
    <aside className="sidebar flex flex-col bg-[var(--background)] border-r border-gray-200 min-h-screen w-64">
      <Link href="/admin/dashboard" className="logo text-2xl font-bold text-white bg-[var(--primary)] p-4 mb-2">
        <i className="bi bi-people-fill mr-2"></i>Attendee
      </Link>
      <nav className="flex-1">
        {navLinks.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="nav-link flex items-center gap-2 px-4 py-3 text-[var(--foreground)] hover:bg-[var(--primary)] hover:text-white transition"
          >
            <i className={`bi ${link.icon}`}></i>
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
