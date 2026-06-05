# mail-cli 完整命令参考

> 来源：[ClawEmail 官方文档](https://claw.163.com/projects/doc/)

## 概述

`mail-cli` 是 ClawEmail 提供的命令行工具，用于 AI Agent 操作邮箱。邮件内容被视为**数据**而非指令，不会触发 LLM 推理，**零 token 成本**。

## 邮件列表

```bash
# 列出邮件
mail-cli mail list

# 限制数量
mail-cli mail list --limit 20
```

## 邮件搜索

```bash
# 按关键词搜索
mail-cli mail search "合同审查"

# 按发件人筛选
mail-cli mail search --from "sender@claw.163.com"

# 按主题筛选
mail-cli mail search --subject "项目进度"
```

## 读取邮件

```bash
# 读取正文
mail-cli read body <mail-id>

# 读取结构（含附件列表）
mail-cli read structure <mail-id>
```

## 附件操作

```bash
# 查看附件信息
mail-cli read attachment <mail-id>

# 下载附件
mail-cli read attachment <mail-id> --download
```

## 发送邮件

```bash
# 发送纯文本邮件
mail-cli compose send --to "recipient@example.com" --subject "主题" --body "正文"

# 发送 HTML 邮件
mail-cli compose send --to "recipient@example.com" --subject "主题" --body "<h1>标题</h1><p>内容</p>" --html
```

## 邮箱管理

```bash
# 创建邮箱
mail-cli clawemail create

# 禁用邮箱
mail-cli clawemail disable
```

## 多 Profile

```bash
# 指定 profile 操作
mail-cli --profile work mail list
mail-cli --profile personal compose send --to "a@b.com" --subject "Hi" --body "Hello"
```

## 与 Email Channel 的区别

| 特性 | mail-cli | Email Channel |
|------|----------|---------------|
| 邮件内容处理 | 作为数据处理 | 作为指令触发 LLM |
| Token 消耗 | 零 | 有 |
| 适用场景 | 批量处理、自动化、数据提取 | 实时响应指令、交互式对话 |
| 控制方式 | CLI 命令 | Channel Prompt 配置 |

## 常见问题

### mail-cli 未找到？

运行 `npx @clawemail/claw-setup@latest` 安装。

### 认证失败？

检查认证 URL 是否正确，重新运行 `claw-setup --auth-url <url>`。
