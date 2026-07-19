"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import { ShieldCheck } from "lucide-react";

function PageLoader() {
  return (
    <div
      className="flex h-screen items-center justify-center"
      style={{ background: "var(--surface-base)" }}
    >
      <div className="flex flex-col items-center gap-4">
        <div
          className="flex items-center justify-center rounded-xl"
          style={{
            width: "2.5rem",
            height: "2.5rem",
            background: "var(--color-accent-light)",
            border: "1px solid var(--border-base)",
          }}
        >
          <ShieldCheck style={{ width: "1.25rem", height: "1.25rem", color: "var(--color-accent)" }} />
        </div>
        <div className="text-center">
          <div className="flex items-center gap-2 justify-center">
            <div
              className="h-4 w-4 animate-spin rounded-full border-[2px] border-transparent"
              style={{ borderTopColor: "var(--color-accent)" }}
            />
            <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
              Verifying session
            </p>
          </div>
          <p className="text-xs mt-1" style={{ color: "var(--text-tertiary)" }}>
            Authenticating your credentials…
          </p>
        </div>
      </div>
    </div>
  );
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    } else {
      setAuthorized(true);
    }
  }, [router]);

  if (!authorized) return <PageLoader />;

  return (
    <div
      className="flex h-screen w-screen overflow-hidden"
      style={{ background: "var(--surface-base)", color: "var(--text-primary)" }}
    >
      {/* Sidebar */}
      <Sidebar />

      {/* Content pane */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <main
          className="flex-1 overflow-y-auto"
          style={{ padding: "2rem 2.25rem" }}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
