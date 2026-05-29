# -*- coding: utf-8 -*-
"""
send_welcome.py — 给「新订阅但还没发过欢迎信」的用户补发欢迎邮件(附今日精选)。

机制：订阅在 Vercel 只写库；本脚本轮询 Neon 找 welcomed_at IS NULL 的 active 订阅者，
发「欢迎 + 今日 AI 洞察 + 精选速览」，发完打 welcomed_at 标记。
建议每 5–10 分钟跑一次(本地任务计划 / 云上 cron)。

邮件内容走精简版(AI 洞察 + 少量精选链接),整份日报几百链接会被反垃圾拦截。

环境变量(由 .env 注入)：
  DATABASE_URL / SITE_URL / TRENDRADAR_OUTPUT
  发信优先 DirectMail：DM_FROM / DM_PASSWORD / DM_SMTP_HOST / DM_SMTP_PORT
  回退个人 QQ：EMAIL_FROM / EMAIL_PASSWORD

用法：
  python send_welcome.py            # 给所有未欢迎的新订阅者补发
  python send_welcome.py --dry-run
  python send_welcome.py --test you@qq.com   # 强制发一封给指定邮箱(不改库)
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

import psycopg2

from digest_content import build_condensed

SEND_INTERVAL = 2.0


def log(m): print(f"[send_welcome] {m}", flush=True)


def build_html(analysis_html, heads, total, unsub_url):
    heads_html = "".join(
        f'<li style="margin:6px 0"><a href="{u}" style="color:#2563eb;text-decoration:none">{t}</a></li>'
        for t, u in heads
    )
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#f4f5f7">
<div style="max-width:640px;margin:0 auto;background:#ffffff">
  <div style="background:linear-gradient(90deg,#0a0a1a,#1a1040);padding:30px 28px;color:#fff">
    <div style="font-size:13px;letter-spacing:.18em;color:#22d3ee">研究 AGENT 的云 · AI 日报</div>
    <div style="font-size:23px;font-weight:700;margin-top:8px">🎉 欢迎订阅！</div>
  </div>
  <div style="padding:22px 28px;color:#1f2937;font-size:15px;line-height:1.8;
       font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif">
    <p style="margin:0 0 6px">你已成功订阅「研究Agent的云」AI 日报 👏 以后每天 <b>早 8 点</b> 与 <b>晚 9 点</b> 各一封。</p>
    <p style="margin:0;color:#6b7280">先送上今天的精选 —— 由 AI 从全球 65 个信源、{total} 条资讯里提炼：</p>

    <h3 style="margin:24px 0 10px;font-size:16px;color:#111">📊 今日 AI 洞察</h3>
    <div style="color:#374151;font-size:14px;line-height:1.85">{analysis_html}</div>

    <h3 style="margin:24px 0 10px;font-size:16px;color:#111">🔥 精选速览</h3>
    <ol style="margin:0;padding-left:20px;color:#374151;font-size:14px">{heads_html}</ol>
  </div>
  <div style="padding:18px 28px;border-top:1px solid #eee;color:#9aa0a6;font-size:12px;line-height:1.7;text-align:center">
    你正在订阅「研究Agent的云」AI 日报，每天早晚各一封。<br>
    不想再收到？<a href="{unsub_url}" style="color:#7c83ff">点此退订</a>
  </div>
</div></body></html>"""


def build_text(analysis_md, heads, unsub_url):
    lines = ["欢迎订阅「研究Agent的云」AI 日报！以后每天早晚各一封。", "", "【今日 AI 洞察】", analysis_md, "", "【精选速览】"]
    lines += [f"- {t}  {u}" for t, u in heads]
    lines += ["", f"退订：{unsub_url}"]
    return "\n".join(lines)


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
    out_dir = Path(os.environ.get("TRENDRADAR_OUTPUT", r"D:\Dev\TrendRadar\output"))

    if not (sender and password and dsn):
        log("缺少发信账号/密码/DATABASE_URL"); sys.exit(1)
    log(f"发信账号 {sender} via {smtp_host}:{smtp_port}")

    md = out_dir / "latest_daily.md"
    if not md.exists():
        log(f"找不到日报：{md}"); sys.exit(1)
    analysis_md, analysis_html, heads, total = build_condensed(md, top_n=8)

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
            msg["Subject"] = "欢迎订阅 AI 日报 · 附今日精选"
            msg["From"] = formataddr(("研究Agent的云", sender))
            msg["To"] = email_addr
            msg["List-Unsubscribe"] = f"<{unsub}>"
            msg.attach(MIMEText(build_text(analysis_md, heads, unsub), "plain", "utf-8"))
            msg.attach(MIMEText(build_html(analysis_html, heads, total, unsub), "html", "utf-8"))
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
