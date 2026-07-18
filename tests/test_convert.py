import json
import unittest
from pathlib import Path

from scripts.convert import BuildError, build_module, convert_qx_line, split_qx_blocks


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "StartUpAds.sample.conf"


class ConvertTests(unittest.TestCase):
    def setUp(self):
        self.source = FIXTURE.read_text(encoding="utf-8")
        self.config = {
            "conversion_mode": "all",
            "strict_upstream_syntax": True,
            "local_overrides": [],
            "local_modules": [],
        }

    def test_full_build_converts_every_fixture_block(self):
        module, stats = build_module(
            self.config,
            "fixture://StartUpAds.sample.conf",
            self.source,
            resource_fetcher=lambda _url: '{"sdk":[],"addata":[]}',
        )

        self.assertEqual(stats["blocks"], 3)
        self.assertEqual(stats["upstream_rules"], 3)
        self.assertEqual(stats["hostnames"], 3)
        self.assertIn("#!date=2026-07-19", module)
        self.assertIn("[URL Rewrite]", module)
        self.assertIn("[Map Local]", module)
        self.assertIn("[Script]", module)
        self.assertIn("hostname = %APPEND% ads.example.com, api.example.com, static.example.com", module)
        self.assertNotIn("Build warnings", module)

    def test_echo_response_is_embedded_as_map_local(self):
        section, line, warning = convert_qx_line(
            r"^https?:\/\/example\.com\/ads url echo-response text/json echo-response https://example.com/empty.json",
            "example",
            {"script": 0},
            resource_fetcher=lambda _url: '{"items":[]}',
        )

        self.assertEqual(section, "Map Local")
        self.assertIn(r'data="{\"items\":[]}"', line)
        self.assertIn('header="Content-Type:application/json"', line)
        self.assertIsNone(warning)

    def test_strict_mode_rejects_unknown_upstream_syntax(self):
        bad_source = self.source.replace("url reject-200", "url unknown-action", 1)
        with self.assertRaises(BuildError):
            build_module(
                self.config,
                "fixture://bad.conf",
                bad_source,
                resource_fetcher=lambda _url: "{}",
            )

    def test_repository_config_uses_all_mode_and_local_fakeios(self):
        config = json.loads((ROOT / "config" / "build.json").read_text(encoding="utf-8"))
        self.assertEqual(config["conversion_mode"], "all")
        self.assertNotIn("external_modules", config)
        paths = {item["path"] for item in config["local_modules"]}
        self.assertIn("modules/FakeiOSAds.sgmodule", paths)

    def test_hostname_line_is_not_part_of_last_block(self):
        blocks = split_qx_blocks(self.source)
        last_block = blocks["sample-echo"]
        self.assertFalse(any(line.startswith("hostname =") for line in last_block))


if __name__ == "__main__":
    unittest.main()
