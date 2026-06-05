# DECISIONS.md 生成指南

Claude 应基于全局协议中定义的 ADR 格式生成。

**范例参考：** 读取 `references/example-funes-AGENTS.md` 中对 DECISIONS 格式的定义，理解 ADR 的标准写法。

**结构：** 第一部分决策记录 + 第二部分工作日志

**初始决策记录：**
- `[DEC-001]` 应记录项目初始化的核心技术选型（框架、语言、架构模式等，从依赖文件和目录结构提取）
- 格式严格遵循：Background → Options → Decision → Rationale → Impact
- Options 应列出至少 2 个实际可选项（不是"选项A/选项B"占位符）

**工作日志：** 首条记录本次初始化操作
