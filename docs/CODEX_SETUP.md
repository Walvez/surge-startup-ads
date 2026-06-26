# Codex Setup

Place these files in repository root:
```text
surge-startup-ads/
├── AGENTS.md
├── CODEX_PROMPT.md
├── docs/
│   ├── PROJECT_CONTEXT.md
│   ├── MAINTENANCE.md
│   ├── COMMON_PROMPTS.md
│   └── CODEX_SETUP.md
├── config/
├── scripts/
├── modules/
├── dist/
└── README.md
```

Only one root `AGENTS.md` is needed.

Open Codex with:
```text
~/Desktop/surge-startup-ads
```

First message:
```text
请先读取根目录 AGENTS.md、docs/PROJECT_CONTEXT.md、docs/MAINTENANCE.md 和 CODEX_PROMPT.md，然后检查当前仓库状态并总结项目架构。不要修改文件。
```

Recommended permissions:
- allow repository file reads/writes;
- allow network access for upstream verification;
- allow normal local commands;
- require confirmation before push, force operations, destructive deletion, or permission changes.

Normal flow:
1. inspect;
2. propose plan;
3. edit and validate;
4. review diff;
5. authorize commit;
6. authorize push;
7. run GitHub Actions only when config/converter/module/output changed.

Keep synchronized after architecture changes:
- `AGENTS.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/MAINTENANCE.md`
- `README.md`
