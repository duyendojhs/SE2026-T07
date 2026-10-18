"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu } from "lucide-react";
import type { RefObject } from "react";
import { navigation } from "@/config/navigation";
import { RateLimitGauge } from "@/components/telemetry/RateLimitGauge";
import type { RateLimitQuota } from "@/types/telemetry";

export function Header({
  quota,
  open,
  onOpen,
  menuButtonRef,
}: {
  quota: RateLimitQuota | null;
  open: boolean;
  onOpen: () => void;
  menuButtonRef: RefObject<HTMLButtonElement>;
}): React.JSX.Element {
  const pathname = usePathname();
  const current = navigation.find((item) => item.href === pathname);
  return (
    <header className="flex flex-wrap items-center justify-between gap-5 border-b border-line bg-surface px-5 py-4 sm:px-8">
      <div className="flex items-center gap-3">
        <button
          ref={menuButtonRef}
          onClick={onOpen}
          aria-label="Open navigation"
          aria-expanded={open}
          aria-controls="mobile-navigation"
          className="rounded border border-line p-2 lg:hidden"
        >
          <Menu size={20} />
        </button>
        <div>
          <p className="text-xs text-muted">Workspace</p>
          <nav aria-label="Breadcrumb" className="mt-1 text-sm font-semibold">
            {current?.group === "analytics" && (
              <>
                <Link href="/" className="text-muted hover:text-primary">
                  Dashboard
                </Link>
                <span aria-hidden="true" className="mx-2 text-muted">
                  /
                </span>
              </>
            )}
            <span aria-current="page">
              {current?.label ?? "Page not found"}
            </span>
          </nav>
        </div>
      </div>
      <RateLimitGauge quota={quota} />
    </header>
  );
}
