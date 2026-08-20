# -*- coding: utf-8 -*-
"""
push_group_copy.py — AI 日报「社群转发文案」生成 + 推送社群

链路:
  latest_daily.md (TrendRadar 产出)
    → digest_content.build_condensed 抽「DeepSeek 分析 + Top 条目」
    → DeepSeek 加工成「精选速览版」纯文本文案(复制即可转发微信群)
    → 企微群机器人 webhook / 飞书会员群
  运营同学在企微复制 → 转发到 10 个 AI 微信群；会员飞书群直接接收同款内容。

设计要点:
  · 输出纯文本(emoji + 数字序号 + 换行),不含 markdown 语法 —— 运营从企微
    复制粘贴到微信群时,## / ** 会变成一堆字符,所以刻意避开。
  · 企微 text 消息上限 2048 字节;超了自动回退 markdown(4096)。
  · 所有密钥走环境变量 / gitignore 的 TrendRadar config,脚本本身零硬编码
    (本文件位于公开开源仓库 ai-daily)。

用法:
  python push_group_copy.py --dry-run   # 只生成并打印,不推送
  python push_group_copy.py             # 按 GROUP_COPY_CHANNELS 推送
  python push_group_copy.py --existing  # 复用已落盘文案并推送，不重复调用模型

环境变量:
  TRENDRADAR_OUTPUT  latest_daily.md 所在目录(默认 D:\\Dev\\TrendRadar\\output)
  TRENDRADAR_CONFIG  config.yaml 路径(默认 <output>/../config/config.yaml)
  DEEPSEEK_API_KEY   DeepSeek key(缺省时从 config.yaml 的 ai.api_key 读)
  DEEPSEEK_API_BASE  DeepSeek 端点(默认 https://api.deepseek.com)
  DEEPSEEK_MODEL     模型(默认 deepseek-chat)
  GROUP_COPY_CHANNELS  推送渠道，逗号分隔：wework、feishu_webhook、feishu_bot、feishu_cli（默认 wework）
  WEWORK_WEBHOOK     企微群机器人 webhook（启用 wework 时必填）
  FEISHU_WEBHOOK     飞书群机器人 Webhook（启用 feishu_webhook 时必填）
  FEISHU_CHAT_ID     飞书群 chat_id（启用 feishu_cli 时必填）
  FEISHU_CLI_BIN     可选，lark-cli 可执行文件路径（默认 lark-cli）
  FEISHU_APP_ID      飞书应用 App ID（启用 feishu_bot 时必填）
  FEISHU_APP_SECRET  飞书应用 App Secret（启用 feishu_bot 时必填）
  GROUP_COPY_SITE    完整版链接(默认 https://ai.dufengyun.xyz/today)
"""
import os
import re
import sys
import json
import time
import hashlib
import shutil
import subprocess
import datetime as _dt
from pathlib import Path

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from digest_content import build_sections  # noqa: E402


class FeishuDeliveryError(RuntimeError):
    """飞书 Webhook 在完成重试后仍无法投递。"""


def log(m):
    print(f"[group-copy] {m}", flush=True)


OUT_DIR = Path(os.environ.get("TRENDRADAR_OUTPUT", r"D:\Dev\TrendRadar\output"))
SITE = os.environ.get("GROUP_COPY_SITE", "https://ai.dufengyun.xyz/today")


def _config_path() -> Path:
    p = os.environ.get("TRENDRADAR_CONFIG")
    if p:
        return Path(p)
    # 默认 <output>/../config/config.yaml
    return OUT_DIR.parent / "config" / "config.yaml"


def _read_config_value(key: str) -> str:
    """从 config.yaml 里正则抠一个顶层/二级标量值(避免强依赖 PyYAML)。"""
    cfg = _config_path()
    if not cfg.exists():
        return ""
    text = cfg.read_text(encoding="utf-8")
    m = re.search(rf'^\s*{re.escape(key)}\s*:\s*"?([^"\n#]+)"?', text, re.M)
    return m.group(1).strip() if m else ""


def deepseek_key() -> str:
    return os.environ.get("DEEPSEEK_API_KEY") or _read_config_value("api_key")


def report_date_label() -> str:
    """从 md 的『更新时间：YYYY-MM-DD』取日期,取不到回退今天。返回『7月7日』。"""
    md = OUT_DIR / "latest_daily.md"
    d = _dt.date.today()
    if md.exists():
        m = re.search(r"更新时间[:：]\s*(\d{4})-(\d{2})-(\d{2})",
                      md.read_text(encoding="utf-8"))
        if m:
            d = _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return f"{d.month}月{d.day}日"


