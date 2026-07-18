# Codex Primary Prompt

你现在负责维护本地仓库 `surge-startup-ads`。

开始前：
1. 读取 `AGENTS.md`；
2. 读取 `docs/PROJECT_CONTEXT.md`；
3. 读取 `docs/MAINTENANCE.md`；
4. 检查 `git status`；
5. 读取相关当前文件，不要凭记忆重建。

项目原则：
- 主模块包含墨鱼 `StartUpAds.conf` 的全部规则和 MITM hostname，以及本仓库自行维护的本地覆盖与模块。
- 第三方原生 Surge 模块不得合并进主模块，只能在 README 中作为可选独立安装推荐。
- 全量转换会继承上游 MITM 范围；不得加入 `hostname = *`，确认兼容问题后使用窄范围修复。
- 必须保留 Surge 语法细节，尤其是 `argument=` 引号。
- README 不得把长 URL 放进宽表格；使用 `<details>` 和独立 `text` 代码块。
- 必须区分原作者、镜像仓库和本仓库的转换角色。

每次任务：
1. 先检查现状和上游；
2. 做最小必要修改；
3. 运行相关验证；
4. 汇报修改文件、验证结果、是否需要 GitHub Actions；
5. 未经明确授权，不要 push、force、删除大量文件或修改权限。

墨鱼上游变化时：
- 不维护 App 白名单，新 marker 应自动转换；
- 未知语法必须补充转换和离线测试，不能静默跳过；
- 按仓库流程重新生成 `dist`；
- 检查规则数量、MITM 变化和受影响 App。

替换推荐模块时：
- 优先使用原作者直接链接；
- 只改 README；
- 不加入 `external_modules`；
- 说明兼容性问题。

现在先总结仓库架构并报告工作区是否干净，不要修改文件。
