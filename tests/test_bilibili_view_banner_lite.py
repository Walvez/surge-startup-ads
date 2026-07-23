"""Offline checks for lightweight under-player banner filtering."""

from __future__ import annotations

import base64
import gzip
import json
import struct
import unittest
import zlib
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "bilibili-view-banner-lite.js"
MODULE = ROOT / "modules" / "BilibiliFeedAds.sgmodule"
QX_LOCAL = ROOT / "quantumultx" / "StartUpAds_Local.conf"
VIEW_HAR = Path("/Users/walve/Downloads/quantumult-x-2026-07-23-185829.har")

SCAN_MARKERS = [
    b"relatedvideo.cm",
    b"sycp/sanlian",
    b"sycp/mgk",
    "立即下载".encode(),
    "查看详情".encode(),
    "了解更多".encode(),
    b"bilibili.ad.v1.",
    b"AdsControlDto",
    b"SourceContentDto",
]
CTA_LABELS = [
    "立即下载".encode(),
    "查看详情".encode(),
    "了解更多".encode(),
    "立即打开".encode(),
    "去看看".encode(),
]

DROP_MARKERS = [
    b"sycp/sanlian",
    b"sycp/app_icon",
    b"sycp/mgk",
    b"relatedvideo.cm",
    b"united.player-video-detail.relatedvideo.cm",
    b"from_spmid=united.player-video-detail.relatedvideo",
    b"adtrack.qianwen.com",
    b"cm.bilibili.com/ldad",
    b"unet.quark.cn/v3/ad",
    b"bilibili.ad.v1.AdsControlDto",
    b"bilibili.ad.v1.SourceContentDto",
    b"type.googleapis.com/bilibili.ad",
    b"#9499A0FF",
    b"#757A81FF",
    b"sycp_android_id",
    b"sycp_ip_before",
    b"sycp_ip=",
]
LABEL_AD = "广告".encode()
LABEL_PLAY = "播放".encode()
RESIDUAL_AD_MAX_LEN = 25000


def has_scan_marker(data: bytes) -> bool:
    return any(m in data for m in SCAN_MARKERS)


def has_cta(data: bytes) -> bool:
    return any(c in data for c in CTA_LABELS)


def is_residual_ad_card(data: bytes) -> bool:
    if len(data) > RESIDUAL_AD_MAX_LEN:
        return False
    has_store = b"apps.apple.com" in data or b"itunes.apple.com" in data
    if has_store and (
        b"sycp" in data
        or LABEL_PLAY in data
        or "隐私协议".encode() in data
        or b"com." in data
    ):
        return True
    if LABEL_AD not in data:
        return False
    if LABEL_PLAY in data and (
        b"vupload" in data
        or b"bfs/archive" in data
        or b"sycp/" in data
        or has_cta(data)
    ):
        return True
    if b"sycp/mng" in data and "屏蔽广告".encode() in data:
        return True
    if "评分".encode() in data and (has_store or b"sycp" in data):
        return True
    return False


def has_drop_marker(data: bytes) -> bool:
    if any(m in data for m in DROP_MARKERS):
        return True
    if has_cta(data) and LABEL_AD in data:
        return True
    if has_cta(data) and (
        b"apps.apple.com" in data
        or b"itunes.apple.com" in data
        or b"adtrack." in data
        or b"sycp/" in data
    ):
        return True
    if b"sycp/face" in data and LABEL_AD in data:
        return True
    if b"apps.apple.com" in data and LABEL_AD in data:
        return True
    if is_residual_ad_card(data):
        return True
    return False


def read_varint(buf: bytes, i: int) -> tuple[int, int]:
    result = 0
    shift = 0
    while i < len(buf):
        b = buf[i]
        i += 1
        result |= (b & 0x7F) << shift
        if b < 0x80:
            return result, i
        shift += 7
        if shift > 35:
            raise ValueError("varint too long")
    raise ValueError("truncated varint")


def write_varint(n: int) -> bytes:
    out = bytearray()
    n &= 0xFFFFFFFF
    while n > 0x7F:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    out.append(n & 0x7F)
    return bytes(out)


