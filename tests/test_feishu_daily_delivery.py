import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import push_group_copy as module


class FakeResponse:
    def __init__(self, payload, status_error=None):
        self.payload = payload
        self.status_error = status_error

    def raise_for_status(self):
        if self.status_error:
            raise self.status_error

    def json(self):
        return self.payload


class FeishuDailyDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.state = Path(self.temp.name)
        self.today = date(2026, 8, 20)
        self.text = "🌅 AI日报 · 8月20日\n\n测试正文"

    def tearDown(self):
        self.temp.cleanup()

    def deliver(self, post, retries=3):
        return module.deliver_feishu_webhook(
            self.text,
            webhook="https://example.invalid/hook",
            state_dir=self.state,
            post=post,
            retries=retries,
            sleeper=lambda _seconds: None,
            today=self.today,
        )

    def test_success_records_sent_and_clears_pending(self):
        post = Mock(return_value=FakeResponse({"code": 0, "msg": "success"}))
        result = self.deliver(post)
        self.assertEqual("sent", result["status"])
        self.assertEqual(1, post.call_count)
        self.assertTrue((self.state / "sent.json").exists())
        self.assertFalse((self.state / "pending.json").exists())

    def test_transient_internal_error_is_retried(self):
        post = Mock(side_effect=[
            FakeResponse({"code": 19002, "msg": "internal error"}),
            FakeResponse({"code": 0, "msg": "success"}),
        ])
        result = self.deliver(post)
        self.assertEqual("sent", result["status"])
        self.assertEqual(2, post.call_count)

    def test_persistent_failure_is_queued_with_error_code(self):
        post = Mock(return_value=FakeResponse({"code": 19002, "msg": "internal error"}))
        with self.assertRaisesRegex(module.FeishuDeliveryError, "19002.*internal error"):
            self.deliver(post)
        self.assertEqual(3, post.call_count)
        pending = json.loads((self.state / "pending.json").read_text(encoding="utf-8"))
        self.assertEqual(self.text, pending["text"])
        self.assertNotIn("webhook", pending)

    def test_pending_message_recovers_on_next_invocation(self):
        failing = Mock(return_value=FakeResponse({"code": 19002, "msg": "internal error"}))
        with self.assertRaises(module.FeishuDeliveryError):
            self.deliver(failing, retries=1)
        succeeding = Mock(return_value=FakeResponse({"code": 0, "msg": "success"}))
        result = self.deliver(succeeding)
        self.assertEqual("sent", result["status"])
        self.assertFalse((self.state / "pending.json").exists())

    def test_same_day_same_message_is_idempotent(self):
        post = Mock(return_value=FakeResponse({"code": 0, "msg": "success"}))
        self.assertEqual("sent", self.deliver(post)["status"])
        self.assertEqual("already_sent", self.deliver(post)["status"])
        self.assertEqual(1, post.call_count)


if __name__ == "__main__":
    unittest.main()
