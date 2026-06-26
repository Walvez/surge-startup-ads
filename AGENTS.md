# AGENTS.md

## Project identity
Repository: `Walvez/surge-startup-ads`

Purpose: maintain a curated Surge startup-ad module generated from selected rules in ddgksf2013/Moyu `StartUpAds.conf`, plus a very small number of repository-owned local conversions.

Primary output:
```text
dist/StartUpAds_Selected.sgmodule
```

Subscription:
```text
https://raw.githubusercontent.com/Walvez/surge-startup-ads/main/dist/StartUpAds_Selected.sgmodule
```

## Architecture rules
The generated main module may contain only:
1. selected Moyu `StartUpAds.conf` conversions;
2. repository-owned local conversion modules, currently including `modules/FakeiOSAds.sgmodule`.

Do not merge third-party native Surge modules into the main output. Document them in `README.md` as optional independent installs.

## Read before editing
1. `AGENTS.md`
2. `docs/PROJECT_CONTEXT.md`
3. `docs/MAINTENANCE.md`
4. `config/apps.json`
5. `scripts/convert.py`
6. `.github/workflows/`
7. `README.md`

Treat current repository files as authoritative.

## Adding an app from Moyu
1. Fetch the current upstream source.
2. Confirm the exact marker, such as `# > mijia`.
3. Read the whole block until the next marker.
4. Identify only required MITM hostnames.
5. Add one entry to `config/apps.json`.
6. Regenerate output.
7. Verify expected rules and hostnames.
8. Update README app lists.

Example:
```json
"米家": {
  "markers": ["mijia"],
  "hostnames": ["home.mi.com"]
}
```

## Optional native Surge modules
Keep them out of `external_modules` unless the user explicitly reverses the current architecture.

Use README collapsible blocks:
```md
<details>
<summary><strong>Module name</strong> · Author</summary>

Short description.

```text
https://example.com/module.sgmodule
```

</details>
```

Do not place long raw URLs in markdown tables.

## Attribution
Always distinguish original author, mirror/aggregator, and this repository's conversion role. Do not credit `ifflagged/Romeo` as original author when it is only a mirror.

## Surge syntax safety
Preserve exact quoting and escaping, especially:
- `argument=`
- regex escapes
- `binary-body-mode`
- `requires-body`
- `[MITM] hostname`
- `%APPEND%`

Known historical bug:
```text
argument={"key":"value"}
```
did not work correctly, while the original quoted form did.

Check for unresolved placeholders:
```bash
grep -n "{{{" dist/StartUpAds_Selected.sgmodule
```

## MITM policy
Keep MITM scope minimal. Never use `hostname = *`. Do not add unrelated wildcard, bank, payment, or securities domains.

## README policy
- mobile-friendly;
- no wide tables with long URLs;
- optional modules use `<details>`;
- install URLs use fenced `text` blocks;
- explain MITM;
- warn against duplicate modules.

## Validation
Before committing:
```bash
git status --short
python3 -m json.tool config/apps.json >/dev/null
python3 scripts/convert.py --help
# run the same converter command used by GitHub Actions
git diff --check
```

Verify:
- output is non-empty;
- expected app marker/rule exists;
- expected hostname exists;
- optional native modules are absent from the main output;
- README links are correct;
- no unresolved placeholders;
- no duplicate script names;
- no accidental unrelated deletions.

## Git workflow
```bash
git pull --rebase origin main
git status --short
# edit and validate
git add <files>
git commit -m "<type>: <summary>"
git push
```

Use `feat:`, `fix:`, `docs:`, `refactor:`, or `chore:`. Never force-push.

README-only changes do not require regeneration. Changes to config, local modules, converter, workflow, or generated output do.

## Reporting
Respond in Chinese. For each task report:
1. what changed;
2. changed files;
3. validation;
4. whether GitHub Actions must run;
5. remaining uncertainty.

Do not claim success without validation evidence.
