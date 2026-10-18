"use client";

import { useEffect, useRef, useState } from "react";
import { X } from "lucide-react";

import type { RateLimitQuota } from "@/types/telemetry";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export function AppShell({
  children,
  quota = null,
}: {
  children: React.ReactNode;
  quota?: RateLimitQuota | null;
}): React.JSX.Element {
  const [open, setOpen] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);
  const menuButton = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    const element = dialog.current;
    const trigger = menuButton.current;
    if (!open || !element) return;
    element.showModal();
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const media = window.matchMedia("(min-width: 1024px)");
    const closeOnDesktop = (): void => {
      if (media.matches) setOpen(false);
    };
    media.addEventListener("change", closeOnDesktop);
    return () => {
      element.close();
      document.body.style.overflow = overflow;
      media.removeEventListener("change", closeOnDesktop);
      trigger?.focus();
    };
  }, [open]);
  return (
    <div className="min-h-screen">
      <a
        href="#main-content"
        className="sr-only z-50 rounded bg-surface p-3 focus:not-sr-only focus:fixed focus:left-4 focus:top-4"
      >
        Skip to content
      </a>
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line lg:block">
        <Sidebar />
      </aside>
      <dialog
        id="mobile-navigation"
        ref={dialog}
        aria-label="Navigation menu"
        onCancel={() => setOpen(false)}
        onClick={(event) => {
          if (event.target === event.currentTarget) setOpen(false);
        }}
        className="fixed inset-y-0 left-0 m-0 h-dvh max-h-none w-80 max-w-[90vw] border-0 bg-transparent p-0 backdrop:bg-overlay/40"
      >
        <div className="relative h-full">
          <button
            autoFocus
            aria-label="Close navigation"
            onClick={() => setOpen(false)}
            className="absolute right-3 top-3 rounded p-2 text-secondary hover:bg-surface-subtle"
          >
            <X size={20} />
          </button>
          <Sidebar onNavigate={() => setOpen(false)} />
        </div>
      </dialog>
      <div className="lg:pl-64">
        <Header
          quota={quota}
          open={open}
          onOpen={() => setOpen(true)}
          menuButtonRef={menuButton}
        />
        <main id="main-content" className="mx-auto max-w-7xl p-5 sm:p-6 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
