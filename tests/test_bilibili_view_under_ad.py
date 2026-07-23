"""Offline checks for the narrow under-player ViewUnite ad filter."""

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
SCRIPT = ROOT / "scripts" / "bilibili-view-under-ad.js"
MODULE = ROOT / "modules" / "BilibiliFeedAds.sgmodule"
VIEW_HAR = Path("/Users/walve/Downloads/quantumult-x-2026-07-23-182318.har")

MARKERS = [
    b"sycp/sanlian",
    b"sycp/app_icon",
    b"sycp/mgk",
    b"relatedvideo.cm",
    b"united.player-video-detail.relatedvideo.cm",
    b"from_spmid=united.player-video-detail.relatedvideo",
    b"adtrack.qianwen.com",
    b"cm.bilibili.com/ldad",
    b"unet.quark.cn/v3/ad",
]
CTA = "立即下载".encode()
LABEL_AD = "广告".encode()


def has_ad_marker(data: bytes) -> bool:
    if any(m in data for m in MARKERS):
        return True
    if CTA in data and (
        b"apps.apple.com" in data
        or b"itunes.apple.com" in data
        or b"adtrack." in data
        or b"sycp/" in data
        or LABEL_AD in data
    ):
        return True
    if b"sycp/face" in data and LABEL_AD in data:
        return True
    if b"sycp/mng" in data and "屏蔽广告".encode() in data:
        return True
    if b"apps.apple.com" in data and LABEL_AD in data:
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
            if has_ad_marker(data):
                cleaned = clean_message(data)
                if has_ad_marker(cleaned):
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
    if len(raw) < 5:
        raise ValueError("too short")
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


class BilibiliViewUnderAdTests(unittest.TestCase):
    def test_script_is_narrow_viewunite_only(self):
        script = SCRIPT.read_text(encoding="utf-8")
        module = MODULE.read_text(encoding="utf-8")
        self.assertIn("viewunite", script.lower() + module.lower())
        self.assertIn("sycp/sanlian", script)
        self.assertIn("relatedvideo.cm", script)
        self.assertIn("立即下载", script)
        self.assertIn("binary-body-mode=true", module)
        self.assertNotIn("MainList", script)
        self.assertNotIn("DynAll", script)
        self.assertNotIn("feed/index", script)

    def test_view_har_strips_under_player_markers(self):
        if not VIEW_HAR.is_file():
            self.skipTest("View HAR not present on this machine")

        har = json.loads(VIEW_HAR.read_text(encoding="utf-8"))
        matched = 0
        for entry in har["log"]["entries"]:
            path = urlparse(entry["request"]["url"]).path
            if not path.endswith("/bilibili.app.viewunite.v1.View/View"):
                continue
            raw = get_raw(entry["response"])
            if not raw or len(raw) < 2000 or b"400 Bad Request" in raw:
                continue
            msg = decode_grpc_message(raw)
            if not any(m in msg for m in (b"sycp/sanlian", b"relatedvideo.cm", CTA)):
                continue
            matched += 1
            cleaned = clean_message(msg)
            self.assertNotIn(b"sycp/sanlian", cleaned)
            self.assertNotIn(b"sycp/mgk", cleaned)
            self.assertNotIn(b"relatedvideo.cm", cleaned)
            self.assertNotIn(b"adtrack.qianwen.com", cleaned)
            self.assertNotIn(CTA, cleaned)
            # Core page content survives.
            self.assertIn("简介".encode(), cleaned)
            self.assertIn("万播放".encode(), cleaned)
            self.assertLess(len(cleaned), len(msg))

        self.assertGreaterEqual(matched, 1)


if __name__ == "__main__":
    unittest.main()
