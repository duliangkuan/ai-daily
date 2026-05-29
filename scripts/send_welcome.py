# -*- coding: utf-8 -*-
"""
send_welcome.py — 给「新订阅但还没发过欢迎信」的用户补发欢迎邮件(附今日日报)。

机制：订阅在 Vercel 只写库；本脚本在本地/服务器轮询 Neon，
找出 welcomed_at IS NULL 的 active 订阅者，发欢迎信 + 今日日报，发完打标记。
建议每 5–10 分钟跑一次（本地用任务计划，云上用 cron）。

环境变量（同 send_digest，由 .env 注入）：
  DATABASE_URL / EMAIL_FROM / EMAIL_PASSWORD / SITE_URL / TRENDRADAR_OUTPUT

用法：
  python send_welcome.py            # 给所有未欢迎的新订阅者补发
  python send_welcome.py --dry-run  # 只列出待发，不发
  python send_welcome.py --test you@qq.com  # 强制发一封给指定邮箱(不改库)
"""
import argparse
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

import markdown
import psycopg2

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465
SEND_INTERVAL = 2.0


def log(m): print(f"[send_welcome] {m}", flush=True)


def load_digest_html(output_dir: Path) -> str:
    md = output_dir / "latest_daily.md"
    if not md.exists():
        log(f"找不到日报：{md}"); sys.exit(1)
    return markdown.markdown(md.read_text(encoding="utf-8"),
                             extensions=["extra", "smarty", "nl2br"])


def wrap_welcome(inner_html: str, unsub_url: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#f4f5f7">
<div style="max-width:680px;margin:0 auto;background:#ffffff">
  <div style="background:linear-gradient(90deg,#0a0a1a,#1a1040);padding:30px 28px;color:#fff">
    <div style="font-size:13px;letter-spacing:.18em;color:#22d3ee">研究 AGENT 的云 · AI 日报</div>
    <div style="font-size:23px;font-weight:700;margin-top:8px">🎉 欢迎订阅！</div>
  </div>
  <div style="padding:22px 28px 4px;color:#1f2937;font-size:15px;line-height:1.8;
       font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif">
    <p style="margin:0 0 10px">你已成功订阅「研究Agent的云」AI 日报 👏</p>
    <p style="margin:0 0 4px;color:#4b5563">从今往后，每天 <b>早 8 点</b> 与 <b>晚 9 点</b>，我会把全球 65 个 AI 信源里
    AI 精选出的当日要闻直接送到这个邮箱。先送上 <b>今天的这份</b>：</p>
  </div>
  <div style="height:1px;background:#eee;margin:16px 28px"></div>
  <div style="padding:4px 28px 24px;color:#1f2937;font-size:15px;line-height:1.75;
       font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif">
    {inner_html}
  </div>
  <div style="padding:20px 28px;border-top:1px solid #eee;color:#9aa0a6;font-size:12px;line-height:1.7;text-align:center">
    你正在订阅「研究Agent的云」AI 日报，每天早晚各一封。<br>
    不想再收到？<a href="{unsub_url}" style="color:#7c83ff">点此退订</a>
  </div>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--test", metavar="EMAIL")
    args = ap.parse_args()

    sender = os.environ.get("EMAIL_FROM", "").strip()
    password = os.environ.get("EMAIL_PASSWORD", "").strip()
    dsn = os.environ.get("DATABASE_URL", "").strip()
    site = os.environ.get("SITE_URL", "https://ai.dufengyun.xyz").rstrip("/")
    out_dir = Path(os.environ.get("TRENDRADAR_OUTPUT", r"D:\Dev\TrendRadar\output"))

    if not (sender and password and dsn):
        log("缺少 EMAIL_FROM / EMAIL_PASSWORD / DATABASE_URL"); sys.exit(1)

    inner = load_digest_html(out_dir)

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

    server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
    server.login(sender, password)
    sent = failed = 0
    try:
        for email_addr, token in targets:
            unsub = f"{site}/api/unsubscribe?token={token}"
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "欢迎订阅 AI 日报 · 附今日精选 ✦"
            msg["From"] = formataddr(("研究Agent的云", sender))
            msg["To"] = email_addr
            msg["List-Unsubscribe"] = f"<{unsub}>"
            msg.attach(MIMEText("请用支持 HTML 的邮件客户端查看本日报。", "plain", "utf-8"))
            msg.attach(MIMEText(wrap_welcome(inner, unsub), "html", "utf-8"))
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
