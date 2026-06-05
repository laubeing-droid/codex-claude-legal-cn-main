---
name: agent-email
homepage: https://claw.163.com
author: 
version: "0.3.1"
license: MIT
author: laubeing-droid
description: Agent 专用邮箱服务，让 Claude Code、Codex 等平台的 Agent 收发邮件、分发任务。目前支持网易 ClawEmail。
---

# Agent Email

让 AI Agent 拥有专属邮箱，通过邮件接收指令、发送结果、与其他 Agent 或人类通信。

**为什么用邮件？**
- **零 token 消耗**：邮件收发本身不消耗 LLM token，理解内容由 Agent 自行完成
- **跨平台互通**：不同平台的 Agent 可以通过标准邮件协议互相通信
- **异步协作**：发完邮件继续工作，对方完成后通过 PR 或回复邮件提交结果

**适用场景：**
- Agent 之间通过邮件分发任务（如 Claude Code → Manus）
- Agent 向人类发送通知或报告
- 通过邮件收发材料、附件

## 触发条件

- 需要为 Agent 配置专属邮箱地址
- 需要收发、搜索、处理邮件
- 需要通过邮件与其他 Agent 或人类通信
- 需要处理邮件附件

## 前置条件

| 依赖 | 说明 |
|------|------|
| Node.js 18+ | `brew install node`（macOS）|
| npx | 随 Node.js 自带 |
| 邮箱服务账号 | 目前支持 [ClawEmail](https://claw.163.com)（网易）|

> **首次使用？** 详见 [首次配置指南](references/clawemail-setup-guide.md) 完成邮箱初始化。配置完成后，日常只需关注下面的邮件操作。

## 邮件操作

先加载封装函数：`source scripts/mail-ops.sh`

### 发送邮件

```bash
claw_send --to "recipient@example.com" --subject "主题" --body "正文内容"
```

自动从 `.env` 读取显示名称并构造 `--from` 参数。

### 查看邮件

```bash
claw_list --fid 1 --limit 20 # 列出邮件（--fid 1 收件箱, 3 已发送）
claw_body <mail-id> # 读取正文
claw_structure <mail-id> # 读取结构（含附件列表）
claw_search --fid 1 "关键词" # 搜索邮件
```

### 附件与文件夹

```bash
claw_download <mail-id> # 下载附件
claw_folders # 查看文件夹
claw_mailboxes # 查看所有邮箱
```

## 典型工作流

### 向其他 Agent 分发任务

```bash
# 1. 构造任务邮件
claw_send --to "$AGENT_MANUS" --subject "数据分析任务" --body "请分析附件中的销售数据..."

# 2. 对方 Agent 执行完成后，通过 git PR 提交结果
# （无需回读邮件）
```

### 读取邮件并回复

```bash
# 1. 查看收件箱
claw_list --fid 1 --limit 10

# 2. 读取邮件正文
claw_body <mail-id>

# 3. Agent 理解内容、执行操作

# 4. 回复
claw_send --to "sender@example.com" --subject "Re: 原主题" --body "处理结果..."
```

### 定时检查新邮件

配合 Cron 定期检查新邮件并处理。

## 常用联系人

邮箱地址统一维护在 `scripts/.env`，source 后可直接引用：

```bash
source scripts/mail-ops.sh
claw_send --to "$AGENT_MANUS" --subject "任务" --body "内容"
claw_send --to "$CONTACT_163" --subject "材料" --body "附件请查收"
```

新增联系人直接在 `.env` 里加一行即可。

## 参考文档

- **`references/clawemail-setup-guide.md`** — 网易 ClawEmail 首次配置指南
- **`references/clawemail-overview.md`** — 网易 ClawEmail 服务介绍（申请流程、模式对比、常见问题排查）
- **`references/clawemail-mail-cli-guide.md`** — 网易 mail-cli 命令参考
- **`templates/reply-template.md`** — 回复邮件模板
