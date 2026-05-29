# -*- coding: utf-8 -*-
"""
push_wechat_draft.py — 把当日完整日报推到微信公众号草稿箱(研究Agent的云)。

内容顺序(按风云要求):DeepSeek 分析在最上面 → 今日全部资讯(按分类)在下面。
公众号正文里外链不可点,故资讯以「标题 + 来源」纯文本呈现;完整可点链接在网页版/邮件。

复用 ai-wechat-pipeline/.env 的 WECHAT_APPID / WECHAT_SECRET。
封面用 Pillow 现生成(草稿必须有封面)。本机 IP 已在公众号白名单。

用法:
  python push_wechat_draft.py            # 生成封面 + 建草稿
  python push_wechat_draft.py --dry-run  # 只渲染本地 HTML 预览,不调公众号
"""
import argparse
import json
import mimetypes
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import markdown
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from digest_content import build_sections

WECHAT_ENV = Path(r"D:\Dev\ai-wechat-pipeline\.env")
OUT_DIR = Path(os.environ.get("TRENDRADAR_OUTPUT", r"D:\Dev\TrendRadar\output"))
FONT = r"C:\Windows\Fonts\msyh.ttc"  # 微软雅黑


def log(m): print(f"[wechat-draft] {m}", flush=True)


def load_wechat_env():
    appid = os.environ.get("WECHAT_APPID")
    secret = os.environ.get("WECHAT_SECRET")
    if (not appid or not secret) and WECHAT_ENV.exists():
        for line in WECHAT_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        appid = os.environ.get("WECHAT_APPID")
        secret = os.environ.get("WECHAT_SECRET")
    return appid, secret


# ===== WeChat API =====
def _get_token(appid, secret):
    url = (f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential"
           f"&appid={appid}&secret={secret}")
    with urllib.request.urlopen(url, context=ssl.create_default_context(), timeout=30) as r:
        d = json.loads(r.read().decode("utf-8"))
    if "access_token" not in d:
        raise RuntimeError(f"token error: {d}")
    return d["access_token"]


def _upload_thumb(token, path):
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=thumb"
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    body = (f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="media"; filename="{path.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n").encode("utf-8") + path.read_bytes() + \
           f"\r\n--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=60) as r:
        d = json.loads(r.read().decode("utf-8"))
    if "media_id" not in d:
        raise RuntimeError(f"upload thumb error: {d}")
    return d["media_id"]


def _create_draft(token, html, title, digest, author, thumb_id, source_url=""):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    article = {"title": title, "author": author, "digest": digest, "content": html,
               "thumb_media_id": thumb_id, "content_source_url": source_url,
               "need_open_comment": 1, "only_fans_can_comment": 0, "show_cover_pic": 1}
    body = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=60) as r:
        d = json.loads(r.read().decode("utf-8"))
    if "media_id" not in d:
        raise RuntimeError(f"draft error: {d}")
    return d["media_id"]


# ===== 封面 =====
def make_cover(edition, out_path):
    W, H = 900, 500
    img = Image.new("RGB", (W, H), (10, 10, 26))
    d = ImageDraw.Draw(img)
    # 霓虹辉光:画几个亮圆后整体高斯模糊
    for (cx, cy, r, col) in [(120, 90, 240, (34, 90, 150)), (820, 60, 230, (80, 50, 140)),
                             (700, 460, 260, (120, 40, 130))]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    img = img.filter(ImageFilter.GaussianBlur(70))
    d = ImageDraw.Draw(img)
    try:
        f_big = ImageFont.truetype(FONT, 96)
        f_mid = ImageFont.truetype(FONT, 40)
        f_sm = ImageFont.truetype(FONT, 30)
    except Exception:
        f_big = f_mid = f_sm = ImageFont.load_default()
    d.text((64, 150), "AI 日报", font=f_big, fill=(34, 211, 238))
    d.text((68, 286), edition, font=f_mid, fill=(225, 228, 240))
    d.text((68, 410), "研究 Agent 的云  ·  每日 AI 精选", font=f_sm, fill=(150, 150, 185))
    img.save(out_path, "PNG")
    return out_path