PROMPT = """你是「研究Agent的云」AI 日报的社群编辑。下面是今天的 AI 圈日报原始素材(DeepSeek 深度分析 + 今日热点条目)。请把它加工成一条**发到微信群的转发文案**。

【硬性格式要求】
1. 纯文本,禁止任何 markdown 符号(不要 #、*、`、> 等),标题层级只用 emoji 和实心圆数字序号,因为运营会直接复制粘贴到微信群。
2. 严格用下面这个骨架(方括号内替换成真实内容,方括号本身不要出现;两条 `──────────` 分隔线原样保留):
🌅 AI日报 · {date}

[一句话点出今天最值得关注的主线，结尾加 👇]
──────────
❶ [短标题，不超过18字]
[一句话说清是什么+为什么值得看，不超过40字]

❷ [短标题]
[一句话]

……(共 6 到 8 条，序号依次用 ❶❷❸❹❺❻❼❽，标题与下一行说明之间不空行、不缩进)
──────────
💡 今日研判：[一句话给个有信息量的判断，不超过40字]

📎 完整版 → {site}

【内容要求】
- 6 到 8 条,从素材里挑最有传播价值的(重大发布 / 融资 IPO / 政策 / 争议 / 硬核突破优先),别选无聊的模型仓库名。
- 每条要具体,带上公司名/产品名/数字,不要空话。
- 语气专业但接地气,像懂行的朋友在群里划重点,不浮夸不标题党。
- 全文控制在 500 字以内(含标点),太长运营没法一条发。
- 只输出文案本身,不要任何解释、前言或代码块包裹。

【今日素材】
=== DeepSeek 深度分析 ===
{analysis}

=== 今日热点条目 ===
{items}
"""


def generate_copy() -> str:
    md_path = OUT_DIR / "latest_daily.md"
    if not md_path.exists():
        raise SystemExit(f"找不到日报: {md_path}")

    # build_sections 用「标志头定位」抽分析(比 build_condensed 的「最后一个链接之后」稳,
    # 因为本日报分析段排在顶部);sections 给分类条目,展平取前若干条喂给模型筛选。
    analysis_md, sections, total = build_sections(md_path)
    heads = []
    for _cat, rows in sections:
        for _src, title, _url in rows:
            heads.append(title)
            if len(heads) >= 16:
                break
        if len(heads) >= 16:
            break
    items = "\n".join(f"- {t}" for t in heads) or "(无)"
    analysis = (analysis_md or "").strip()[:4000] or "(今日分析缺失，请仅依据热点条目提炼)"

    key = deepseek_key()
    if not key:
        raise SystemExit("缺 DeepSeek key(设 DEEPSEEK_API_KEY 或写进 config.yaml ai.api_key)")

    base = os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com").rstrip("/")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    prompt = PROMPT.format(date=report_date_label(), site=SITE,
                           analysis=analysis, items=items)

    log(f"调用 DeepSeek({model}) 生成文案… 素材:{len(heads)}条 / 分析{len(analysis)}字")
    resp = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1200,
        },
        timeout=120,
    )
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"].strip()
    return _sanitize(text)


def _sanitize(text: str) -> str:
    """兜底清掉模型偶尔漏出的 markdown 痕迹,保证复制到微信群干净。"""
    # 去掉代码块围栏
    text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text.strip())
    lines = []
    for ln in text.split("\n"):
        s = ln.rstrip()
        s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)   # **加粗**
        s = re.sub(r"^#{1,6}\s*", "", s)          # ## 标题
        s = re.sub(r"^\s*[-*]\s+", "", s)         # - 列表符(保留数字emoji序号)
        lines.append(s)
    # 折叠 3+ 连续空行为 1 个
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return out


