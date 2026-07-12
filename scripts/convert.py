#!/usr/bin/env python3
"""Build one Surge module from selected Quantumult X blocks and supplemental Surge modules."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "apps.json"
OUTPUT_PATH = ROOT / "dist" / "StartUpAds_Selected.sgmodule"
USER_AGENT = "surge-startup-ads/1.0 (+https://github.com/Walvez/surge-startup-ads)"

SUPPORTED_SECTIONS = (
    "Rule",
    "URL Rewrite",
    "Map Local",
    "Body Rewrite",
    "Header Rewrite",
    "Script",
)

MARKER_RE = re.compile(r"^\s*#\s*>\s*(.+?)\s*$")
SECTION_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")


class BuildError(RuntimeError):
    pass


def fetch_text(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
    return raw.decode("utf-8-sig", errors="replace").replace("\r\n", "\n")


def fetch_first(urls: Iterable[str]) -> tuple[str, str]:
    errors: list[str] = []
    for url in urls:
        try:
            text = fetch_text(url)
            if "# >" not in text or "hostname =" not in text:
                raise BuildError("downloaded content does not look like StartUpAds.conf")
            return url, text
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{url}: {exc}")
    raise BuildError("all primary source URLs failed:\n" + "\n".join(errors))


def normalize_marker(value: str) -> str:
    value = value.strip().strip("[]")
    value = re.sub(r"\s+", "", value)
    return value.casefold()


def split_qx_blocks(text: str) -> dict[str, list[str]]:
    blocks: dict[str, list[str]] = defaultdict(list)
    current: str | None = None
    for line in text.splitlines():
        match = MARKER_RE.match(line)
        if match:
            current = normalize_marker(match.group(1))
            blocks[current].append(line.rstrip())
            continue
        if current is not None:
            if re.match(r"^\s*#\s*=+", line):
                current = None
                continue
            blocks[current].append(line.rstrip())
    return dict(blocks)


def unique_name(prefix: str, counter: int) -> str:
    safe = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff]+", "_", prefix).strip("_")
    return f"{safe}_{counter}"


def convert_qx_line(
    line: str,
    app_name: str,
    counters: dict[str, int],
) -> tuple[str | None, str | None, str | None]:
    """Return (section, converted_line, warning)."""
    raw = line.strip()
    if not raw or raw.startswith("#") or raw.startswith(";"):
        return None, None, None

    # URL reject actions.
    match = re.match(
        r"^(.*?)\s+url\s+(reject(?:-[A-Za-z0-9_-]+)?)\s*$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        pattern, action = match.groups()
        return "URL Rewrite", f"{pattern.strip()} - {action.lower()}", None

    # QX response/request scripts.
    match = re.match(
        r"^(.*?)\s+url\s+script-(request|response)-(body|header)\s+(\S+)(?:\s+.*)?$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        pattern, direction, content_kind, script_url = match.groups()
        counters["script"] += 1
        name = unique_name(app_name, counters["script"])
        requires_body = "true" if content_kind.lower() == "body" else "false"
        script_type = "http-request" if direction.lower() == "request" else "http-response"
        value = (
            f"{name} = type={script_type}, pattern={pattern.strip()}, "
            f"requires-body={requires_body}, max-size=-1, timeout=60, "
            f"script-path={script_url}"
        )
        return "Script", value, None

    # QX analyze-echo response script.
    match = re.match(
        r"^(.*?)\s+url\s+script-analyze-echo-response\s+(\S+)(?:\s+.*)?$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        pattern, script_url = match.groups()
        counters["script"] += 1
        name = unique_name(app_name, counters["script"])
        value = (
            f"{name} = type=http-response, pattern={pattern.strip()}, "
            f"requires-body=true, max-size=-1, timeout=60, "
            f"script-path={script_url}"
        )
        return "Script", value, None

    # QX body replacements.
    match = re.match(
        r"^(.*?)\s+url\s+response-body\s+(.+?)\s+response-body\s+(.+)$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        pattern, search, replacement = match.groups()
        return (
            "Body Rewrite",
            f"http-response {pattern.strip()} {search.strip()} {replacement.strip()}",
            None,
        )

    match = re.match(
        r"^(.*?)\s+url\s+request-body\s+(.+?)\s+request-body\s+(.+)$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        pattern, search, replacement = match.groups()
        return (
            "Body Rewrite",
            f"http-request {pattern.strip()} {search.strip()} {replacement.strip()}",
            None,
        )

    # QX JSON jq response modifier.
    match = re.match(
        r"^(.*?)\s+url\s+jsonjq-response-body\s+(.+)$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        pattern, jq = match.groups()
        return "Body Rewrite", f"http-response-jq {pattern.strip()} {jq.strip()}", None

    # QX host / host-suffix rules.
    match = re.match(
        r"^\s*(host|host-suffix)\s*,\s*([^,]+)\s*,\s*([^,\s]+)",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        kind, domain, policy = match.groups()
        surge_kind = "DOMAIN" if kind.lower() == "host" else "DOMAIN-SUFFIX"
        policy_lower = policy.lower()
        surge_policy = "DIRECT" if policy_lower == "direct" else "REJECT"
        return "Rule", f"{surge_kind},{domain.strip()},{surge_policy}", None

    return None, None, f"{app_name}: unsupported selected rule: {raw}"


def append_unique(target: list[str], line: str) -> None:
    if line not in target:
        target.append(line)


def parse_hostname_line(line: str) -> list[str]:
    match = re.match(r"^\s*hostname\s*=\s*(?:%APPEND%\s*)?(.*)$", line, re.I)
    if not match:
        return []
    return [item.strip() for item in match.group(1).split(",") if item.strip()]


def merge_surge_module(
    text: str,
    source_name: str,
    sections: dict[str, list[str]],
    hostnames: list[str],
    script_counter: list[int],
) -> None:
    current: str | None = None
    for original in text.splitlines():
        line = original.rstrip()
        section_match = SECTION_RE.match(line)
        if section_match:
            current = section_match.group(1).strip()
            continue
        if current == "MITM":
            for host in parse_hostname_line(line):
                append_unique(hostnames, host)
            continue
        if current not in SUPPORTED_SECTIONS:
            continue
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            append_unique(sections[current], f"# [{source_name}] {line.lstrip('# ').strip()}")
            continue
        if current == "Script" and "=" in line:
            _, rhs = line.split("=", 1)
            script_counter[0] += 1
            line = f"{unique_name(source_name, script_counter[0])} ={rhs}"
        append_unique(sections[current], line)


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    strict = bool(config.get("strict_selected_syntax", True))
    source_url, source_text = fetch_first(config["source_urls"])
    source_sha = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    blocks = split_qx_blocks(source_text)

    sections: dict[str, list[str]] = {name: [] for name in SUPPORTED_SECTIONS}
    hostnames: list[str] = []
    warnings: list[str] = []
    found_apps: list[str] = []
    counters = {"script": 0}

    for app_name, spec in config["apps"].items():
        matched_any = False
        for marker in spec.get("markers", []):
            block = blocks.get(normalize_marker(marker))
            if not block:
                continue
            matched_any = True
            append_unique(sections["URL Rewrite"], f"# ===== {app_name} / {marker} =====")
            for line in block:
                section, converted, warning = convert_qx_line(line, app_name, counters)
                if warning:
                    warnings.append(warning)
                if section and converted:
                    append_unique(sections[section], converted)
        if matched_any:
            found_apps.append(app_name)
            for hostname in spec.get("hostnames", []):
                append_unique(hostnames, hostname)
        else:
            warnings.append(f"{app_name}: no configured marker found upstream")

    external_results: list[str] = []
    external_script_counter = [counters["script"]]
    for module in config.get("local_modules", []):
        name = module["name"]
        path = ROOT / module["path"]
        try:
            module_text = path.read_text(encoding="utf-8")
            merge_surge_module(
                module_text,
                name,
                sections,
                hostnames,
                external_script_counter,
            )
            external_results.append(f"{name}: merged")
        except Exception as exc:  # noqa: BLE001
            raise BuildError(f"{name}: local module failed: {path}: {exc}") from exc

    for module in config.get("external_modules", []):
        name = module["name"]
        url = module["url"]
        required = bool(module.get("required", False))
        try:
            module_text = fetch_text(url)
            merge_surge_module(
                module_text,
                name,
                sections,
                hostnames,
                external_script_counter,
            )
            external_results.append(f"{name}: merged")
        except Exception as exc:  # noqa: BLE001
            message = f"{name}: supplemental module failed: {url}: {exc}"
            if required:
                raise BuildError(message) from exc
            warnings.append(message)
            external_results.append(f"{name}: skipped")

    unsupported = [item for item in warnings if "unsupported selected rule" in item]
    if strict and unsupported:
        raise BuildError(
            "selected upstream blocks contain unsupported syntax:\n"
            + "\n".join(unsupported)
        )

    if not any(sections.values()):
        raise BuildError("no rules were generated")

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    output: list[str] = [
        "#!name=精选 App 去开屏（自动更新）",
        "#!desc=从墨鱼 StartUpAds.conf 提取指定 App，并合并缺失 App 的 Surge 模块",
        "#!author=Walvez + GitHub Actions",
        "#!homepage=https://github.com/Walvez/surge-startup-ads",
        "#!category=去广告",
        f"#!date={generated_at}",
        "",
        f"# Primary source: {source_url}",
        f"# Primary SHA-256: {source_sha}",
        f"# Selected apps found: {', '.join(found_apps) if found_apps else 'none'}",
        f"# Supplemental modules: {'; '.join(external_results) if external_results else 'none'}",
    ]

    if warnings:
        output.extend(["#", "# Build warnings:"])
        output.extend(f"# - {warning}" for warning in warnings)

    for section_name in SUPPORTED_SECTIONS:
        lines = sections[section_name]
        if not lines:
            continue
        output.extend(["", f"[{section_name}]"])
        output.extend(lines)

    output.extend(["", "[MITM]"])
    output.append("hostname = %APPEND% " + ", ".join(hostnames))
    output.append("")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(output), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Primary source: {source_url}")
    print(f"Warnings: {len(warnings)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, urllib.error.URLError, TimeoutError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
