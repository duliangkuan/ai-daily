import { getSql } from "@/lib/db";

export const runtime = "nodejs";

/** 退订：邮件底部链接 /api/unsubscribe?token=xxx 直接打开 */
export async function GET(req: Request) {
  const token = new URL(req.url).searchParams.get("token") ?? "";

  let title = "退订失败";
  let msg = "链接无效或已过期。如有问题请直接回复日报邮件联系我们。";

  if (token) {
    try {
      const sql = getSql();
      const rows = await sql`
        update subscribers set status = 'unsubscribed', updated_at = now()
        where unsub_token = ${token}
        returning email
      `;
      if (rows.length > 0) {
        title = "已为你退订";
        msg = "你将不再收到 AI 日报。随时欢迎回来订阅 ✦";
      }
    } catch (e) {
      console.error("[unsubscribe] error:", e);
      msg = "服务器开小差了，请稍后再试。";
    }
  }

  const html = `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title} · 研究Agent的云</title>
<style>
  body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
    background:radial-gradient(60rem 60rem at 20% 0%,rgba(139,92,246,.22),transparent 60%),
      radial-gradient(50rem 50rem at 90% 10%,rgba(34,211,238,.18),transparent 55%),
      linear-gradient(180deg,#07070f,#0b0820);color:#e5e7eb}
  .card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
    backdrop-filter:blur(12px);border-radius:24px;padding:48px 40px;max-width:440px;
    margin:20px;text-align:center;box-shadow:0 0 40px rgba(34,211,238,.12)}
  h1{margin:0 0 12px;font-size:24px;
    background:linear-gradient(90deg,#22d3ee,#818cf8,#d946ef);
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
  p{margin:0 0 24px;color:rgba(229,231,235,.65);line-height:1.7}
  a{display:inline-block;padding:12px 24px;border-radius:12px;text-decoration:none;
    font-weight:600;color:#07070f;background:linear-gradient(90deg,#22d3ee,#8b5cf6);
    box-shadow:0 0 22px rgba(34,211,238,.45)}
</style></head>
<body><div class="card"><h1>${title}</h1><p>${msg}</p>
<a href="https://dufengyun.xyz">返回首页</a></div></body></html>`;

  return new Response(html, {
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}
