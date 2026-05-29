import nodemailer from "nodemailer";

/**
 * 订阅成功后立即发欢迎信(通知式,DirectMail)。
 * 需要 Vercel 环境变量:DM_FROM / DM_PASSWORD / DM_SMTP_HOST / DM_SMTP_PORT / SITE_URL
 */
export async function sendWelcome(email: string, token: string) {
  const from = process.env.DM_FROM;
  const pass = process.env.DM_PASSWORD;
  const host = process.env.DM_SMTP_HOST || "smtpdm.aliyun.com";
  const port = parseInt(process.env.DM_SMTP_PORT || "465", 10);
  const site = (process.env.SITE_URL || "https://ai.dufengyun.xyz").replace(/\/$/, "");
  if (!from || !pass) throw new Error("缺少 DM_FROM / DM_PASSWORD");

  const todayUrl = `${site}/today`;
  const unsub = `${site}/api/unsubscribe?token=${token}`;

  const html = `<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#f4f5f7">
<div style="max-width:560px;margin:0 auto;background:#fff">
  <div style="background:linear-gradient(90deg,#0a0a1a,#1a1040);padding:30px 28px;color:#fff">
    <div style="font-size:13px;letter-spacing:.18em;color:#22d3ee">研究 AGENT 的云 · AI 日报</div>
    <div style="font-size:22px;font-weight:700;margin-top:8px">🎉 欢迎订阅！</div>
  </div>
  <div style="padding:26px 28px;color:#1f2937;font-size:15px;line-height:1.8;
       font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif">
    <p style="margin:0 0 10px">你已成功订阅，以后每天 <b>早 8 点</b> 与 <b>晚 9 点</b> 各收到一封 AI 精选日报。</p>
    <p style="margin:0 0 24px;color:#6b7280">今天的这份已经为你备好，点下面直接看 👇</p>
    <p style="margin:0;text-align:center">
      <a href="${todayUrl}" style="display:inline-block;padding:13px 30px;border-radius:10px;
        background:linear-gradient(90deg,#22d3ee,#8b5cf6);color:#08081a;font-weight:700;
        text-decoration:none;font-size:15px">阅读今日 AI 日报 →</a>
    </p>
  </div>
  <div style="padding:18px 28px;border-top:1px solid #eee;color:#9aa0a6;font-size:12px;line-height:1.7;text-align:center">
    每天早晚各一封。不想再收到？<a href="${unsub}" style="color:#7c83ff">点此退订</a>
  </div>
</div></body></html>`;

  const text = `欢迎订阅「研究Agent的云」AI 日报！以后每天早晚各一封。\n\n今天的日报:${todayUrl}\n\n退订:${unsub}`;

  const transporter = nodemailer.createTransport({
    host, port, secure: port === 465, auth: { user: from, pass },
  });
  await transporter.sendMail({
    from: `"研究Agent的云" <${from}>`,
    to: email,
    subject: "欢迎订阅 AI 日报 ✦",
    text,
    html,
    headers: { "List-Unsubscribe": `<${unsub}>` },
  });
}
