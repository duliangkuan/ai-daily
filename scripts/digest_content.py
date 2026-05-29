# -*- coding: utf-8 -*-
"""
从 TrendRadar 的 latest_daily.md 里提取「精简版邮件」需要的内容：
  1) AI 深度洞察正文(md 末尾那段无链接的 DeepSeek 分析)—— 邮件主体,零链接
  2) Top N 精选标题 + 链接 —— 少量链接,控制反垃圾风险

整份日报有几百条几百个链接,直接塞邮件会被 DirectMail 判垃圾;
所以邮件只放「洞察 + 少量精选」,这也是主流 newsletter 的做法。
"""
import re
import markdown

_LINK = re.compile(r"\]\(https?://")
_ITEM = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
_NUM = re.compile(r"^\d+\.\s")
_CAT = re.compile(r"[📌🔥]\s*\[\d+/\d+\]\s*\*\*(.+?)\*\*")
_SRC = re.compile(r"^\d+\.\s*\[([^\]]+)\]")


def _analysis_md(lines):
    last_link = max((i for i, l in enumerate(lines) if _LINK.search(l)), default=-1)
    tail = lines[last_link + 1:] if last_link >= 0 else []
    return "\n".join(l for l in tail if not l.strip().startswith(">")).strip()


def build_sections(md_path):
    """把 latest_daily.md 解析成 (analysis_md, sections, total)。
    sections = [(分类名, [(来源, 标题, 链接), ...]), ...],按分类全量去重。
    供公众号全文 / 网页全文复用。"""
    lines = md_path.read_text(encoding="utf-8").splitlines()
    sections, order, seen, cur = {}, [], set(), None
    for l in lines:
        m = _CAT.search(l)
        if m:
            cur = m.group(1).strip()
            if cur not in sections:
                sections[cur] = []
                order.append(cur)
            continue
        s = l.strip()
        if cur and _NUM.match(s):
            mi = _ITEM.findall(l)
            if not mi:
                continue
            title, url = mi[-1]
            if url in seen:
                continue
            seen.add(url)
            sm = _SRC.match(s)
            sections[cur].append((sm.group(1).strip() if sm else "", title.strip(), url))
    grouped = [(c, sections[c]) for c in order if sections[c]]
    return _analysis_md(lines), grouped, len(seen)


def build_condensed(md_path, top_n=8):
    """返回 (analysis_md, analysis_html, headlines[(title,url)], total_links)。"""
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # —— AI 洞察:最后一个含链接的行之后、到结尾的无链接正文 ——
    last_link = -1
    for i, l in enumerate(lines):
        if _LINK.search(l):
            last_link = i
    tail = lines[last_link + 1:] if last_link >= 0 else []
    analysis_lines = [l for l in tail if not l.strip().startswith(">")]
    analysis_md = "\n".join(analysis_lines).strip()
    analysis_html = markdown.markdown(analysis_md, extensions=["extra", "nl2br"]) if analysis_md else ""

    # —— Top N 精选标题(按文件顺序去重)——
    seen, heads = set(), []
    for l in lines:
        if not _NUM.match(l.strip()):
            continue
        m = _ITEM.findall(l)
        if not m:
            continue
        title, url = m[-1]  # 行内最后一个 [文字](链接) 即标题链接([来源] 无链接)
        if url in seen:
            continue
        seen.add(url)
        heads.append((title.strip(), url))
        if len(heads) >= top_n:
            break

    total_links = len({m[-1][1] for l in lines for m in [_ITEM.findall(l)] if m})
    return analysis_md, analysis_html, heads, total_links
