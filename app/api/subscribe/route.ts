import { NextResponse } from "next/server";

/**
 * 订阅接口（占位版）
 * ─────────────────────────────────────────────
 * 当前：仅校验邮箱格式并返回成功，方便先看前端效果。
 * 下一步：接 Neon Postgres 存订阅者 + double opt-in 确认邮件。
 * 发信仍走本地 TrendRadar 的 QQ SMTP（详见项目方案）。
 */
export async function POST(req: Request) {
  try {
    const { email } = await req.json();

    if (typeof email !== "string" || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return NextResponse.json(
        { ok: false, message: "邮箱格式不正确" },
        { status: 400 }
      );
    }

    // TODO: 写入 Neon，生成 confirm_token，发送确认邮件
    console.log("[subscribe] new email:", email);

    return NextResponse.json({
      ok: true,
      message: "订阅成功！明天早上开始，日报准时到达你的邮箱 ✦",
    });
  } catch {
    return NextResponse.json(
      { ok: false, message: "请求解析失败" },
      { status: 400 }
    );
  }
}
