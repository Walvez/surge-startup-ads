"""Offline checks for the narrow Bilibili feed-ad filter."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "bilibili_feed_index.sample.json"
SCRIPT = ROOT / "scripts" / "bilibili-feed-ads.js"
MODULE = ROOT / "modules" / "BilibiliFeedAds.sgmodule"
QX_LOCAL = ROOT / "quantumultx" / "StartUpAds_Local.conf"
HAR_PATH = Path("/Users/walve/Downloads/quantumult-x-2026-07-23-160037.har")

TARGET_CARD_GOTOS = frozenset({"ad_av", "ad_web_s", "ad_web_gif"})
TARGET_BADGE_TEXT = ("创作推广", "会员购", "App Store", "立即探索 App Store")


def collect_text(value, out: list[str]) -> None:
    if value is None:
        return
    if isinstance(value, str):
        if value:
            out.append(value)
        return
    if isinstance(value, list):
        for item in value:
            collect_text(item, out)
        return
    if isinstance(value, dict):
        for key in ("text", "title", "desc", "name", "label"):
            raw = value.get(key)
            if isinstance(raw, str) and raw:
                out.append(raw)


def has_target_badge(item: dict) -> bool:
    texts: list[str] = []
    collect_text(item.get("desc"), texts)
    collect_text(item.get("desc_button"), texts)
    collect_text(item.get("cover_right_text"), texts)
    collect_text(item.get("goto_icon"), texts)
    collect_text(item.get("badges"), texts)
    collect_text(item.get("badge"), texts)
    ad_info = item.get("ad_info") or {}
    collect_text(ad_info.get("creative_content"), texts)
    joined = " ".join(texts)
    return any(badge in joined for badge in TARGET_BADGE_TEXT)


def is_target_feed_ad(item: dict) -> bool:
    if not isinstance(item, dict):
        return False
    card_goto = str(item.get("card_goto") or "")
    if card_goto in TARGET_CARD_GOTOS:
        return True
    if item.get("card_type") == "cm_v2" and has_target_badge(item):
        return True
    return False


def filter_feed_items(items: list) -> list:
    return [item for item in items if not is_target_feed_ad(item)]


class BilibiliFeedAdsTests(unittest.TestCase):
    def test_sample_fixture_removes_only_target_ads(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        items = payload["data"]["items"]
        filtered = filter_feed_items(items)

        gotos = [item.get("card_goto") for item in filtered]
        self.assertNotIn("ad_av", gotos)
        self.assertNotIn("ad_web_s", gotos)
        self.assertNotIn("ad_web_gif", gotos)
        self.assertIn("banner", gotos)
        self.assertIn("av", gotos)
        self.assertIn("bangumi", gotos)
        self.assertEqual(len(filtered), 4)

        titles = [item.get("title") for item in filtered]
        self.assertIn("普通推荐视频", titles)
        self.assertNotIn("立即探索 App Store", titles)
        self.assertNotIn("当我用AI生成喜欢的角色（自定义）", titles)

    def test_badge_fallback_catches_cm_v2_without_known_goto(self):
        item = {
            "card_type": "cm_v2",
            "card_goto": "future_slot",
            "badge": {"text": "会员购"},
        }
        self.assertTrue(is_target_feed_ad(item))

    def test_normal_video_kept(self):
        item = {
            "card_type": "small_cover_v2",
            "card_goto": "av",
            "title": "普通视频",
            "desc": "UP主",
        }
        self.assertFalse(is_target_feed_ad(item))

    def test_script_and_module_are_narrow(self):
        script = SCRIPT.read_text(encoding="utf-8")
        module = MODULE.read_text(encoding="utf-8")
        qx = QX_LOCAL.read_text(encoding="utf-8")

        self.assertIn("ad_av", script)
        self.assertIn("ad_web_s", script)
        self.assertIn("ad_web_gif", script)
        self.assertIn("创作推广", script)
        self.assertIn("会员购", script)
        self.assertIn("App Store", script)
        self.assertIn(r"feed\/index", module)
        self.assertIn("bilibili-feed-ads.js", module)
        self.assertIn("bilibili-view-under-ad.js", module)
        self.assertIn("viewunite", module)
        self.assertIn(r"feed\/index", qx)
        self.assertIn("bilibili-feed-ads.js", qx)
        self.assertIn("bilibili-view-under-ad.js", qx)
        self.assertIn("viewunite", qx)
        # Must not attach broad B 站 hooks (comments / dynamic / full ADBlock).
        self.assertNotIn("splash", module)
        self.assertNotIn("dynamic", module.lower())
        self.assertNotIn("reply", module.lower())
        self.assertNotIn("MainList", module)

    def test_har_real_feed_if_present(self):
        if not HAR_PATH.is_file():
            self.skipTest("HAR capture not present on this machine")

        import base64
        import gzip
        from urllib.parse import urlparse

        har = json.loads(HAR_PATH.read_text(encoding="utf-8"))

        def body_text(entry: dict) -> str | None:
            content = entry["response"].get("content") or {}
            text = content.get("text")
            if text is None:
                return None
            if content.get("encoding") == "base64":
                raw = base64.b64decode(text)
                try:
                    raw = gzip.decompress(raw)
                except OSError:
                    pass
                return raw.decode("utf-8", errors="replace")
            return text

        matched = 0
        for entry in har["log"]["entries"]:
            path = urlparse(entry["request"]["url"]).path
            if not path.endswith("/x/v2/feed/index"):
                continue
            text = body_text(entry)
            if not text:
                continue
            payload = json.loads(text)
            items = (payload.get("data") or {}).get("items") or []
            if not items:
                continue
            matched += 1
            before_gotos = [item.get("card_goto") for item in items]
            filtered = filter_feed_items(items)
            after_gotos = [item.get("card_goto") for item in filtered]

            self.assertNotIn("ad_av", after_gotos)
            self.assertNotIn("ad_web_s", after_gotos)
            self.assertNotIn("ad_web_gif", after_gotos)
            # Banner and normal videos remain.
            if "banner" in before_gotos:
                self.assertIn("banner", after_gotos)
            self.assertTrue(any(g in ("av", "vertical_av", "picture", "bangumi") for g in after_gotos))
            if any(g in TARGET_CARD_GOTOS for g in before_gotos):
                self.assertLess(len(filtered), len(items))

        self.assertGreaterEqual(matched, 1)

    def test_new_apple_har_removes_ad_web_gif(self):
        apple_har = Path("/Users/walve/Downloads/quantumult-x-2026-07-23-181638.har")
        if not apple_har.is_file():
            self.skipTest("Apple feed HAR not present on this machine")

        import base64
        import gzip
        from urllib.parse import urlparse

        har = json.loads(apple_har.read_text(encoding="utf-8"))

        def body_text(entry: dict) -> str | None:
            content = entry["response"].get("content") or {}
            text = content.get("text")
            if text is None:
                return None
            if content.get("encoding") == "base64":
                raw = base64.b64decode(text)
                try:
                    raw = gzip.decompress(raw)
                except OSError:
                    pass
                return raw.decode("utf-8", errors="replace")
            return text

        saw_gif = 0
        for entry in har["log"]["entries"]:
            if not urlparse(entry["request"]["url"]).path.endswith("/x/v2/feed/index"):
                continue
            text = body_text(entry)
            if not text:
                continue
            payload = json.loads(text)
            items = (payload.get("data") or {}).get("items") or []
            if not any(item.get("card_goto") == "ad_web_gif" for item in items):
                continue
            saw_gif += 1
            filtered = filter_feed_items(items)
            after_gotos = [item.get("card_goto") for item in filtered]
            self.assertNotIn("ad_web_gif", after_gotos)
            self.assertTrue(any(g in ("av", "bangumi") for g in after_gotos))
            self.assertLess(len(filtered), len(items))

        self.assertGreaterEqual(saw_gif, 1)


if __name__ == "__main__":
    unittest.main()
