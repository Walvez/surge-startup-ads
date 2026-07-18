# AGENTS.md

## Project identity

Repository: `Walvez/surge-startup-ads`

Purpose: maintain a full Surge conversion of ddgksf2013/Moyu `StartUpAds.conf`, plus a very small number of repository-owned local fixes.

Primary output and compatibility subscription:

```text
dist/StartUpAds_Selected.sgmodule
https://raw.githubusercontent.com/Walvez/surge-startup-ads/main/dist/StartUpAds_Selected.sgmodule
```

The historical `Selected` filename is retained to avoid breaking existing subscriptions. The generated content is full, not selected.

## Architecture rules

The generated main module may contain only:

1. all active Moyu `StartUpAds.conf` conversions and upstream MITM hostnames;
2. repository-owned local overrides and modules, including `modules/FakeiOSAds.sgmodule`.

Do not merge third-party native Surge modules into the main output. Document them in `README.md` as optional independent installs.

## Read before editing

1. `AGENTS.md`
2. `docs/PROJECT_CONTEXT.md`
3. `docs/MAINTENANCE.md`
4. `config/build.json`
5. `scripts/convert.py`
6. `.github/workflows/`
7. `README.md`

Treat current repository files as authoritative.

## Upstream conversion

- Do not maintain an App allowlist.
- Fetch the current upstream source and confirm it is config text, not HTML.
- Convert every `# > marker` block and deduplicate the complete upstream hostname list.
- Unknown upstream syntax must fail the build; never silently skip it.
- Add an offline fixture and unit test for every newly supported syntax.
- Use upstream `@UpdateTime` for `#!date`; do not use wall-clock build time.

## Repository-owned fixes

- Use `local_overrides` in `config/build.json` for removals/replacements.
- Use `local_modules` for repository-owned Surge modules.
- Read local modules from this checkout. Do not fetch this repository's own `main` branch as an external module.
- Check `quantumultx/StartUpAds_Local.conf` when a local rule also applies to Quantumult X.

## Optional native Surge modules

Keep third-party native modules out of the generator. Use README collapsible blocks with the original author distinguished from mirrors/aggregators. Do not place long raw URLs in markdown tables.

## Surge syntax safety

Preserve exact quoting and escaping, especially `argument=`, regex escapes, `binary-body-mode`, `requires-body`, `[MITM] hostname`, and `%APPEND%`.

Known historical bug:

```text
argument={"key":"value"}
```

did not work correctly, while the original quoted form did.

## MITM policy

Full conversion intentionally inherits the upstream MITM scope, including wildcards, IPs, and finance-related domains. Never use `hostname = *`. Document the risk and use narrow App-specific compatibility fixes for confirmed regressions.

## README policy

- mobile-friendly;
- no wide tables with long URLs;
- optional modules use `<details>`;
- install URLs use fenced `text` blocks;
- explain full-conversion MITM scope;
- warn against duplicate modules.

## Validation

Before committing:

```bash
git status --short
python3 -m json.tool config/build.json >/dev/null
python3 -m unittest discover -s tests -v
python3 scripts/convert.py --help
python3 scripts/convert.py --dry-run
python3 scripts/convert.py
git diff --check
```

Verify:

- output is non-empty and reports hundreds of upstream blocks/rules;
- current upstream builds with zero unsupported syntax;
- expected local overrides and modules exist;
- complete upstream and local hostnames are merged without `hostname = *`;
- no unresolved placeholders or duplicate script names;
- README links are correct;
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

Respond in Chinese. Report what changed, changed files, validation evidence, whether GitHub Actions must run, and remaining uncertainty. Do not claim success without evidence.