def push_wework(content: str) -> None:
    webhook = os.environ.get("WEWORK_WEBHOOK", "").strip()
    if not webhook:
        raise SystemExit("缺 WEWORK_WEBHOOK,无法推送")

    nbytes = len(content.encode("utf-8"))
    if nbytes <= 2048:
        payload = {"msgtype": "text", "text": {"content": content}}
        log(f"推送 text 消息({nbytes} 字节)")
    else:
        payload = {"msgtype": "markdown", "markdown": {"content": content}}
        log(f"文案 {nbytes} 字节超 text 上限,回退 markdown")

    r = requests.post(webhook, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("errcode") != 0:
        raise SystemExit(f"企微推送失败: {data}")
    log("企微推送成功 ✓")


def push_feishu_cli(content: str) -> None:
    """通过 lark-cli 向会员飞书群发送与企微完全相同的纯文本日报。"""
    chat_id = os.environ.get("FEISHU_CHAT_ID", "").strip()
    if not chat_id:
        raise SystemExit("缺 FEISHU_CHAT_ID，无法推送飞书会员群")

    cli = os.environ.get("FEISHU_CLI_BIN", "lark-cli").strip() or "lark-cli"
    cli_path = shutil.which(cli)
    if not cli_path:
        raise SystemExit(f"找不到飞书 CLI：{cli}")

    log(f"推送飞书纯文本消息（{len(content.encode('utf-8'))} 字节）")
    args = ["im", "+messages-send", "--chat-id", chat_id, "--text", content, "--as", "user"]
    # npm 在 Windows 安装的 CLI 通常是 .cmd shim，Python 无法直接执行。
    # 优先经同目录的 PowerShell shim 调用，参数保持数组传递，避免日报正文被 shell 解释。
    ps1 = Path(cli_path).with_suffix(".ps1")
    if os.name == "nt" and ps1.exists():
        command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps1), *args]
    else:
        command = [cli_path, *args]
    result = subprocess.run(
        command,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise SystemExit(f"飞书推送失败（exit {result.returncode}）：{detail}")
    log("飞书会员群推送成功 ✓")


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def _delivery_key(content: str, today: _dt.date) -> tuple[str, str]:
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return f"{today.isoformat()}:{digest}", digest


def deliver_feishu_webhook(
    content: str,
    *,
    webhook: str,
    state_dir: Path,
    post=requests.post,
    retries: int = 3,
    sleeper=time.sleep,
    today: _dt.date | None = None,
) -> dict:
    """可靠投递一份日报：同日幂等、失败落盘、最多重试 retries 次。"""
    if not webhook:
        raise FeishuDeliveryError("缺 FEISHU_WEBHOOK，无法推送飞书会员群")
    if retries < 1:
        raise ValueError("retries 必须至少为 1")

    state_dir = Path(state_dir)
    pending_path = state_dir / "pending.json"
    sent_path = state_dir / "sent.json"
    current_day = today or _dt.date.today()
    key, digest = _delivery_key(content, current_day)

    sent = _load_json(sent_path)
    if sent.get("key") == key:
        return {"status": "already_sent", "key": key, "hash": digest}

    pending = _load_json(pending_path)
    if pending.get("key") and pending.get("key") != key:
        log(f"忽略过期待发记录：{pending.get('key', '').split(':', 1)[0]}")

    _save_json(pending_path, {
        "key": key,
        "hash": digest,
        "text": content,
        "queued_at": _dt.datetime.now().isoformat(timespec="seconds"),
    })

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = post(
                webhook,
                json={"msg_type": "text", "content": {"text": content}},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            code = data.get("code", data.get("StatusCode"))
            if code != 0:
                message = data.get("msg", data.get("StatusMessage", "未知错误"))
                raise FeishuDeliveryError(f"code={code}: {message}")

            _save_json(sent_path, {
                "key": key,
                "hash": digest,
                "sent_at": _dt.datetime.now().isoformat(timespec="seconds"),
            })
            pending_path.unlink(missing_ok=True)
            return {"status": "sent", "key": key, "hash": digest, "attempts": attempt}
        except Exception as exc:
            last_error = exc
            log(f"飞书 Webhook 第 {attempt}/{retries} 次投递失败：{exc}")
            if attempt < retries:
                sleeper(1.5 * attempt)

    raise FeishuDeliveryError(f"飞书 Webhook 推送失败（已重试 {retries} 次）：{last_error}")


def push_feishu_webhook(content: str) -> dict:
    """通过飞书群机器人 Webhook 可靠投递日报。"""
    webhook = os.environ.get("FEISHU_WEBHOOK", "").strip()
    state_dir = Path(os.environ.get(
        "FEISHU_DAILY_STATE_DIR",
        str(Path(__file__).resolve().parent.parent / "outputs" / "feishu_daily_state"),
    ))
    retries = int(os.environ.get("FEISHU_DAILY_RETRIES", "3"))

    log(f"飞书 Webhook 推送纯文本消息（{len(content.encode('utf-8'))} 字节）")
    result = deliver_feishu_webhook(
        content,
        webhook=webhook,
        state_dir=state_dir,
        retries=retries,
    )
    if result["status"] == "already_sent":
        log("飞书日报今日已发送，幂等跳过 ✓")
    else:
        log(f"飞书 Webhook 推送成功（第 {result['attempts']} 次）✓")
    return result


def push_feishu_bot(content: str) -> None:
    """用飞书应用机器人直连 OpenAPI，供云端定时任务使用。"""
    chat_id = os.environ.get("FEISHU_CHAT_ID", "").strip()
    app_id = os.environ.get("FEISHU_APP_ID", "").strip()
    app_secret = os.environ.get("FEISHU_APP_SECRET", "").strip()
    missing = [name for name, value in {
        "FEISHU_CHAT_ID": chat_id,
        "FEISHU_APP_ID": app_id,
        "FEISHU_APP_SECRET": app_secret,
    }.items() if not value]
    if missing:
        raise SystemExit(f"缺 {'、'.join(missing)}，无法由飞书机器人推送")

    token_resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=30,
    )
    token_resp.raise_for_status()
    token_data = token_resp.json()
    if token_data.get("code") != 0 or not token_data.get("tenant_access_token"):
        raise SystemExit(f"获取飞书机器人 token 失败：{token_data.get('msg', '未知错误')}")

    log(f"飞书机器人推送纯文本消息（{len(content.encode('utf-8'))} 字节）")
    send_resp = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages",
        params={"receive_id_type": "chat_id"},
        headers={"Authorization": f"Bearer {token_data['tenant_access_token']}"},
        json={"receive_id": chat_id, "msg_type": "text", "content": json.dumps({"text": content}, ensure_ascii=False)},
        timeout=30,
    )
    send_resp.raise_for_status()
    send_data = send_resp.json()
    if send_data.get("code") != 0:
        raise SystemExit(f"飞书机器人推送失败：{send_data.get('msg', '未知错误')}")
    log("飞书机器人推送成功 ✓")


