import { NextResponse } from "next/server";
import { randomUUID } from "crypto";
import { getSql } from "@/lib/db";

export const runtime = "nodejs";

/**
 * 订阅接口
 * ─────────────────────────────────────────────
 * 写入 Neon：新邮箱 active；曾退订的重新激活；已订阅则幂等返回成功。
 * 不在此发任何邮件——发信统一由本地 send_digest 按早晚两推完成。
 */
export async function POST(req: Request) {
  try {
    const body = await req.json().catch(() => ({}));
    const email = String(body.email ?? "").trim().toLowerCase();

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) {
      return NextResponse.json(
        { ok: false, message: "邮箱格式不正确" },
        { status: 400 }
      );
    }

    const sql = getSql();
    const token = randomUUID();

    // 已存在则重新激活，否则插入新行
    await sql`
      insert into subscribers (email, status, unsub_token)
      values (${email}, 'active', ${token})
      on conflict (email)
      do update set status = 'active', updated_at = now()
    `;

    return NextResponse.json({
      ok: true,
      message: "订阅成功！明天早上开始，日报准时到达你的邮箱 ✦",
    });
  } catch (err) {
    console.error("[subscribe] error:", err);
    return NextResponse.json(
      { ok: false, message: "服务器开小差了，稍后再试一下" },
      { status: 500 }
    );
  }
}