def clean_message(buf: bytes) -> bytes:
    out = bytearray()
    i = 0
    n = len(buf)
    while i < n:
        start = i
        try:
            tag, i = read_varint(buf, i)
        except ValueError:
            out.extend(buf[start:])
            break
        field_number = tag >> 3
        wire = tag & 7
        if field_number == 0:
            out.extend(buf[start:])
            break
        if wire == 0:
            try:
                _, i2 = read_varint(buf, i)
            except ValueError:
                out.extend(buf[start:])
                break
            out.extend(buf[start:i2])
            i = i2
        elif wire == 1:
            if i + 8 > n:
                out.extend(buf[start:])
                break
            out.extend(buf[start : i + 8])
            i += 8
        elif wire == 5:
            if i + 4 > n:
                out.extend(buf[start:])
                break
            out.extend(buf[start : i + 4])
            i += 4
        elif wire == 2:
            try:
                length, i2 = read_varint(buf, i)
            except ValueError:
                out.extend(buf[start:])
                break
            if i2 + length > n:
                out.extend(buf[start:])
                break
            data = buf[i2 : i2 + length]
            i = i2 + length
            if has_drop_marker(data):
                cleaned = clean_message(data)
                if has_drop_marker(cleaned):
                    continue
                data = cleaned
            out.extend(write_varint(tag))
            out.extend(write_varint(len(data)))
            out.extend(data)
        else:
            out.extend(buf[start:])
            break
    return bytes(out)


def get_raw(resp: dict) -> bytes | None:
    content = resp.get("content") or {}
    text = content.get("text")
    if text is None:
        return None
    if content.get("encoding") == "base64":
        raw = base64.b64decode(text)
        try:
            return gzip.decompress(raw)
        except OSError:
            return raw
    if isinstance(text, str):
        return text.encode("utf-8", errors="replace")
    return text


def decode_grpc_message(raw: bytes) -> bytes:
    compressed = raw[0]
    length = struct.unpack(">I", raw[1:5])[0]
    payload = raw[5 : 5 + length]
    if compressed == 1:
        try:
            return gzip.decompress(payload)
        except OSError:
            try:
                return zlib.decompress(payload, -zlib.MAX_WBITS)
            except zlib.error:
                return zlib.decompress(payload)
    return payload


