"use client";
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

export default function GuestGuard() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // the email verification link should still work when logged in
    if (
      pathname.startsWith("/verify-email") ||
      pathname.startsWith("/reset-password")
    )
      return;

    function check() {
      if (localStorage.getItem("access_token")) router.replace("/");
    }

    check();

    // the back button can restore a cached page without re-running effects
    function onShow(e) {
      if (e.persisted) check();
    }
    window.addEventListener("pageshow", onShow);
    return () => window.removeEventListener("pageshow", onShow);
  }, [pathname, router]);

  return null;
}
