"use client";
import React, { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [mode, setMode] = useState<string | null>(null);

  useEffect(() => {
    const saved = typeof window !== "undefined" ? localStorage.getItem("theme-mode") : null;
    if (saved === "dark" || saved === "light") {
      setMode(saved);
      document.documentElement.classList.remove("dark", "light");
      document.documentElement.classList.add(saved);
    } else {
      const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      setMode(isDark ? "dark" : "light");
      document.documentElement.classList.remove("dark", "light");
      document.documentElement.classList.add(isDark ? "dark" : "light");
    }
  }, []);

  const toggleMode = () => {
    const newMode = mode === "dark" ? "light" : "dark";
    setMode(newMode);
    document.documentElement.classList.remove("dark", "light");
    document.documentElement.classList.add(newMode);
    if (typeof window !== "undefined") localStorage.setItem("theme-mode", newMode);
  };

  return (
    <div className="fixed top-4 right-4 z-50">
      <button
        aria-label="Toggle dark mode"
        onClick={toggleMode}
        className="rounded-full p-2 bg-[var(--background)] border border-[var(--foreground)] text-[var(--foreground)] shadow hover:bg-[var(--primary)] hover:text-white transition"
      >
        {mode === "dark" ? "🌙" : "☀️"}
      </button>
    </div>
  );
}