class BilibiliViewBannerLiteTests(unittest.TestCase):
    def test_module_is_narrow_no_grpc_hostname(self):
        script = SCRIPT.read_text(encoding="utf-8")
        module = MODULE.read_text(encoding="utf-8")
        qx = QX_LOCAL.read_text(encoding="utf-8")

        self.assertIn("viewunite", module)
        self.assertIn("bilibili-view-banner-lite.js", module)
        self.assertIn("sycp", module)
        self.assertIn("app_icon", module)
        self.assertIn("bilibili-view-banner-lite.js", qx)
        self.assertIn("sycp", qx)
        # app.biliapi.net allowed; grpc host not.
        self.assertIn(r"app\.bili(bili\.com|api\.net)", module)

        mitm_line = [ln for ln in module.splitlines() if "hostname" in ln.lower()][-1]
        self.assertNotIn("grpc.biliapi.net", mitm_line)
        self.assertNotIn("grpc.biliapi.net", qx.split("[mitm]")[-1] if "[mitm]" in qx else qx)
        self.assertNotIn("MainList", script)
        self.assertNotIn("grpc.biliapi.net/bilibili", module)
        self.assertIn("hasScanMarker", script)
        self.assertIn("relatedvideo.cm", script)
        self.assertIn("查看详情", script)

    def test_har_app_bilibili_view_strips_banner_markers(self):
        if not VIEW_HAR.is_file():
            self.skipTest("View HAR not present")

        har = json.loads(VIEW_HAR.read_text(encoding="utf-8"))
        matched = 0
        for entry in har["log"]["entries"]:
            url = entry["request"]["url"]
            host = urlparse(url).netloc
            path = urlparse(url).path
            if host not in ("app.bilibili.com", "app.biliapi.net"):
                continue
            if not path.endswith("/bilibili.app.viewunite.v1.View/View"):
                continue
            raw = get_raw(entry["response"])
            if not raw or len(raw) < 2000 or b"400 Bad Request" in raw:
                continue
            msg = decode_grpc_message(raw)
            if not has_scan_marker(msg):
                # Fast path: would return original unchanged
                cleaned = clean_message(msg)
                self.assertEqual(cleaned, msg)
                continue
            matched += 1
            cleaned = clean_message(msg)
            self.assertNotIn(b"relatedvideo.cm", cleaned)
            self.assertNotIn(b"sycp/sanlian", cleaned)
            self.assertNotIn(b"sycp/mgk", cleaned)
            self.assertNotIn(b"AdsControlDto", cleaned)
            self.assertNotIn(b"SourceContentDto", cleaned)
            self.assertNotIn("立即下载".encode(), cleaned)
            self.assertIn("简介".encode(), cleaned)
            self.assertLess(len(cleaned), len(msg))

        self.assertGreaterEqual(matched, 1)

    def test_cold_start_har_strips_quark_banner(self):
        cold = Path("/Users/walve/Downloads/quantumult-x-2026-07-23-193127.har")
        if not cold.is_file():
            self.skipTest("cold-start HAR not present")

        har = json.loads(cold.read_text(encoding="utf-8"))
        matched = 0
        for entry in har["log"]["entries"]:
            url = entry["request"]["url"]
            host = urlparse(url).netloc
            path = urlparse(url).path
            if host not in ("app.bilibili.com", "app.biliapi.net"):
                continue
            if not path.endswith("/bilibili.app.viewunite.v1.View/View"):
                continue
            raw = get_raw(entry["response"])
            if not raw or len(raw) < 5000 or b"400 Bad Request" in raw:
                continue
            msg = decode_grpc_message(raw)
            if "没有工作".encode() not in msg and "夸克AI".encode() not in msg:
                continue
            matched += 1
            cleaned = clean_message(msg)
            self.assertNotIn("没有工作".encode(), cleaned)
            self.assertNotIn("夸克AI".encode(), cleaned)
            self.assertNotIn(b"AdsControlDto", cleaned)
            self.assertIn("简介".encode(), cleaned)

        self.assertGreaterEqual(matched, 1)

    def test_latest_har_strips_reverse1999_banner(self):
        """Screenshot-aligned HAR: 重返未来横幅 must not survive clean."""
        latest = Path("/Users/walve/Downloads/quantumult-x-2026-07-23-194219.har")
        if not latest.is_file():
            self.skipTest("latest HAR not present")

        har = json.loads(latest.read_text(encoding="utf-8"))
        matched = 0
        for entry in har["log"]["entries"]:
            url = entry["request"]["url"]
            host = urlparse(url).netloc
            path = urlparse(url).path
            if host not in ("app.bilibili.com", "app.biliapi.net"):
                continue
            if not path.endswith("/bilibili.app.viewunite.v1.View/View"):
                continue
            raw = get_raw(entry["response"])
            if not raw or len(raw) < 5000 or b"400 Bad Request" in raw:
                continue
            msg = decode_grpc_message(raw)
            if "重返未来".encode() not in msg and "双生舞伶".encode() not in msg:
                continue
            matched += 1
            cleaned = clean_message(msg)
            self.assertNotIn("重返未来".encode(), cleaned)
            self.assertNotIn("双生舞伶".encode(), cleaned)
            self.assertNotIn(b"AdsControlDto", cleaned)
            self.assertNotIn(b"relatedvideo.cm", cleaned)
            self.assertIn("简介".encode(), cleaned)

        self.assertGreaterEqual(matched, 1)

    def test_layer_a_cdn_rule_present(self):
        module = MODULE.read_text(encoding="utf-8")
        qx = QX_LOCAL.read_text(encoding="utf-8")
        self.assertIn("sanlian|mgk|app_icon", module)
        self.assertIn("sycp", qx)
        self.assertIn("app_icon", qx)
        self.assertIn("reject", qx.lower())


if __name__ == "__main__":
    unittest.main()
