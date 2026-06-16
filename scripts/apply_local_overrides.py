#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "dist" / "StartUpAds_Selected.sgmodule"

BAIDU_MARKER = "# ===== 百度网盘 / baiduwangpan ====="
ACTIVITY_TOKEN = r"pan\.baidu\.com\/act\/api\/activityentry"
SPLASH_TOKEN = r"pan\.baidu\.com\/buy\/ad\/conf"
LOCAL_RULES = [
    r"^https:\/\/pan\.baidu\.com\/act\/api\/activityentry - reject-dict",
    r"^https:\/\/pan\.baidu\.com\/buy\/ad\/conf\?.*type=splashMode - reject-dict",
]

def main():
    lines = OUTPUT_PATH.read_text(encoding="utf-8").splitlines()
    out = []
    found = False
    for line in lines:
        if ACTIVITY_TOKEN in line or SPLASH_TOKEN in line:
            continue
        out.append(line)
        if line == BAIDU_MARKER:
            found = True
            out.extend(LOCAL_RULES)
    if not found:
        raise RuntimeError("Baidu Netdisk marker not found")
    OUTPUT_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("Applied Baidu Netdisk local overrides")

if __name__ == "__main__":
    main()
