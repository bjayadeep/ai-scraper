"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      router.push("/dashboard");
    } else {
      router.push("/login");
    }
  }, [router]);

  return (
    <div className="flex h-screen items-center justify-center" style={{ background: "var(--surface-base)" }}>
      <div className="flex flex-col items-center gap-4">
        {/* Branded spinner */}
        <div className="relative h-10 w-10">
          <div
            className="absolute inset-0 rounded-full border-[3px]"
            style={{ borderColor: "var(--border-base)" }}
          />
          <div
            className="absolute inset-0 animate-spin rounded-full border-[3px] border-transparent"
            style={{ borderTopColor: "var(--color-accent)" }}
          />
        </div>
        <div className="text-center">
          <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
            ATS Platform
          </p>
          <p className="text-xs mt-0.5" style={{ color: "var(--text-tertiary)" }}>
            Initialising secure session…
          </p>
        </div>
      </div>
    </div>
  );
}
