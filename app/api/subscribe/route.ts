import { NextResponse } from "next/server";
import { randomUUID } from "crypto";
import { getSql } from "@/lib/db";
import { sendWelcome } from "@/lib/mail";
import { upsertSubscriber } from "@/lib/feishu";

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

    // 先看旧状态:决定是否发欢迎信(新邮箱 / 退订后回归 / 从没发过 → 发;已订阅且发过 → 不重发)
    const prev = (await sql`
      select status, welcomed_at from subscribers where email = ${email}
    `) as { status: string; welcomed_at: string | null }[];
    const prevRow = prev[0];

    const rows = (await sql`
      insert into subscribers (email, status, unsub_token)
      values (${email}, 'active', ${token})
      on conflict (email)
      do update set status = 'active', updated_at = now()
      returning unsub_token
    `) as { unsub_token: string }[];
    const unsubToken = rows[0]?.unsub_token ?? token;

    const shouldWelcome =
      !prevRow || prevRow.status === "unsubscribed" || !prevRow.welcomed_at;

    let message = "你已经在订阅啦 ✦ 日报每天早晚照常送达你的邮箱";
    if (shouldWelcome) {
      try {
        await sendWelcome(email, unsubToken);
        await sql`update subscribers set welcomed_at = now() where email = ${email}`;
        message = "订阅成功！欢迎邮件已发出，请查收 ✦";
      } catch (e) {
        console.error("[subscribe] 欢迎信发送失败(订阅仍成功):", e);
        message = "订阅成功！日报每天早晚送达你的邮箱 ✦";
      }
    }

    // 实时同步到飞书多维表格;失败不影响订阅成功
    try {
      await upsertSubscriber(email, "active", unsubToken, "网站订阅");
    } catch (e) {
      console.error("[subscribe] 飞书同步失败:", e);
    }

    return NextResponse.json({ ok: true, message });
  } catch (err) {
    console.error("[subscribe] error:", err);
    return NextResponse.json(
      { ok: false, message: "服务器开小差了，稍后再试一下" },
      { status: 500 }
    );
  }
}
