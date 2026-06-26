# Project Context

## Goal
Create a curated, maintainable Surge startup-ad module rather than an all-in-one mega-module.

Architecture:
```text
selected Moyu StartUpAds conversion
+ repository-owned local conversions
= dist/StartUpAds_Selected.sgmodule
```

Third-party native Surge modules remain independent recommendations in README.

## Current decisions
Keep in main output:
- selected Moyu rules;
- repository-owned conversions such as `modules/FakeiOSAds.sgmodule`.

Do not merge:
- BiliUniverse ADBlock;
- Maasea YouTube Enhance;
- GoofishAds;
- CainiaoAds;
- SmzdmAds;
- Amap;
- XiaoHongShuAds;
- TieBaAds;
- Zhihu;
- WeChat mini-program modules;
- China Telecom;
- other native third-party Surge modules.

## Recommended modules

### Bilibili
Use BiliUniverse ADBlock:
```text
https://github.com/BiliUniverse/ADBlock/releases/latest/download/BiliBili.ADBlock.sgmodule
```
Reason: a previous ddgksf2013 combined Bilibili module caused comment loading stalls/no-connection behavior. BiliUniverse is parameterized; comment ad removal can be disabled.

### YouTube
Use Maasea directly:
```text
https://raw.githubusercontent.com/Maasea/sgmodule/master/YouTube.Enhance.sgmodule
```

## Recent Moyu additions

### 米家
Marker:
```text
# > mijia
```
Rule:
```text
^https?:\/\/home\.mi\.com\/cgi-op\/api\/v\d\/recommendation url reject-200
```
Hostname:
```text
home.mi.com
```

### 小米
Marker:
```text
# > xiaomi
```
Rule:
```text
^https?:\/\/api\.m\.mi\.com\/v1\/app\/start url reject-200
```
Hostname:
```text
api.m.mi.com
```

## Historical bug
A merged Maasea YouTube module lost required quoting around `argument=`. It installed but did not remove ads. Preserve exact original syntax.

## README layout
Long module URLs must be in `<details>` sections and fenced `text` blocks, not markdown tables.

## Sources
Primary:
```text
https://ddgksf2013.top/rewrite/StartUpAds.conf
```
Fallback:
```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/ddgksf2013/Official/StartUpAds.conf
```
Repository:
```text
https://github.com/Walvez/surge-startup-ads
```
