"use client";
import { usePathname } from "next/navigation";
import { Nav } from "@/components/nav";

export function ConditionalNav() {
  const pathname = usePathname();
  if (pathname === "/" || pathname.startsWith("/admin") || pathname === "/login") return null;
  return <Nav />;
}
