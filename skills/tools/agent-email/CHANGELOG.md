## [0.3.1] - 2026-05-17

### 修复
- 修复 `mail-ops.sh` 中 `npx` 参数分隔导致 mail-cli 收到多余参数的问题
- 修复 `claw_send` 的 `--from`、`--body` 等参数组装，支持显示名和正文中的空格
- 修复 `.env.example` 与首次配置指南中的 `DISPLAY_NAME` 示例，避免 source 时因空格中断
- 移除函数库顶层 shell 选项修改，避免 `source scripts/mail-ops.sh` 影响调用方终端

### 文档完善
- 同步 SKILL frontmatter、README 和 Marketplace 清单版本为 `0.3.1`

## [0.3.0] - 2026-05-17

### 变更
- 技能重命名：`claw-mail` → `agent-email`，定位为通用 Agent 邮箱服务（ClawEmail 为首个支持的服务商）
- SKILL.md 重构：新增「这是什么」章节、适用场景，ClawEmail 细节移至 references
- 首次配置章节移至 `references/clawemail-setup-guide.md`，SKILL.md 聚焦日常邮件操作
- 邮件操作章节统一展示封装函数 + 原始命令
- 新增典型工作流：Agent 任务分发（邮件发任务 → PR 收结果）
- 常见问题排查扩充：发件人名称不显示、npx 安装慢

## [0.2.0] - 2026-05-17

### 变更
- 重定位为纯 mail-cli 模式，移除 claw-setup / OpenClaw 插件依赖
- 删除 `scripts/setup.sh` 和 `scripts/.env.example`
- 重写 `scripts/mail-ops.sh`：去掉 .env 依赖，改用 npx 调用，新增 `claw_init` 一键配置
- SKILL.md 全面重写，聚焦 mail-cli 操作和首次配置流程

## [0.1.0] - 2026-05-16

### 新增
- 初始版本：ClawEmail 邮件服务接入 Skill
