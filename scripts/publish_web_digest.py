# -*- coding: utf-8 -*-
"""
publish_web_digest.py — 把当日完整日报渲染成网页 HTML 存进 Neon,供网站 /today 展示。

内容顺序(按风云要求):DeepSeek 分析在顶 → 全部资讯(可点链接)按分类在底。
邮件只发通知 + 链接指到 /today,正文全文看网页。

环境变量:DATABASE_URL / TRENDRADAR_OUTPUT
用法:python publish_web_digest.py
"""
import html
import os
import sys
from datetime import datetime
from pathlib import Path

import psycopg2

sys.path.insert(0, str(Path(__file__).parent))
from digest_content import build_sections

OUT_DIR = Path(os.environ.get("TRENDRADAR_OUTPUT", r"D:\Dev\TrendRadar\output"))

DDL = """
create table if not exists digests (
  id         bigserial primary key,
  edition    text not null,
  html       text not null,
  created_at timestamptz not null default now()
);
"""


def log(m): print(f"[web-digest] {m}", flush=True)


def build_web_html(analysis_md, sections, total):
    import markdown
    out = []
    out.append('<section class="digest-analysis"><h2>📊 今日 AI 洞察</h2>')
    out.append(markdown.markdown(analysis_md, extensions=["extra", "nl2br"]))
    out.append("</section>")
    out.append(f'<p class="digest-note">— 今日全部 {total} 条资讯,按主题分组 —</p>')
    for cat, items in sections:
        out.append(f'<h3 class="digest-cat">{html.escape(cat)} '
                   f'<span class="digest-count">{len(items)}</span></h3><ul class="digest-list">')
        for src, title, url in items:
            src_tag = f'<span class="digest-src">[{html.escape(src)}]</span> ' if src else ""
            out.append(f'<li>{src_tag}<a href="{html.escape(url)}" target="_blank" '
                       f'rel="noopener">{html.escape(title)}</a></li>')
        out.append("</ul>")
    return "".join(out)


def main():
    dsn = os.environ.get("DATABASE_URL", "").strip()
    if not dsn:
        log("缺 DATABASE_URL"); sys.exit(1)
    md = OUT_DIR / "latest_daily.md"
    if not md.exists():
        log(f"找不到日报:{md}"); sys.exit(1)

    analysis_md, sections, total = build_sections(md)
    inner = build_web_html(analysis_md, sections, total)
    hour = datetime.now().hour
    edition = datetime.now().strftime("%Y-%m-%d ") + ("早报" if hour < 14 else "晚报")

    conn = psycopg2.connect(dsn); conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(DDL)
        cur.execute("insert into digests (edition, html) values (%s, %s) returning id",
                    (edition, inner))
        did = cur.fetchone()[0]
    conn.close()
    log(f"{edition}｜{len(sections)} 分类 {total} 条 → digests#{did}（{len(inner):,} 字符）")


if __name__ == "__main__":
    main()
