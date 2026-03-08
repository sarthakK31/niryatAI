"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageSquare,
  CheckCircle2,
  Globe2,
  User,
  LogOut,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/chat", label: "AI Assistant", icon: MessageSquare },
  { href: "/readiness", label: "Export Readiness", icon: CheckCircle2 },
  { href: "/markets", label: "Market Intelligence", icon: Globe2 },
  { href: "/profile", label: "Profile", icon: User },
];

export default function Sidebar({ onLogout }: { onLogout: () => void }) {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-screen bg-[var(--bg-card)] border-r border-[var(--border)] flex flex-col fixed left-0 top-0">
      {/* Logo */}
      <div className="p-6 border-b border-[var(--border)]">
        <h1 className="text-2xl font-bold">
          <span className="text-[var(--accent)]">Niryat</span>{" "}
          <span className="text-[var(--primary-light)]">AI</span>
        </h1>
        <p className="text-xs text-[var(--text-secondary)] mt-1">
          Export Intelligence Platform
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? "bg-[var(--primary)] text-white"
                  : "text-[var(--text-secondary)] hover:bg-[var(--border)] hover:text-white"
              }`}
            >
              <Icon size={20} />
              <span className="text-sm font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-[var(--border)]">
        <button
          onClick={onLogout}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-[var(--text-secondary)] hover:bg-red-900/30 hover:text-red-400 transition-colors w-full"
        >
          <LogOut size={20} />
          <span className="text-sm font-medium">Logout</span>
        </button>
      </div>
    </aside>
  );
}
