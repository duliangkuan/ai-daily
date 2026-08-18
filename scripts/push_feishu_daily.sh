#!/bin/bash
# 每天 09:00 复用 08:00 已生成的社群文案，推送风云AI学习社会员飞书群。
set -euo pipefail

ENV_FILE=/root/ai-daily.env
COPY_FILE=/root/ai-daily/outputs/group_copy_latest.txt
PY=/root/TrendRadar/.venv/bin/python
SCRIPT=/root/ai-daily/scripts/push_group_copy.py
LOG=/root/daily.log

if [ ! -s "$COPY_FILE" ]; then
  echo "[FAIL] feishu_daily: 社群文案不存在或为空" >> "$LOG"
  exit 1
fi

if [ "$(date -r "$COPY_FILE" +%F)" != "$(date +%F)" ]; then
  echo "[FAIL] feishu_daily: 社群文案不是今天生成，跳过推送" >> "$LOG"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a
export PYTHONIOENCODING=utf-8
export GROUP_COPY_CHANNELS=feishu_webhook

"$PY" -X utf8 "$SCRIPT" --existing >> "$LOG" 2>&1
echo "[ok] feishu_daily" >> "$LOG"
