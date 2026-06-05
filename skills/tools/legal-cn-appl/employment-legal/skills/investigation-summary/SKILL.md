---
license: MIT
author: laubeing-droid
name: investigation-summary
description: >
platforms: [codex, claude-code, workbuddy, trae]
 从调查备忘录起草面向特定受众的摘要——HR版本、管理层版本或外部律师版本。
 当调查备忘录需要传达给不应看到完整保密工作成果的受众时使用。
argument-hint: "[调查事项名称] [受众：hr / 管理层 / 外部律师]"
version: 2.10.0
module: employment-legal
status: active
---

# /investigation-summary

从调查备忘录起草精简的、适合受众的摘要。HR摘要不包含保密分析和法律风险暴露评估。管理层摘要为高层次概述。外部律师简报包含完整上下文。

## 指令

1. 加载调查备忘录并运行受众摘要模式。
2. 如果尚无备忘录，提议先起草备忘录。
3. 各受众版本的规则：

| 受众 | 包含 | 排除 |
|---|---|---|
| **HR** | 事实发现、处理建议 | 法律分析、证据三性审查意见、法律风险评估 |
| **管理层** | 结论性摘要、关键事实、建议方案 | 详细证据分析、调查方法、内部法律意见 |
| **外部律师** | 完整事实背景、已有证据、缺口清单、需要外部意见的问题 | 仅排除与其他案件交叉的内容（除非有交叉引用授权） |

4. HR摘要不得包含：律师主观分析意见、证据可信度评估方法论、法律风险暴露分析。

## 保密说明

对外发出的摘要（HR、管理层）应移除"律师工作成果"标头，但保留基本保密标注。对外部律师的简报如包含律师分析意见，应标注保密并明确受《中华人民共和国律师法》第38条保护。`[法条原文]`

## 示例

```
/employment-legal:investigation-summary [调查事项名称] hr
```

```
/employment-legal:investigation-summary [调查事项名称] 管理层
```

```
/employment-legal:investigation-summary [调查事项名称] 外部律师
```
