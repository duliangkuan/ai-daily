import { NextResponse } from "next/server";
import { randomUUID } from "crypto";
import { getSql } from "@/lib/db";
import { sendWelcome } from "@/lib/mail";

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

    // 已存在则重新激活，否则插入新行;返回 unsub_token + 是否已欢迎过
    const rows = (await sql`
      insert into subscribers (email, status, unsub_token)
      values (${email}, 'active', ${token})
      on conflict (email)
      do update set status = 'active', updated_at = now()
      returning unsub_token, welcomed_at
    `) as { unsub_token: string; welcomed_at: string | null }[];

    const row = rows[0];
    // 新订阅(还没发过欢迎)→ 立即发欢迎信;失败不影响订阅成功
    if (row && !row.welcomed_at) {
      try {
        await sendWelcome(email, row.unsub_token);
        await sql`update subscribers set welcomed_at = now() where email = ${email}`;
      } catch (e) {
        console.error("[subscribe] 欢迎信发送失败(订阅仍成功):", e);
      }
    }

    return NextResponse.json({
      ok: true,
      message: "订阅成功！欢迎邮件已发出，请查收 ✦",
    });
  } catch (err) {
    console.error("[subscribe] error:", err);
    return NextResponse.json(
      { ok: false, message: "服务器开小差了，稍后再试一下" },
      { status: 500 }
    );
  }
}
