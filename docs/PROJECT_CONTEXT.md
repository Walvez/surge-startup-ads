# Project Context

## Goal

Provide a maintainable full Surge conversion of Moyu `StartUpAds.conf`, so users are not limited to a maintainer-selected App list.

Architecture:

```text
all Moyu StartUpAds rules and MITM hostnames
+ repository-owned local overrides and modules
= dist/StartUpAds_Selected.sgmodule
```

The output filename is retained for subscription compatibility. Its content is full, not selected.

## Current decisions

Keep in the main output:

- every active rule block exposed by the current Moyu source;
- the complete upstream MITM hostname list, deduplicated;
- repository-owned overrides and modules, including `modules/FakeiOSAds.sgmodule`.

Current repository-owned surfaces (2026-08-03):

- `local_overrides` in `config/build.json`: 百度网盘、掌上生活、京东健康；
- `local_modules` in this checkout: FakeiOSAds、广发基金、浦大喜奔补充、医考帮、摩根资产管理、哔哩哔哩开屏/推荐流补充；
- standalone Quantumult X rewrite resource: `quantumultx/StartUpAds_Local.conf` (parity with the local patches above; not part of the Surge generator).

Do not merge third-party native Surge modules such as BiliUniverse ADBlock, Maasea YouTube Enhance, GoofishAds, CainiaoAds, SmzdmAds, Amap, XiaoHongShuAds, TieBaAds, Zhihu, WeChat mini-program modules, or China Telecom. Keep those as optional independent recommendations in README.

## Failure policy

- Unknown upstream syntax fails the build instead of being skipped.
- Local modules are read from this checkout and are required.
- The source SHA-256, block count, converted-rule count, and hostname count are recorded in the generated header.
- Upstream `@UpdateTime` is used as `#!date`; wall-clock build time must not create empty daily commits.

## MITM tradeoff

Full conversion intentionally has a much larger MITM scope than the former selected build. It includes upstream wildcards, IPs, and finance-related domains. Never add `hostname = *`. Document the risk and fix confirmed App-specific regressions with narrow exclusions or overrides.

## Sources

Primary:

```text
https://ddgksf2013.top/rewrite/StartUpAds.conf
```

If the primary URL returns HTML or a site shell instead of config text, fall back to the mirror below before comparing markers or regenerating.

Fallback mirror:

```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/ddgksf2013/Official/StartUpAds.conf
```

`ifflagged/Romeo` is a mirror/aggregator, not the original author.