# ===== 公众号 HTML(精致简报:洞察在顶 + Top 12 要闻;全文走阅读原文)=====
def build_wechat_html(analysis_md, heads, total, more_url):
    # 把【小标题】上色,**bold** 交给 markdown
    ana = re.sub(r"【([^】]+)】",
                 r'<span style="color:#0a84c2;font-weight:600;">【\1】</span>', analysis_md)
    ana_html = markdown.markdown(ana, extensions=["extra", "nl2br"])

    p = ['<section style="font-size:15px;color:#333;line-height:1.85;">']
    p.append('<p style="color:#999;font-size:13px;margin:0 0 18px;">'
             '每天扫描 65 个 AI 信源 · DeepSeek 智能精选</p>')

    # 洞察(顶)
    p.append('<p style="font-size:18px;font-weight:700;color:#111;margin:0 0 10px;">📊 今日 AI 洞察</p>')
    p.append('<section style="background:#f6f8fb;border-radius:10px;padding:16px 18px;'
             f'margin:0 0 26px;color:#444;font-size:15px;line-height:1.9;">{ana_html}</section>')

    # 今日要闻 Top 12
    p.append('<p style="font-size:18px;font-weight:700;color:#111;margin:0 0 14px;">🔥 今日要闻</p>')
    for i, (src, title, _u) in enumerate(heads, 1):
        src_tag = f'<span style="color:#7c83ff;font-size:12px;">[{src}]</span> ' if src else ""
        p.append(f'<p style="margin:0 0 12px;padding:0 0 12px;border-bottom:1px solid #eee;'
                 f'font-size:15px;line-height:1.6;color:#222;">'
                 f'<span style="color:#22b8cf;font-weight:700;">{i:02d}</span>&nbsp;&nbsp;{src_tag}{title}</p>')

    # 阅读原文引导
    p.append(f'<p style="margin:24px 0 4px;color:#888;font-size:14px;text-align:center;">'
             f'完整 {total} 条资讯 + 可点击链接</p>')
    p.append('<p style="margin:0;color:#888;font-size:14px;text-align:center;">'
             '👇 点文末「阅读原文」查看完整网页版</p>')
    p.append('<p style="margin:26px 0 4px;color:#bbb;font-size:12px;text-align:center;">'
             '研究Agent的云 · 每日 AI 精选直达</p>')
    p.append('</section>')
    return "".join(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    md = OUT_DIR / "latest_daily.md"
    if not md.exists():
        log(f"找不到日报:{md}"); sys.exit(1)
    analysis_md, sections, total = build_sections(md)
    heads = [t for _c, items in sections for t in items][:12]  # 扁平化取前 12 条要闻
    more_url = os.environ.get("SITE_URL", "https://ai.dufengyun.xyz").rstrip("/") + "/today"

    hour = datetime.now().hour
    date = datetime.now().strftime("%Y-%m-%d")
    edition = f"{date} {'早报' if hour < 14 else '晚报'}"
    title = f"AI 日报 · {edition}"
    digest = (analysis_md[:80].replace("\n", " ") + "…") if analysis_md else f"今日 {total} 条 AI 资讯精选"
    author = "研究Agent的云"

    html = build_wechat_html(analysis_md, heads, total, more_url)
    log(f"{edition}｜要闻 {len(heads)} 条 / 全 {total} 条,阅读原文 → {more_url}，HTML {len(html):,} 字符")

    # 本地预览
    preview = OUT_DIR / "html" / f"wechat-draft-{date}.html"
    preview.parent.mkdir(parents=True, exist_ok=True)
    preview.write_text(f'<!doctype html><meta charset="utf-8"><body style="max-width:677px;'
                       f'margin:20px auto;font-family:sans-serif;">'
                       f'<h2 style="text-align:center">{title}</h2>{html}</body>', encoding="utf-8")
    log(f"本地预览:{preview}")

    if args.dry_run:
        log("dry-run:不调公众号 API")
        return

    appid, secret = load_wechat_env()
    if not (appid and secret):
        log("缺 WECHAT_APPID / WECHAT_SECRET"); sys.exit(1)

    cover = make_cover(edition, OUT_DIR / "html" / f"wechat-cover-{date}.png")
    log(f"封面已生成:{cover}")

    token = _get_token(appid, secret)
    log("token OK")
    thumb_id = _upload_thumb(token, cover)
    log(f"封面上传 OK -> {thumb_id[:24]}…")
    media_id = _create_draft(token, html, title, digest, author, thumb_id, source_url=more_url)
    log(f"✓ 草稿已建 media_id: {media_id}")
    log("公众号后台 → 草稿箱 → 审阅 → 发出")


if __name__ == "__main__":
    main()
