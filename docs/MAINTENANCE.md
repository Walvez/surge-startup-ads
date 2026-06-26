# Maintenance Guide

## Add an app from Moyu

Fetch upstream:
```bash
curl -L 'https://ddgksf2013.top/rewrite/StartUpAds.conf' -o /tmp/StartUpAds.conf
grep -n -i '# > marker\|keyword' /tmp/StartUpAds.conf
```

Read from the marker to the next `# >` marker.

Add a minimal `config/apps.json` entry:
```json
"米家": {
  "markers": ["mijia"],
  "hostnames": ["home.mi.com"]
}
```

Validate JSON:
```bash
python3 -m json.tool config/apps.json >/dev/null
```

Inspect converter/workflow:
```bash
python3 scripts/convert.py --help
ls .github/workflows
```

Use the same generation command as GitHub Actions.

Verify:
```bash
grep -n -i 'marker\|hostname' dist/StartUpAds_Selected.sgmodule
grep -n '{{{' dist/StartUpAds_Selected.sgmodule
git diff --check
```

Update README category list.

## Replace an optional recommendation
1. Verify original maintainer and direct link.
2. Replace only the relevant README `<details>` block.
3. Update attribution.
4. Keep it out of `external_modules`.
5. README-only change: no workflow run needed.

## Diagnose a module
Check:
1. duplicate enabled modules;
2. MITM certificate and hostname;
3. HTTP/2 MITM requirement;
4. script execution logs;
5. `pattern`;
6. `binary-body-mode`;
7. `requires-body`;
8. exact `argument=` quoting;
9. unresolved placeholders;
10. cached ads;
11. whether original upstream works alone.

## README layout
Use:
```md
<details>
<summary><strong>Name</strong> · Author</summary>

Description.

```text
URL
```

</details>
```

## Routine update
```bash
git pull --rebase origin main
python3 scripts/convert.py --help
# run repository's actual generation command
git diff --check
git status --short
```

Review large rule deletions carefully. Do not blindly commit upstream breakage.
