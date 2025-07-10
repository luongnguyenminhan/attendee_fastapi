import Image from "next/image";
import Link from "next/link";
import React from "react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-[var(--background)] text-[var(--foreground)] font-sans transition-colors">
      <header className="w-full bg-[var(--primary)] text-white p-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Image src="/next.svg" alt="Logo" width={40} height={40} />
          <span className="text-2xl font-bold">Attendee Platform</span>
        </div>
        <nav className="flex gap-6">
          <Link
            href="/admin/dashboard"
            className="hover:underline underline-offset-4 font-semibold"
          >
            Admin
          </Link>
          <Link
            href="/base"
            className="hover:underline underline-offset-4 font-semibold"
          >
            Base
          </Link>
        </nav>
      </header>
      <main className="flex-1 flex flex-col items-center justify-center gap-10 p-8">
        <h1 className="text-4xl font-bold mb-2">Welcome to Attendee!</h1>
        <p className="text-lg text-gray-500 dark:text-gray-300 mb-6 text-center max-w-xl">
          Quản lý người tham dự, tổ chức, dự án, bot và nhiều hơn nữa với nền tảng
          hiện đại, bảo mật và dễ mở rộng.
        </p>
        <div className="flex gap-4 flex-wrap justify-center">
          <Link
            href="/admin/dashboard"
            className="px-6 py-3 rounded bg-[var(--primary)] text-white font-semibold hover:bg-blue-700 transition"
          >
            Vào trang Admin
          </Link>
          <Link
            href="/base"
            className="px-6 py-3 rounded bg-[var(--accent)] text-white font-semibold hover:bg-green-700 transition"
          >
            Trang Base
          </Link>
          <a
            href="https://nextjs.org/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 rounded bg-[var(--info)] text-white font-semibold hover:bg-sky-700 transition"
          >
            Tài liệu Next.js
          </a>
        </div>
      </main>
      <footer className="w-full p-4 bg-[var(--secondary)] text-white text-center text-sm transition-colors">
        © {new Date().getFullYear()} Attendee Platform. Powered by Next.js &
        Tailwind CSS.
      </footer>
    </div>
  );
}
