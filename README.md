# Surge 去开屏模块

基于 `ddgksf2013 / 墨鱼` 的 `StartUpAds.conf`，将其中全部 Quantumult X 规则转换为 Surge 模块，并合并本仓库维护的少量本地补丁。

主要处理 App 开屏、启动页及部分启动阶段广告。上游增加规则后，GitHub Actions 会自动重新生成模块。

## 安装

```text
https://raw.githubusercontent.com/Walvez/surge-startup-ads/main/dist/StartUpAds_Selected.sgmodule
```

1. 在 Surge 中选择“从 URL 安装模块”。
2. 粘贴订阅地址并启用模块。
3. 安装并信任 MITM 证书，开启 HTTPS 解密。
4. 彻底退出目标 App 后重新打开；如仍显示缓存广告，可清理 App 缓存后再试。

## 本模块包含

- 墨鱼 `StartUpAds.conf` 当前全部规则块的 Surge 转换；
- 完整上游 MITM hostname 列表；
- 影视类 FakeiOSAds 转换规则；
- 百度网盘 `activityentry` 与 `splashMode` 本地覆盖；
- 掌上生活开屏预缓存与首页浮窗拦截；
- 京东健康启动开屏资源拦截；
- 广发基金 iOS 开屏图片拦截；
- 浦大喜奔当前开屏素材拦截；
- 医考帮开屏、启动弹窗、首页浮窗及横幅广告清理；
- 摩根资产管理原生启动开屏广告清理。

第三方原生深度去广告模块不在本订阅内，可在下方“可选模块”中按需安装。本模块不会使用 `hostname = *`。

## MITM 与使用风险

本模块中的 HTTPS 重写、脚本和 Map Local 规则依赖 Surge MITM。没有安装并信任证书时，多数规则无法生效。

模块会继承墨鱼配置中的完整 MITM 列表，其中包含通配域名、IP，以及银行、证券、基金等相关域名。部分银行、支付或使用证书锁定的 App 可能出现联网、登录或内容加载异常。

遇到异常时：

1. 暂时停用本模块并重新打开 App；
2. 确认异常是否随模块停用而消失；
3. 检查是否同时启用了功能重复的模块；
4. 提交具体 App、版本和脱敏日志，以便添加针对性兼容处理。

<details>
<summary><strong>Surge Mac 证书设置</strong></summary>

1. 在 Surge Mac 的 HTTPS 解密设置中生成并安装 CA 证书。
2. 将证书安装到 macOS 系统钥匙串并设为信任。
3. 开启 HTTPS 解密。
4. 确认本模块处于启用状态。

</details>

<details>
<summary><strong>由 Surge Mac 接管的 iPhone / iPad</strong></summary>

1. 在设备上安装 Surge Mac 提供的 CA 证书。
2. 进入“设置 → 通用 → VPN 与设备管理”完成安装。
3. 进入“设置 → 通用 → 关于本机 → 证书信任设置”，开启完全信任。
4. 确保设备流量实际经过 Surge Mac。

</details>

## 可选模块

以下模块为独立订阅，适合需要特定 App 深度去广告的用户。请按需安装，避免同时启用功能重复的模块。

<details>
<summary><strong>闲鱼增强</strong> · ddgksf2013</summary>

补充首页及部分信息流广告处理。

```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/ddgksf2013/GoofishAds.sgmodule
```

</details>

<details>
<summary><strong>菜鸟增强</strong> · ddgksf2013</summary>

补充首页、搜索栏、寄件及个人页推广处理。

```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/ddgksf2013/CainiaoAds.sgmodule
```

</details>

<details>
<summary><strong>什么值得买</strong> · ddgksf2013</summary>

处理首页、好价、百科、搜索及会员页面推广。

```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/ddgksf2013/SmzdmAds.sgmodule
```

</details>

<details>
<summary><strong>高德地图</strong> · sooyaaabo</summary>

处理首页、搜索热词、路线及导航结束页推广。

```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/sooyaaabo/Amap.sgmodule
```

</details>

<details>
<summary><strong>哔哩哔哩 ADBlock</strong> · BiliUniverse</summary>

支持参数化处理开屏、推荐、搜索、直播、动态和评论广告。出现评论加载异常时，可在模块参数中关闭“评论去广告”。

