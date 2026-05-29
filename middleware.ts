import { NextRequest, NextResponse } from "next/server";

// 只保护 /admin;用 HTTP Basic Auth,凭证从环境变量取(只有你知道)
export const config = { matcher: ["/admin", "/admin/:path*"] };

export function middleware(req: NextRequest) {
  const user = process.env.ADMIN_USER || "admin";
  const pass = process.env.ADMIN_PASSWORD || "";
  const auth = req.headers.get("authorization");

  if (pass && auth?.startsWith("Basic ")) {
    try {
      const decoded = atob(auth.slice(6));
      const idx = decoded.indexOf(":");
      const u = decoded.slice(0, idx);
      const p = decoded.slice(idx + 1);
      if (u === user && p === pass) return NextResponse.next();
    } catch {
      /* fallthrough */
    }
  }

  return new NextResponse("需要登录", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="AI 日报后台", charset="UTF-8"' },
  });
}
