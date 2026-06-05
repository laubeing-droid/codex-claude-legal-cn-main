---
license: MIT
author: laubeing-droid
name: form-generation
description: >
platforms: [codex, claude-code, workbuddy, trae]
 参考：已弃用——请使用 `/draft` 代替。本技能已在 v2 重构中并入
 draft 技能，后者处理实践领域文件生成（含表格填充）。保留为重定向以支持迁移。
user-invocable: false
version: 2.10.0
module: legal-clinic
status: active
---

# [已弃用] 表格生成 → 参见 `/draft`

本技能在 v2 重构中已并入 `skills/draft/`。`/draft` 命令处理所有诊所文件的初稿生成，包括表格填充（劳动仲裁申请书、离婚起诉状、人身保护令申请书等），附实践领域模板和管辖地感知的格式。

**请改用 `/draft [文件类型]`。**

完整工作流见 `skills/draft/SKILL.md`。
