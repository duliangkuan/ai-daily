# Feishu Daily Reliable Delivery Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use the Code workflow and verify against the real Feishu group after deployment.

**Goal:** Make the 09:00 AI daily Feishu delivery retry transient failures, persist failed messages, avoid duplicates, and automatically retry at 09:05.

**Architecture:** Keep the existing saved-copy workflow. Add a small durable delivery state machine inside `push_group_copy.py`: write a pending record before delivery, retry the same webhook request up to three times, write a sent ledger on success, and skip a repeated same-day message. Run the same safe shell entry point at 09:00 and 09:05.

**Tech Stack:** Python 3, requests, unittest, cron, Feishu custom-bot webhook.

---

### Task 1: Tests

**Files:**
- Create: `tests/test_feishu_daily_delivery.py`

Cover success, transient retry, persistent failure queue, pending recovery, same-day idempotency, and full error-code reporting.

### Task 2: Reliable delivery state machine

**Files:**
- Modify: `scripts/push_group_copy.py`
- Modify: `scripts/push_feishu_daily.sh`

Keep credentials in environment files. Never write webhook values to state or logs.

### Task 3: Deployment and acceptance

1. Run the unit tests and Python syntax checks.
2. Commit and push the repository.
3. Pull the commit on `/root/ai-daily`.
4. Add a second cron entry at 09:05; repeated execution must be idempotent.
5. Replay today's saved copy once.
6. Read the active Feishu member group and confirm exactly one 2026-08-20 AI daily message.
