# Maintenance Guide

## Routine validation

```bash
git status --short
python3 -m json.tool config/build.json >/dev/null
python3 -m unittest discover -s tests -v
python3 scripts/convert.py --help
python3 scripts/convert.py --dry-run
python3 scripts/convert.py
git diff --check
```

`--help` is side-effect free. `--dry-run` fetches and fully validates the current upstream but does not write the output. The plain command is the same generation command used by GitHub Actions.

For an offline converter check:

```bash
python3 scripts/convert.py \
  --source-file tests/fixtures/StartUpAds.sample.conf \
  --dry-run
```

## Upstream changes

No App allowlist is maintained. New upstream markers are converted automatically.

When a build fails after an upstream update:

1. confirm the downloaded response is real config text, not HTML;
2. identify the exact marker and unsupported rule;
3. add a narrowly scoped conversion with an offline test;
4. regenerate and inspect the affected Surge section and MITM hostname;
5. do not weaken strict mode or silently skip the rule.

## Repository-owned fixes

Use `local_overrides` in `config/build.json` when an upstream rule must be removed or replaced. Use `local_modules` for repository-owned Surge modules. Keep local modules in the checkout; never fetch this repository's own `main` branch through `external_modules`.

When a local rule is applicable to Quantumult X, also inspect `quantumultx/StartUpAds_Local.conf` for parity. That file remains a standalone QX rewrite resource and is not part of the Surge generator.

## Diagnose a module

Check:

1. duplicate enabled modules;
2. MITM certificate and hostname;
3. HTTP/2 MITM requirement;
4. script execution logs;
5. `pattern` and rule order;
6. `binary-body-mode` and `requires-body`;
7. exact `argument=` quoting;
8. unresolved placeholders;
9. cached ads;
10. whether original upstream works alone.

For a full-build regression, first disable the main module and confirm the affected App recovers. Then add the narrowest compatible exclusion or override instead of returning to an App allowlist.

## Optional recommendations

Verify the original maintainer and direct link, keep optional modules out of the generator, and use README `<details>` blocks with URLs in fenced `text` blocks.

Review large upstream rule or hostname deletions carefully. Never blindly commit them.
