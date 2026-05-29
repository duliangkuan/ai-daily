# -*- coding: utf-8 -*-
"""
send_welcome.py — 给新订阅者发欢迎信(通知式:欢迎语 + 阅读今日全文链接)。

方案 A:邮件极简(DirectMail 拒长内容/新闻正文),完整日报在网页 /today。
轮询 welcomed_at IS NULL 的 active 订阅者,发完打标记。建议每 5–10 分钟跑一次。

环境变量:DATABASE_URL / SITE_URL
  发信优先 DirectMail：DM_FROM / DM_PASSWORD / DM_SMTP_HOST / DM_SMTP_PORT;回退 EMAIL_FROM / EMAIL_PASSWORD
用法:python send_welcome.py [--dry-run] [--test you@qq.com]
"""
import argparse
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import psycopg2

SEND_INTERVAL = 2.0


def log(m): print(f"[send_welcome] {m}", flush=True)


def build_html(today_url, unsub_url):
    return f"""<!doctype html><html><head><meta charset="utf-8">
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
    <p style="margin:0 0 8px;text-align:center">
      <a href="{today_url}" style="display:inline-block;padding:13px 30px;border-radius:10px;
        background:linear-gradient(90deg,#22d3ee,#8b5cf6);color:#08081a;font-weight:700;
        text-decoration:none;font-size:15px">阅读今日 AI 日报 →</a>
    </p>
  </div>
  <div style="padding:18px 28px;border-top:1px solid #eee;color:#9aa0a6;font-size:12px;line-height:1.7;text-align:center">
    每天早晚各一封。不想再收到？<a href="{unsub_url}" style="color:#7c83ff">点此退订</a>
  </div>
</div></body></html>"""


def build_text(today_url, unsub_url):
    return ("欢迎订阅「研究Agent的云」AI 日报！以后每天早晚各一封。\n\n"
            f"今天的日报:{today_url}\n\n"
            f"退订:{unsub_url}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--test", metavar="EMAIL")
    args = ap.parse_args()

    sender = os.environ.get("DM_FROM", "").strip() or os.environ.get("EMAIL_FROM", "").strip()
    password = os.environ.get("DM_PASSWORD", "").strip() or os.environ.get("EMAIL_PASSWORD", "").strip()
    smtp_host = os.environ.get("DM_SMTP_HOST", "").strip() or ("smtpdm.aliyun.com" if os.environ.get("DM_FROM") else "smtp.qq.com")
    smtp_port = int(os.environ.get("DM_SMTP_PORT", "465"))
    dsn = os.environ.get("DATABASE_URL", "").strip()
    site = os.environ.get("SITE_URL", "https://ai.dufengyun.xyz").rstrip("/")
    today_url = f"{site}/today"

    if not (sender and password and dsn):
        log("缺少发信账号/密码/DATABASE_URL"); sys.exit(1)
    log(f"发信账号 {sender} via {smtp_host}:{smtp_port}")

    if args.test:
        targets = [(args.test.strip().lower(), "TEST-TOKEN")]
    else:
        conn = psycopg2.connect(dsn)
        with conn.cursor() as cur:
            cur.execute("select email, unsub_token from subscribers "
                        "where status='active' and welcomed_at is null order by created_at")
            targets = cur.fetchall()
        conn.close()

    log(f"待发欢迎信：{len(targets)} 人")
    if args.dry_run:
        for t in targets[:10]:
            log(f"  - {t[0]}")
        return
    if not targets:
        return

    server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
    server.login(sender, password)
    sent = failed = 0
    try:
        for email_addr, token in targets:
            unsub = f"{site}/api/unsubscribe?token={token}"
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "欢迎订阅 AI 日报 ✦"
            msg["From"] = formataddr(("研究Agent的云", sender))
            msg["To"] = email_addr
            msg["List-Unsubscribe"] = f"<{unsub}>"
            msg.attach(MIMEText(build_text(today_url, unsub), "plain", "utf-8"))
            msg.attach(MIMEText(build_html(today_url, unsub), "html", "utf-8"))
            try:
                server.sendmail(sender, [email_addr], msg.as_string())
                sent += 1
                log(f"✓ {email_addr}")
                if not args.test:
                    c2 = psycopg2.connect(dsn); c2.autocommit = True
                    with c2.cursor() as cur:
                        cur.execute("update subscribers set welcomed_at=now() where email=%s", (email_addr,))
                    c2.close()
            except Exception as e:
                failed += 1
                log(f"✗ {email_addr}: {e}")
            time.sleep(SEND_INTERVAL)
    finally:
        server.quit()
    log(f"完成：成功 {sent}，失败 {failed}")


if __name__ == "__main__":
    main()
