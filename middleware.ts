import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { jwtVerify } from "jose";

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "atelier2026";
const SECRET = new TextEncoder().encode(ADMIN_PASSWORD);

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const token = req.cookies.get("atelier_session")?.value;

  let authenticated = false;
  if (token) {
    try { await jwtVerify(token, SECRET); authenticated = true; } catch { /* invalid token */ }
  }

  // 后台页面保护
  if (pathname.startsWith("/admin")) {
    if (!authenticated) {
      return NextResponse.redirect(new URL("/login", req.url));
    }
  }

  // API 写操作保护
  if (pathname.startsWith("/api/")) {
    const isWrite = ["POST", "PUT", "PATCH", "DELETE"].includes(req.method);
    if (isWrite && !pathname.startsWith("/api/auth/")) {
      if (!authenticated) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
      }
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*", "/api/:path*"],
};
