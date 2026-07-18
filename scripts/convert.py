#!/usr/bin/env python3
"""Convert every rule in Moyu StartUpAds.conf into one Surge module."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "build.json"
OUTPUT_PATH = ROOT / "dist" / "StartUpAds_Selected.sgmodule"
USER_AGENT = "surge-startup-ads/2.0 (+https://github.com/Walvez/surge-startup-ads)"

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
        if re.match(r"^\s*hostname\s*=", line, re.I) or SECTION_RE.match(line):
            current = None
            continue
        if current is not None:
            if re.match(r"^\s*#\s*=+", line):
                current = None
                continue
            blocks[current].append(line.rstrip())
    return dict(blocks)


def marker_display(block: list[str], fallback: str) -> str:
    if block:
        match = MARKER_RE.match(block[0])
        if match:
            return match.group(1).strip()
    return fallback


def unique_name(prefix: str, counter: int) -> str:
    safe = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff]+", "_", prefix).strip("_")
    return f"{safe}_{counter}"


def convert_qx_line(
    line: str,
    app_name: str,
    counters: dict[str, int],
    resource_fetcher: Callable[[str], str] = fetch_text,
) -> tuple[str | None, str | None, str | None]:
    """Return (section, converted_line, warning)."""
    raw = line.strip()
    if not raw or raw.startswith(("#", ";")):
        return None, None, None
    if re.match(r"^hostname\s*=", raw, re.I):
        return None, None, None

    match = re.match(
        r"^(.*?)\s+url\s+(reject(?:-[A-Za-z0-9_-]+)?)\s*$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        pattern, action = match.groups()
        return "URL Rewrite", f"{pattern.strip()} - {action.lower()}", None

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

    match = re.match(
        r"^(.*?)\s+url\s+echo-response\s+(\S+)\s+echo-response\s+(\S+)\s*$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        pattern, content_type, payload_url = match.groups()
        try:
            payload = resource_fetcher(payload_url).strip()
        except Exception as exc:  # noqa: BLE001
            return None, None, f"{app_name}: echo-response payload failed: {payload_url}: {exc}"
        if len(payload.encode("utf-8")) > 65536:
            return None, None, f"{app_name}: echo-response payload is too large: {payload_url}"
        surge_content_type = "application/json" if content_type.casefold() == "text/json" else content_type
        encoded_payload = json.dumps(payload, ensure_ascii=False)
        value = (
            f"{pattern.strip()} data-type=text data={encoded_payload} status-code=200 "
            f'header="Content-Type:{surge_content_type}"'
        )
        return "Map Local", value, None

    match = re.match(
        r"^(.*?)\s+url\s+response-body\s+(.+?)\s+response-body\s+(.+)$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        pattern, search, replacement = match.groups()
        return "Body Rewrite", f"http-response {pattern.strip()} {search.strip()} {replacement.strip()}", None

    match = re.match(
        r"^(.*?)\s+url\s+request-body\s+(.+?)\s+request-body\s+(.+)$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        pattern, search, replacement = match.groups()
        return "Body Rewrite", f"http-request {pattern.strip()} {search.strip()} {replacement.strip()}", None

    match = re.match(
        r"^(.*?)\s+url\s+jsonjq-response-body\s+(.+)$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        pattern, jq = match.groups()
        return "Body Rewrite", f"http-response-jq {pattern.strip()} {jq.strip()}", None

    match = re.match(
        r"^\s*(host|host-suffix)\s*,\s*([^,]+)\s*,\s*([^,\s]+)\s*$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        kind, domain, policy = match.groups()
        if policy.casefold() not in {"direct", "reject"}:
            return None, None, f"{app_name}: unsupported host policy: {raw}"
        surge_kind = "DOMAIN" if kind.casefold() == "host" else "DOMAIN-SUFFIX"
        surge_policy = "DIRECT" if policy.casefold() == "direct" else "REJECT"
        return "Rule", f"{surge_kind},{domain.strip()},{surge_policy}", None

    return None, None, f"{app_name}: unsupported upstream rule: {raw}"


def append_unique(target: list[str], line: str) -> None:
    if line not in target:
        target.append(line)


def parse_hostname_line(line: str) -> list[str]:
    match = re.match(r"^\s*hostname\s*=\s*(?:%APPEND%\s*)?(.*)$", line, re.I)
    if not match:
        return []
    return [item.strip() for item in match.group(1).split(",") if item.strip()]


def parse_all_hostnames(text: str) -> list[str]:
    hostnames: list[str] = []
    for line in text.splitlines():
        for hostname in parse_hostname_line(line):
            append_unique(hostnames, hostname)
    return hostnames


def parse_update_date(text: str) -> str:
    match = re.search(r"^//\s*@UpdateTime\s+(\d{4}-\d{2}-\d{2})\s*$", text, re.M)
    return match.group(1) if match else "unknown"


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
        if current not in SUPPORTED_SECTIONS or not line.strip():
            continue
        if line.lstrip().startswith("#"):
            append_unique(sections[current], f"# [{source_name}] {line.lstrip('# ').strip()}")
            continue
        if current == "Script" and "=" in line:
            _, rhs = line.split("=", 1)
            script_counter[0] += 1
            line = f"{unique_name(source_name, script_counter[0])} ={rhs}"
        append_unique(sections[current], line)


def apply_local_overrides(config: dict, sections: dict[str, list[str]]) -> list[str]:
    results: list[str] = []
    for override in config.get("local_overrides", []):
        name = override["name"]
        section = override["section"]
        if section not in sections:
            raise BuildError(f"{name}: unsupported override section: {section}")
        tokens = override.get("remove_contains", [])
        sections[section] = [
            line for line in sections[section] if not any(token in line for token in tokens)
        ]
        lines = override.get("lines", [])
        if not lines:
            raise BuildError(f"{name}: override has no replacement lines")
        append_unique(sections[section], f"# ===== {name} =====")
        for line in lines:
            append_unique(sections[section], line)
        results.append(f"{name}: applied")
    return results


def build_module(
    config: dict,
    source_url: str,
    source_text: str,
    resource_fetcher: Callable[[str], str] = fetch_text,
) -> tuple[str, dict[str, int]]:
    if config.get("conversion_mode") != "all":
        raise BuildError("conversion_mode must be 'all'")

    blocks = split_qx_blocks(source_text)
    sections: dict[str, list[str]] = {name: [] for name in SUPPORTED_SECTIONS}
    hostnames = parse_all_hostnames(source_text)
    warnings: list[str] = []
    counters = {"script": 0}
    converted_rules = 0

    for normalized_marker, block in blocks.items():
        display = marker_display(block, normalized_marker)
        per_section: dict[str, list[str]] = defaultdict(list)
        for line in block:
            section, converted, warning = convert_qx_line(
                line,
                display,
                counters,
                resource_fetcher=resource_fetcher,
            )
            if warning:
                warnings.append(warning)
            if section and converted:
                append_unique(per_section[section], converted)
                converted_rules += 1
        for section, lines in per_section.items():
            append_unique(sections[section], f"# ===== {display} =====")
            for line in lines:
                append_unique(sections[section], line)

    if config.get("strict_upstream_syntax", True) and warnings:
        raise BuildError("upstream conversion warnings:\n" + "\n".join(warnings))
    if converted_rules == 0:
        raise BuildError("no upstream rules were generated")

    supplemental_results = apply_local_overrides(config, sections)
    script_counter = [counters["script"]]
    for module in config.get("local_modules", []):
        name = module["name"]
        path = ROOT / module["path"]
        try:
            module_text = path.read_text(encoding="utf-8")
            merge_surge_module(module_text, name, sections, hostnames, script_counter)
            supplemental_results.append(f"{name}: merged")
        except Exception as exc:  # noqa: BLE001
            raise BuildError(f"{name}: local module failed: {path}: {exc}") from exc

    source_sha = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    output: list[str] = [
        "#!name=Surge 去开屏模块",
        "#!desc=完整转换墨鱼 StartUpAds.conf，并合并本仓库维护的本地补丁",
        "#!author=ddgksf2013 + Walvez",
        "#!homepage=https://github.com/Walvez/surge-startup-ads",
        "#!category=去广告",
        f"#!date={parse_update_date(source_text)}",
        "",
        "# Upstream: ddgksf2013/Moyu StartUpAds.conf",
        f"# Upstream SHA-256: {source_sha}",
        f"# Upstream blocks: {len(blocks)}",
        f"# Upstream rules converted: {converted_rules}",
        f"# Upstream MITM hostnames: {len(parse_all_hostnames(source_text))}",
        f"# Local additions: {'; '.join(supplemental_results) if supplemental_results else 'none'}",
    ]

    for section_name in SUPPORTED_SECTIONS:
        lines = sections[section_name]
        if lines:
            output.extend(["", f"[{section_name}]", *lines])

    output.extend(["", "[MITM]"])
    output.append("hostname = %APPEND% " + ", ".join(hostnames))
    output.append("")

    stats = {
        "blocks": len(blocks),
        "upstream_rules": converted_rules,
        "hostnames": len(hostnames),
        "scripts": script_counter[0],
    }
    return "\n".join(output), stats


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-file", type=Path, help="use a local StartUpAds.conf fixture")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="output module path")
    parser.add_argument("--dry-run", action="store_true", help="validate and print stats without writing")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if args.source_file:
        source_url = args.source_file.resolve().as_uri()
        source_text = args.source_file.read_text(encoding="utf-8-sig")
    else:
        source_url, source_text = fetch_first(config["source_urls"])

    module_text, stats = build_module(config, source_url, source_text)
    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(module_text, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print("Dry run; output was not written")
    print(f"Primary source: {source_url}")
    print("Stats: " + ", ".join(f"{key}={value}" for key, value in stats.items()))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, urllib.error.URLError, TimeoutError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