```text
https://github.com/BiliUniverse/ADBlock/releases/latest/download/BiliBili.ADBlock.sgmodule
```

</details>

<details>
<summary><strong>小红书</strong> · ddgksf2013</summary>

处理开屏、首页、搜索和活动入口。

```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/ddgksf2013/XiaoHongShuAds.sgmodule
```

</details>

<details>
<summary><strong>墨迹天气</strong> · fmz200</summary>

处理开屏及部分广告资源。

```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/fmz200/Official/MojiWeather.sgmodule
```

</details>

<details>
<summary><strong>百度贴吧</strong> · ddgksf2013</summary>

处理信息流、热搜及页面广告。

```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/ddgksf2013/TieBaAds.sgmodule
```

</details>

<details>
<summary><strong>知乎</strong> · ddgksf2013、blackmatrix7 等</summary>

处理推荐、热榜、搜索、回答页及弹窗。

```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/ddgksf2013/zhihu.ads.sgmodule
```

</details>

<details>
<summary><strong>微信小程序</strong> · Kelee</summary>

覆盖多个常用微信小程序，规则范围较广。

```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/Kelee/Beta/WexinMiniPrograms_Remove_ads.sgmodule
```

</details>

<details>
<summary><strong>YouTube Enhance</strong> · Maasea</summary>

适用于 YouTube 与 YouTube Music，支持去广告、画中画、后台播放和翻译。

```text
https://raw.githubusercontent.com/Maasea/sgmodule/master/YouTube.Enhance.sgmodule
```

</details>

<details>
<summary><strong>中国电信</strong> · fmz200</summary>

处理欢迎页、开屏及部分广告请求。

```text
https://raw.githubusercontent.com/ifflagged/Romeo/main/Modules/Surge/fmz200/Beta/ChinaTelecom.sgmodule
```

</details>

<details>
<summary><strong>浦大喜奔</strong> · 奶思 / fmz200</summary>

匹配新版浦大喜奔 `image.spdbccc.com.cn` 上的已知开屏素材。首次启用后可能需要清理 App 缓存或重新安装。

```text
https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/split/partP/PuDaXiBen.sgmodule
```

</details>

说明：

- `ifflagged / Romeo` 是 Surge 模块镜像和整理来源，不代表所有规则均由其原创；
- YouTube 使用 Maasea 原始模块；
- 独立模块可能扩大 MITM 范围，安装前请查看模块内容和来源。

## Quantumult X 补充

Quantumult X 用户可在已经启用墨鱼 `StartUpAds.conf` 的基础上，添加本仓库的补充重写：

```text
https://raw.githubusercontent.com/Walvez/surge-startup-ads/main/quantumultx/StartUpAds_Local.conf
```

请添加到 Quantumult X 的“重写资源”。该订阅包含百度网盘 `splashMode`、掌上生活开屏与首页浮窗、京东健康、哔哩哔哩开屏/推荐流、广发基金、浦大喜奔、医考帮和摩根资产管理补充规则，不属于 Surge 主模块订阅。

## 自动更新

GitHub Actions 会定期获取墨鱼 `StartUpAds.conf`、转换全部规则、合并本地补丁并校验生成结果。订阅地址保持固定，Surge 可直接获取更新后的模块。

生成文件头部会记录上游 SHA-256、规则块数量、转换规则数量和 MITM hostname 数量，便于核对更新内容。

## 问题反馈

提交前请确认：

1. MITM 证书已经安装并信任；
2. HTTPS 解密已经开启；
3. 没有同时启用功能重复的模块；
4. 已彻底退出并重新打开 App，必要时清理缓存；
5. 停用本模块后，问题是否消失。

请提供：

- App 名称及版本；
- 设备和系统版本；
- Surge 版本；
- 广告或异常出现的位置；
- 已启用的相关模块；
- 脱敏后的截图或日志。

请勿上传代理节点、订阅地址、证书、完整 Surge 配置或其他敏感信息。

## 上游与致谢

本项目使用或参考以下来源：

- ddgksf2013 / 墨鱼；
- ifflagged / Romeo；
- Maasea；
- BiliUniverse；
- Kelee；
- blackmatrix7；
- sooyaaabo；
- fmz200。

感谢各上游作者和贡献者的维护。本仓库负责规则整理、格式转换、自动构建及本地兼容补丁。
