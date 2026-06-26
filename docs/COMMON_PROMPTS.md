# Common Codex Prompts

## 添加 App
```text
检查墨鱼最新 StartUpAds.conf 是否包含【APP 名称】。有的话确认精确 marker、完整规则块和必要 MITM hostname；加入 config/apps.json，更新 README，按现有流程重新生成 dist 并验证。不要加入同品牌的其他 App，除非我明确要求。先不要 push。
```

## 替换推荐模块
```text
把 README 中【旧模块】替换为【新模块链接】。先验证原作者和直链，只修改对应 <details> 区块和致谢。不要加入 external_modules，不要合并进主模块。URL 必须放独立 text 代码块。先不要 push。
```

## 排查失效
```text
排查【模块/App】的【故障】。检查重复模块、MITM、HTTP/2 MITM、pattern、binary-body-mode、requires-body、argument 引号、未替换占位符和缓存。对比原作者与当前生成模块，先给根因，不要先改文件。
```

## 例行维护
```text
按 AGENTS.md 和 docs/MAINTENANCE.md 做一次例行维护：拉取最新上游、重新生成、检查异常删减、语法错误、未替换占位符、重复脚本名、MITM 变化和 README 链接。先展示结果，不要自动提交。
```

## 准备提交
```text
检查当前 diff 和验证结果，确认没有无关修改。给出建议 commit message、待提交文件和是否需要 GitHub Actions。等我确认后再 commit/push。
```
