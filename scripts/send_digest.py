# -*- coding: utf-8 -*-
"""
send_digest.py — 把 TrendRadar 生成的日报群发给 Neon 里的订阅者。

数据流：
  TrendRadar 跑完 → output/latest_daily.md
  本脚本：读 md → 转 HTML → 套品牌模板 → 逐封发给 active 订阅者（带退订链接）

环境变量（由 run_trendradar.ps1 从 TrendRadar/.env 注入）：
  DATABASE_URL    Neon 连接串（postgres://...sslmode=require）
  EMAIL_FROM      发信 QQ 邮箱
  EMAIL_PASSWORD  QQ SMTP 授权码
  SITE_URL        站点地址（退订链接用，默认 https://dufengyun.xyz）
  TRENDRADAR_OUTPUT  日报目录（默认 D:\\Dev\\TrendRadar\\output）
  MAX_PER_RUN     单次最多发多少封（默认 90，护住 QQ 普通号 100/天上限）

用法：
  python send_digest.py            # 正式群发
  python send_digest.py --dry-run  # 只统计，不发
  python send_digest.py --test you@qq.com  # 只发给指定邮箱自测
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

import markdown
import psycopg2

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465
SEND_INTERVAL = 2.0  # 秒/封 → ≈30 封/分，稳在 QQ 的 40/分限速内


def log(msg: str) -> None:
    print(f"[send_digest] {msg}", flush=True)


def load_digest_html(output_dir: Path) -> str:
    md_path = output_dir / "latest_daily.md"
    if not md_path.exists():
        log(f"找不到日报：{md_path}")
        sys.exit(1)
    text = md_path.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["extra", "smarty", "nl2br"])
    return body


def wrap_email(inner_html: str, unsub_url: str, edition: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#f4f5f7;padding:0">
<div style="max-width:680px;margin:0 auto;background:#ffffff">
  <div style="background:linear-gradient(90deg,#0a0a1a,#1a1040);padding:28px 28px 22px;color:#fff">
    <div style="font-size:13px;letter-spacing:.18em;color:#22d3ee">研究 AGENT 的云 · AI 日报</div>
    <div style="font-size:22px;font-weight:700;margin-top:6px">{edition}</div>
  </div>
  <div style="padding:24px 28px;color:#1f2937;font-size:15px;line-height:1.75;
       font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif">
    {inner_html}
  </div>
  <div style="padding:20px 28px;border-top:1px solid #eee;color:#9aa0a6;font-size:12px;line-height:1.7;text-align:center">
    你正在订阅「研究Agent的云」AI 日报，每天早晚各一封。<br>
    不想再收到？<a href="{unsub_url}" style="color:#7c83ff">点此退订</a>
  </div>
</div></body></html>"""


def fetch_subscribers(dsn: str):
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "select email, unsub_token from subscribers where status='active' order by created_at"
            )
            return cur.fetchall()
    finally:
        conn.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--test", metavar="EMAIL", help="只发给该邮箱自测")
    args = ap.parse_args()

    sender = os.environ.get("EMAIL_FROM", "").strip()
    password = os.environ.get("EMAIL_PASSWORD", "").strip()
    dsn = os.environ.get("DATABASE_URL", "").strip()
    site = os.environ.get("SITE_URL", "https://dufengyun.xyz").rstrip("/")
    out_dir = Path(os.environ.get("TRENDRADAR_OUTPUT", r"D:\Dev\TrendRadar\output"))
    max_per_run = int(os.environ.get("MAX_PER_RUN", "90"))

    if not sender or not password:
        log("缺少 EMAIL_FROM / EMAIL_PASSWORD"); sys.exit(1)
    if not dsn:
        log("缺少 DATABASE_URL"); sys.exit(1)

    hour = datetime.now().hour
    edition = ("早报" if hour < 14 else "晚报") + " · " + datetime.now().strftime("%Y-%m-%d")

    inner = load_digest_html(out_dir)

    # 收件人列表
    if args.test:
        recipients = [(args.test.strip().lower(), "TEST-TOKEN")]
    else:
        recipients = fetch_subscribers(dsn)

    log(f"{edition}｜active 订阅者 {len(recipients)} 人")

    if args.dry_run:
        log("dry-run：不发送。前 5 个收件人示例：")
        for r in recipients[:5]:
            log(f"  - {r[0]}")
        return

    if not recipients:
        log("没有订阅者，结束。")
        return

    if len(recipients) > max_per_run:
        log(f"⚠️ 订阅者 {len(recipients)} > MAX_PER_RUN({max_per_run})，"
            f"本次只发前 {max_per_run} 个，其余 {len(recipients) - max_per_run} 个本轮跳过"
            f"（已达 QQ 个人号上限，该升级阿里云 DirectMail 了）")
        recipients = recipients[:max_per_run]

    server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
    server.login(sender, password)

    sent = 0
    failed = 0
    try:
        for email_addr, token in recipients:
            unsub_url = f"{site}/api/unsubscribe?token={token}"
            html = wrap_email(inner, unsub_url, edition)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"【AI 日报】{edition}"
            msg["From"] = formataddr(("研究Agent的云", sender))
            msg["To"] = email_addr
            msg["List-Unsubscribe"] = f"<{unsub_url}>"
            msg.attach(MIMEText("请用支持 HTML 的邮件客户端查看本日报。", "plain", "utf-8"))
            msg.attach(MIMEText(html, "html", "utf-8"))
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
