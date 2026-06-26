# Codex Primary Prompt

你现在负责维护本地仓库 `surge-startup-ads`。

开始前：
1. 读取 `AGENTS.md`；
2. 读取 `docs/PROJECT_CONTEXT.md`；
3. 读取 `docs/MAINTENANCE.md`；
4. 检查 `git status`；
5. 读取相关当前文件，不要凭记忆重建。

项目原则：
- 主模块只包含墨鱼 `StartUpAds.conf` 的选定转换规则，以及本仓库自行维护的本地转换模块。
- 第三方原生 Surge 模块不得合并进主模块，只能在 README 中作为可选独立安装推荐。
- MITM 范围应尽量小。
- 必须保留 Surge 语法细节，尤其是 `argument=` 引号。
- README 不得把长 URL 放进宽表格；使用 `<details>` 和独立 `text` 代码块。
- 必须区分原作者、镜像仓库和本仓库的转换角色。

每次任务：
1. 先检查现状和上游；
2. 做最小必要修改；
3. 运行相关验证；
4. 汇报修改文件、验证结果、是否需要 GitHub Actions；
5. 未经明确授权，不要 push、force、删除大量文件或修改权限。

添加墨鱼 App 时：
- 核对精确 marker；
- 读取完整规则块；
- 只加入必要 hostname；
- 修改 `config/apps.json`；
- 按仓库现有流程重新生成 `dist`；
- 更新 README；
- 检查生成结果。

替换推荐模块时：
- 优先使用原作者直接链接；
- 只改 README；
- 不加入 `external_modules`；
- 说明兼容性问题。

现在先总结仓库架构并报告工作区是否干净，不要修改文件。
