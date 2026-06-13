# Surge 精选 App 去开屏

本仓库每天自动：

1. 下载 `https://ddgksf2013.top/rewrite/StartUpAds.conf`；
2. 提取 `config/apps.json` 中指定的国内 App；
3. 把常见 Quantumult X 重写语法转换成 Surge 模块语法；
4. 合并高德地图、哔哩哔哩、小红书、墨迹天气、中国电信等补充 Surge 模块；
5. 输出一个远程模块：`dist/StartUpAds_Selected.sgmodule`。

## Surge 订阅地址

```text
https://raw.githubusercontent.com/Walvez/surge-startup-ads/main/dist/StartUpAds_Selected.sgmodule
```

在 Surge Mac 中进入：

```text
模块 → 安装新模块 → 从 URL 安装
```

粘贴上面的地址即可。

## 第一次上传后要做什么

进入仓库的 **Actions** 页面，选择：

```text
Update selected Surge startup-ad module
```

点击 **Run workflow**。运行成功后，`dist/StartUpAds_Selected.sgmodule` 会被自动更新。

之后 GitHub Actions 每天北京时间约 11:17 检查一次上游；只有输出发生变化时才提交新版本。

## 若 GitHub Actions 无法提交

进入：

```text
仓库 Settings
→ Actions
→ General
→ Workflow permissions
→ Read and write permissions
```

保存后重新运行工作流。

## 规则范围

主配置从墨鱼 `StartUpAds.conf` 中选择以下 App：

- 淘宝、天猫、京东、拼多多、闲鱼
- 得物、识货、慢慢买
- 美团、大众点评、滴滴出行、去哪儿旅行
- 菜鸟、肯德基、豆瓣、百度网盘、中国移动

补充 Surge 模块：

- 什么值得买
- 高德地图
- 哔哩哔哩
- 小红书
- 墨迹天气
- 中国电信

注意：部分补充模块不只处理开屏广告，也可能同时处理该 App 的信息流、首页或弹窗广告。

## 安全机制

- 主源失败时自动尝试 GitHub 镜像。
- 选中段落出现无法识别的新语法时，工作流会失败，不覆盖上一版可用模块。
- 某个非必需补充模块下载失败时，只在生成文件头部记录警告，不影响其他规则更新。
- Surge 客户端必须安装并完全信任同一张 CA，HTTPS 重写才会生效。
