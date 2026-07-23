"""Offline checks for Bilibili splash empty-structure responses."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "bilibili-splash-ads.js"
MODULE = ROOT / "modules" / "BilibiliFeedAds.sgmodule"
QX_LOCAL = ROOT / "quantumultx" / "StartUpAds_Local.conf"
HAR_PATH = Path("/Users/walve/Downloads/quantumult-x-2026-07-23-183452.har")


def pick_empty_body(url: str) -> dict:
    u = str(url or "")
    if "/splash/show" in u:
        return {"code": 0, "message": "OK", "ttl": 1, "data": {"show": []}}
    if "/splash/event/list2" in u or "/splash/event/list" in u:
        return {"code": 0, "message": "OK", "ttl": 1, "data": {"event_list": []}}
    if "/splash/brand/list" in u:
        return {
            "code": 0,
            "message": "OK",
            "ttl": 1,
            "data": {
                "pull_interval": 86400,
                "forcibly": 0,
                "rule": 0,
                "list": [],
                "preload": [],
                "has_new_splash_set": 0,
            },
        }
    return {
        "code": 0,
        "message": "OK",
        "ttl": 1,
        "data": {
            "max_time": 0,
            "min_interval": 86400,
            "pull_interval": 86400,
            "keep_ids": [],
            "list": [],
            "show": [],
        },
    }


class BilibiliSplashAdsTests(unittest.TestCase):
    def test_script_returns_structured_empty_not_bare_object(self):
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("show:[]", script.replace(" ", ""))
        self.assertIn("EMPTY_SHOW", script)
        self.assertIn("EMPTY_LIST", script)
        self.assertIn("EMPTY_BRAND", script)
        # Implementation must return structured JSON, not bare "{}"
        self.assertIn("JSON.stringify", script)
        self.assertIn("code: 0", script)

    def test_pick_empty_by_path(self):
        show = pick_empty_body("https://app.bilibili.com/x/v2/splash/show?x=1")
        self.assertEqual(show["data"]["show"], [])
        self.assertIn("code", show)

        listing = pick_empty_body("https://app.bilibili.com/x/v2/splash/list?x=1")
        self.assertEqual(listing["data"]["list"], [])
        self.assertEqual(listing["data"]["show"], [])

        brand = pick_empty_body("https://app.bilibili.com/x/v2/splash/brand/list")
        self.assertEqual(brand["data"]["list"], [])

        event = pick_empty_body("https://app.bilibili.com/x/v2/splash/event/list2")
        self.assertEqual(event["data"]["event_list"], [])

    def test_module_and_qx_use_splash_script(self):
        module = MODULE.read_text(encoding="utf-8")
        qx = QX_LOCAL.read_text(encoding="utf-8")
        self.assertIn("bilibili-splash-ads.js", module)
        self.assertIn("bilibili-splash-ads.js", qx)
        self.assertIn(r"splash\/", module)
        # reject-dict for bilibili splash should be gone
        self.assertNotRegex(
            qx,
            re.compile(
                r"app\\.bili.*splash.*reject-dict",
                re.I,
            ),
        )

    def test_latest_splash_har_was_reject_dict_empty(self):
        """Document that the comic splash HAR already hit reject-dict '{}'."""
        if not HAR_PATH.is_file():
            self.skipTest("splash HAR not present")
        import base64
        import gzip
        from urllib.parse import urlparse

        har = json.loads(HAR_PATH.read_text(encoding="utf-8"))
        saw = 0
        for entry in har["log"]["entries"]:
            path = urlparse(entry["request"]["url"]).path
            if "/splash/" not in path:
                continue
            content = entry["response"].get("content") or {}
            text = content.get("text")
            if content.get("encoding") == "base64" and text:
                raw = base64.b64decode(text)
                try:
                    raw = gzip.decompress(raw)
                except OSError:
                    pass
                text = raw.decode("utf-8", errors="replace")
            if text is None:
                continue
            saw += 1
            # Previous reject-dict behavior observed in capture
            self.assertEqual(text.strip(), "{}")
            # Improved body must not be bare {}
            improved = json.dumps(pick_empty_body(entry["request"]["url"]), ensure_ascii=False)
            self.assertNotEqual(improved, "{}")
            payload = json.loads(improved)
            self.assertEqual(payload["code"], 0)
            self.assertIsInstance(payload["data"], dict)
        self.assertGreaterEqual(saw, 1)


if __name__ == "__main__":
    unittest.main()
