# Surge 精选 App 去开屏模块

本项目将墨鱼 `StartUpAds.conf` 中指定 App 的 Quantumult X 重写规则自动转换为 Surge 模块，并额外合并本仓库自行维护的少量转换模块。

为了便于维护和排查，本项目不再把多个第三方 Surge 专用模块全部融合进同一个文件。深度去广告模块改为在 README 中单独推荐，由用户按需安装。

最终生成文件：

```text
dist/StartUpAds_Selected.sgmodule
```

## 订阅地址

```text
https://raw.githubusercontent.com/Walvez/surge-startup-ads/main/dist/StartUpAds_Selected.sgmodule
```

在 Surge 中选择“从 URL 安装模块”，粘贴以上地址并启用。

### Quantumult X 本地补充重写

如果 Quantumult X 已经启用 `ddgksf2013 / 墨鱼` 的 `StartUpAds.conf`，可以再添加以下重写订阅，用于补充当前上游尚未覆盖的百度网盘 `splashMode`、广发基金 iOS 开屏图片、浦大喜奔当前开屏素材、医考帮和摩根资产管理开屏广告：

```text
https://raw.githubusercontent.com/Walvez/surge-startup-ads/main/quantumultx/StartUpAds_Local.conf
```

在 Quantumult X 的“重写资源”中添加并启用即可。摩根资产管理规则仅处理原生启动请求，不影响同一接口承载的首页广告位。

## 当前主模块包含什么

### 1. 墨鱼 StartUpAds 主配置转换

以下 App 的规则来自 `ddgksf2013 / 墨鱼` 的 `StartUpAds.conf`。

上游原始格式为 **Quantumult X 重写语法**，本仓库的 `scripts/convert.py` 会自动提取指定 App，并转换为 Surge 的 `[Rule]`、`[URL Rewrite]`、`[Body Rewrite]`、`[Script]`、`[Map Local]` 和 `[MITM]` 等区块。

| 分类 | App |
|---|---|
| 电商与购物 | 淘宝、天猫、京东、拼多多、闲鱼、得物、识货、慢慢买、唯品会、转转 |
| 外卖与生活 | 美团、美团外卖、大众点评、饿了么、叮咚买菜、盒马 |
| 出行与交通 | 滴滴出行、去哪儿旅行、飞猪旅行、铁路 12306、交管 12123、同程旅行 |
| 文娱与内容 | 豆瓣、腾讯新闻、百度网盘、百度地图、夸克、淘票票、猫眼、网易严选 |
| 餐饮 | 肯德基、麦当劳、必胜客 |
| 通信服务 | 中国移动、中国联通 |
| 智能家居与小米服务 | 米家、小米 |
| 其他 | 菜鸟、贝壳找房、大麦、顺丰速运 |

这部分主要用于开屏、启动页及少量基础广告处理。上游规则更新后，GitHub Actions 会重新提取并转换。

### 2. 本仓库单独转换的模块

| 功能 | 原始来源 | 原始格式 | 处理方式 |
|---|---|---|---|
| 影视去广告 | ddgksf2013 `FakeiOSAds.conf` | Quantumult X `.conf` | 由本仓库转换为 `modules/FakeiOSAds.sgmodule`，再合并进主模块 |
| 广发基金去开屏 | 本仓库根据实机请求维护 | Surge `.sgmodule` | 仅拦截 `trade-pic/app/pic/` 下带 `_ios` 或 `_kpios` 后缀的 iOS 开屏图片 |
| 浦大喜奔开屏补充 | 本仓库根据实机请求维护 | Surge `.sgmodule` | 补充拦截上游模块尚未覆盖、经实机确认的开屏素材 |
| 医考帮去开屏 | 本仓库根据实机抓包维护 | Surge `.sgmodule` | 仅删除启动配置响应中的 `boot_page` 对象，保留同一接口的其他数据 |
| 摩根资产管理去开屏 | 本仓库根据实机抓包维护 | Surge `.sgmodule` | 仅清空原生启动请求中的开屏广告数组，不影响同接口的首页广告位 |

当前主模块只包含以上两类内容。

## 可选的 Surge 专用模块

以下模块**不会再合并进本项目的主模块**。需要深度去广告时，可展开对应项目，复制订阅地址，再到 Surge 中选择“从 URL 安装模块”。

单独安装的好处：

- 可以按需启用或停用；
- 某个 App 出现异常时更容易排查；
- 更新来源更直接；
- 避免一个大型融合模块包含过多 MITM 域名和脚本；
- 不需要某项功能时，可以完全不安装。

> 每个模块的订阅地址都放在独立代码块中，GitHub 右上角会显示复制按钮。

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

- `ifflagged / Romeo` 在这里主要作为 Surge 模块镜像和整理来源，不代表所有规则均由其原创。
- YouTube 建议直接使用 Maasea 原始模块，不要再通过本项目进行融合。
- 不建议同时安装功能重复的多个专用模块。
- 专用模块可能扩大 MITM 范围，安装前应查看模块内容和来源。

## 使用前提：MITM / HTTPS 解密

本模块中的许多规则依赖 Surge 的 MITM。只安装模块但没有安装并信任证书时，HTTPS 重写、脚本和 Map Local 规则可能无法生效。

### Surge Mac 本机

1. 在 Surge Mac 的 HTTPS 解密设置中生成并安装 CA 证书。
2. 将证书安装到 macOS 系统钥匙串并设为信任。
3. 开启 HTTPS 解密。
4. 确认本模块已启用。

### 由 Surge Mac 接管的 iPhone / iPad

1. 在设备上安装 Surge Mac 提供的 CA 证书。
2. 进入“设置 → 通用 → VPN 与设备管理”完成安装。
3. 进入“设置 → 通用 → 关于本机 → 证书信任设置”，开启完全信任。
4. 确保设备流量实际经过 Surge Mac。

部分银行、支付及使用证书锁定的 App 可能拒绝 MITM。不要随意扩大解密范围。

## 自动更新方式

GitHub Actions 会定期执行：

1. 下载墨鱼 `StartUpAds.conf`；
2. 提取 `config/apps.json` 中指定的 App；
3. 将 Quantumult X 规则转换成 Surge 语法；
4. 合并本仓库维护的本地转换模块；
5. 生成 `dist/StartUpAds_Selected.sgmodule`；
6. 仅在结果变化时提交新版本。

第三方 Surge 专用模块已改为用户自行安装，不再参与主模块生成。

## 使用说明

- 首次启用后，建议彻底退出目标 App 再重新打开。
- App 可能缓存旧开屏素材，可在清理缓存后再次测试。
- App 更新后接口可能变化，规则可能暂时失效。
- 同一 App 不建议同时启用多个功能重复的模块。
- 出现异常时，先停用对应专用模块，而不是关闭整个主模块。
- 本项目仅整理、转换和自动更新上游规则，不保证长期兼容。

## 问题反馈

提交问题时请尽量提供：

- App 名称及版本；
- 设备和系统版本；
- Surge 版本；
- 广告出现的位置；
- 是否已安装并信任 MITM 证书；
- 是否已开启 HTTPS 解密；
- 已启用的相关专用模块；
- 脱敏后的截图。

请勿上传代理节点、订阅地址、证书、完整 Surge 配置或其他敏感信息。

## 上游与致谢

本项目使用或参考的主要来源包括：

- ddgksf2013 / 墨鱼规则；
- ifflagged / Romeo 镜像；
- Maasea；
- BiliUniverse；
- Kelee；
- blackmatrix7；
- sooyaaabo；
- fmz200。

感谢各上游作者和贡献者的维护。本仓库仅作个人整理、格式转换与自动更新。
