---
license: MIT
author: laubeing-droid
name: write-a-legal-skill
description: >
platforms: [codex, claude-code, workbuddy, trae]
 遵循 -ZH 仓库的底层架构标准，指导并自动生成标准化、结构化的法律AI技能文件（SKILL.md），确保包含完整的 YAML frontmatter、精准的中国法条引用及标准化的代码块输出格式。
argument-hint: 请提供你想创建的法律技能名称、所属 Plugin 领域、目标触发词以及核心的工作流步骤。
version: 2.10.0
module: legal-builder-hub
status: active
---

# /legal-builder-hub:write-a-legal-skill

1. 引导用户明确新技能的定位、应用场景、目标插件及其中文释义。
2. 自动构建符合规范的 YAML frontmatter，包含 name、description（折叠块）及 argument-hint。
3. 规划逻辑严密的编号工作流步骤（以动词开头，强调中国法律实务动作）。
4. 在"详细说明"中嵌入精准的中国法条（法律全称+精确条款号），并设计 Markdown 输出模板。
5. 输出完整的 `SKILL.md` 源码文件。

## 详细说明

本技能是针对本技能仓库本身的元技能（Meta-Skill），旨在维护系统工程的严谨性。编写时须遵循以下设计规范：
- **架构对齐**：所有生成的技能文件必须采用标准 Markdown 语法，严禁在正文中使用非法符号破坏系统解析。
- **中国法适配**：工作流和详细说明部分必须体现中国法特有的诉讼、仲裁、行政合规流程。
- **输出可视化**：末尾必须使用标准 Markdown 结构和代码块提供预期的 AI 输出范例。

### 输出格式示例

```markdown
# 技能文件生成成功

以下是为您生成的标准化 `SKILL.md` 文件源码：

```yaml
---
name: sample-skill-name
description: >
 [此处为折叠块描述，每行开头强制缩进2个空格]
argument-hint: [用户输入提示词]
---
# /domain-plugin:sample-skill-name

1. [步骤一：定义审查起点]
2. [步骤二：匹配中国法律条文]
3. [步骤三：输出合规结论]

## 详细说明
[深入阐述中国法律实务要求及条款要件细节...]

### 输出格式示例
....
```