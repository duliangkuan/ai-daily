# -*- coding: utf-8 -*-
"""
send_digest.py — 每天 8:00 / 21:00 把当日精选群发给所有 active 订阅者。

邮件走精简版(AI 洞察 + 少量精选链接);整份日报几百链接会被反垃圾拦截。
（完整版日报另发到公众号草稿箱,见 push_wechat_draft.py)

环境变量(由 .env 注入)：
  DATABASE_URL / SITE_URL / TRENDRADAR_OUTPUT / MAX_PER_RUN
  发信优先 DirectMail：DM_FROM / DM_PASSWORD / DM_SMTP_HOST / DM_SMTP_PORT
  回退个人 QQ：EMAIL_FROM / EMAIL_PASSWORD

用法：
  python send_digest.py            # 正式群发
  python send_digest.py --dry-run
  python send_digest.py --test you@qq.com
"""
import argparse
import os
import smtplib
import sys
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

import psycopg2

from digest_content import build_condensed

SEND_INTERVAL = 2.0


def log(m): print(f"[send_digest] {m}", flush=True)


def build_html(analysis_html, heads, total, edition, unsub_url):
    heads_html = "".join(
        f'<li style="margin:6px 0"><a href="{u}" style="color:#2563eb;text-decoration:none">{t}</a></li>'
        for t, u in heads
    )
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#f4f5f7">
<div style="max-width:640px;margin:0 auto;background:#ffffff">
  <div style="background:linear-gradient(90deg,#0a0a1a,#1a1040);padding:28px 28px 22px;color:#fff">
    <div style="font-size:13px;letter-spacing:.18em;color:#22d3ee">研究 AGENT 的云 · AI 日报</div>
    <div style="font-size:22px;font-weight:700;margin-top:6px">{edition}</div>
  </div>
  <div style="padding:22px 28px;color:#1f2937;font-size:15px;line-height:1.8;
       font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif">
    <p style="margin:0;color:#6b7280">AI 从全球 65 个信源、{total} 条资讯里为你提炼今天的要点：</p>

    <h3 style="margin:22px 0 10px;font-size:16px;color:#111">📊 今日 AI 洞察</h3>
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
    lines = ["研究Agent的云 · AI 日报", "", "【今日 AI 洞察】", analysis_md, "", "【精选速览】"]
    lines += [f"- {t}  {u}" for t, u in heads]
    lines += ["", f"退订：{unsub_url}"]
    return "\n".join(lines)


def fetch_subscribers(dsn):
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute("select email, unsub_token from subscribers "
                        "where status='active' order by created_at")
            return cur.fetchall()
    finally:
        conn.close()


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
    max_per_run = int(os.environ.get("MAX_PER_RUN", "200"))

    if not sender or not password:
        log("缺少发信账号/密码"); sys.exit(1)
    log(f"发信账号 {sender} via {smtp_host}:{smtp_port}")

    md = out_dir / "latest_daily.md"
    if not md.exists():
        log(f"找不到日报：{md}"); sys.exit(1)
    analysis_md, analysis_html, heads, total = build_condensed(md, top_n=8)

    hour = datetime.now().hour
    edition = ("早报" if hour < 14 else "晚报") + " · " + datetime.now().strftime("%Y-%m-%d")

    if args.test:
        recipients = [(args.test.strip().lower(), "TEST-TOKEN")]
    else:
        recipients = fetch_subscribers(dsn)

    log(f"{edition}｜active 订阅者 {len(recipients)} 人")
    if args.dry_run:
        for r in recipients[:5]:
            log(f"  - {r[0]}")
        return
    if not recipients:
        log("没有订阅者，结束。")
        return
    if len(recipients) > max_per_run:
        log(f"⚠️ 订阅者 {len(recipients)} > MAX_PER_RUN({max_per_run})，本次只发前 {max_per_run} 个，"
            f"其余 {len(recipients) - max_per_run} 个本轮跳过")
        recipients = recipients[:max_per_run]

    server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
    server.login(sender, password)
    sent = failed = 0
    try:
        for email_addr, token in recipients:
            unsub = f"{site}/api/unsubscribe?token={token}"
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"【AI 日报】{edition}"
            msg["From"] = formataddr(("研究Agent的云", sender))
            msg["To"] = email_addr
            msg["List-Unsubscribe"] = f"<{unsub}>"
            msg.attach(MIMEText(build_text(analysis_md, heads, unsub), "plain", "utf-8"))
            msg.attach(MIMEText(build_html(analysis_html, heads, total, edition, unsub), "html", "utf-8"))
            try:
                server.sendmail(sender, [email_addr], msg.as_string())
                sent += 1
                log(f"✓ {email_addr}")
            except Exception as e:
                failed += 1
                log(f"✗ {email_addr}: {e}")
            time.sleep(SEND_INTERVAL)
    finally:
        server.quit()
    log(f"完成：成功 {sent}，失败 {failed}")


if __name__ == "__main__":
    main()