def delivery_channels() -> list[str]:
    """解析目标渠道；默认保持旧的企微行为，避免影响既有群推送。"""
    raw = os.environ.get("GROUP_COPY_CHANNELS", "wework")
    channels = [item.strip().lower() for item in raw.split(",") if item.strip()]
    if not channels:
        raise SystemExit("GROUP_COPY_CHANNELS 不能为空")
    unsupported = set(channels) - {"wework", "feishu_webhook", "feishu_bot", "feishu_cli"}
    if unsupported:
        raise SystemExit(f"不支持的推送渠道：{', '.join(sorted(unsupported))}")
    return list(dict.fromkeys(channels))


def copy_output_path() -> Path:
    out = os.environ.get("GROUP_COPY_OUT", "").strip()
    return Path(out) if out else Path(__file__).resolve().parent.parent / "outputs" / "group_copy_latest.txt"


def save_copy(content: str) -> Path:
    """落盘企微文案（供 xhs-fab 等复用拉取；路径走 env GROUP_COPY_OUT，默认仓库 outputs/）。
    每次生成覆盖同名文件，保持「最新一份」语义。"""
    p = copy_output_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    log(f"已落盘: {p}")
    return p


def load_saved_copy() -> str:
    """读取早间任务已生成的社群文案，供 9:00 飞书任务原样复用。"""
    p = copy_output_path()
    if not p.exists():
        raise SystemExit(f"找不到已落盘社群文案：{p}")
    content = p.read_text(encoding="utf-8").strip()
    if not content:
        raise SystemExit(f"已落盘社群文案为空：{p}")
    log(f"复用已落盘文案：{p}")
    return content


def main():
    dry = "--dry-run" in sys.argv
    existing = "--existing" in sys.argv
    content = load_saved_copy() if existing else generate_copy()
    print("\n" + "=" * 40 + " 文案预览 " + "=" * 40)
    print(content)
    print("=" * 90)
    print(f"[长度] {len(content)} 字 / {len(content.encode('utf-8'))} 字节\n")
    if not existing:
        save_copy(content)  # 先落盘（dry-run 也落盘，供复用/排查）
    if dry:
        log("dry-run,未推送")
        return
    for channel in delivery_channels():
        if channel == "wework":
            push_wework(content)
        elif channel == "feishu_webhook":
            push_feishu_webhook(content)
        elif channel == "feishu_bot":
            push_feishu_bot(content)
        elif channel == "feishu_cli":
            push_feishu_cli(content)


if __name__ == "__main__":
    main()
