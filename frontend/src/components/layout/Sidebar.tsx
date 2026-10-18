"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { GitFork } from "lucide-react";
import { navigation } from "@/config/navigation";

export function Sidebar({
  onNavigate,
}: {
  onNavigate?: () => void;
}): React.JSX.Element {
  const pathname = usePathname();
  return (
    <div className="flex h-full flex-col bg-surface p-5">
      <Link
        href="/"
        onClick={onNavigate}
        className="mb-8 flex items-center gap-3 px-2 py-3"
      >
        <span className="rounded-lg bg-primary p-2 text-on-color">
          <GitFork size={22} />
        </span>
        <span className="text-sm font-semibold">
          GitHub<span className="block text-secondary">Project Coach</span>
        </span>
      </Link>
      <nav aria-label="Main navigation" className="space-y-7">
        <div role="group" aria-label="Dashboard">
          {navigation
            .filter((item) => item.group !== "system")
            .map(({ href, label, icon: Icon, group }) => (
              <Link
                key={href}
                href={href}
                onClick={onNavigate}
                aria-current={pathname === href ? "page" : undefined}
                className={`flex items-center gap-2.5 rounded-md py-3 text-xs transition-colors ${group === "analytics" ? "ml-5 border-l border-line pl-4 pr-2" : "px-3 font-semibold"} ${pathname === href ? "bg-primary-soft text-primary" : "text-secondary hover:bg-surface-muted hover:text-foreground"}`}
              >
                <Icon
                  size={group === "analytics" ? 15 : 18}
                  className="shrink-0"
                />
                {label}
              </Link>
            ))}
        </div>
        <div role="group" aria-label="System">
          <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-widest text-muted">
            System
          </p>
          {navigation
            .filter((item) => item.group === "system")
            .map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                onClick={onNavigate}
                aria-current={pathname === href ? "page" : undefined}
                className={`flex items-center gap-2.5 rounded-md px-3 py-3 text-xs ${pathname === href ? "bg-primary-soft text-primary" : "text-secondary hover:bg-surface-muted"}`}
              >
                <Icon size={18} />
                {label}
              </Link>
            ))}
        </div>
      </nav>
      <p className="mt-auto px-2 pt-5 text-[10px] text-muted">
        SE2026-T07 · Team Entropy
      </p>
    </div>
  );
}
