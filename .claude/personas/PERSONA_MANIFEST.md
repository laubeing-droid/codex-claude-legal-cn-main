---
license: MIT
author: laubeing-droid
---

# Persona Manifest — 法律画像库

## 一、概述

本目录包含 28 个法律专业画像（Persona），按 7 大部门组织。每个 Persona 为原独立 Agent 的降维凝练——保留完整 6 步 SOP 检查清单和标准化输出模板，但不再以独立 Agent 形态运行。

## 二、加载机制

10 个核心 Agent 在处理任务时，根据业务属性动态加载对应部门 Persona：

- Agent 识别任务的业务属性
- 匹配并注入对应部门 Persona 的 SOP 和输出模板
- Agent 本体不变，上下文层面获得专业行为模式
- 实现"同一 Agent，不同行为"

## 三、部门索引

| 部门 | Persona 数 | 适用 Agent |
|:---|---:|:---|
| 01-case-practice | 5 | Strategist, Writer, Researcher, EvidenceAnalyzer |
| 02-case-management | 4 | Scheduler, DocAnalyzer, Summarizer |
| 03-client-relations | 4 | Strategist, Writer, Reporter |
| 04-due-diligence | 4 | Researcher, EvidenceAnalyzer, IssueIdentifier |
| 05-business-development | 4 | Writer, Strategist |
| 06-finance-admin | 4 | Scheduler, Reporter |
| 07-knowledge-management | 3 | Researcher, Reviewer, Strategist |

## 四、SOP 检查清单结构

每个 Persona 的 6 步 SOP：

1. **任务识别**：确认当前任务属于本部门管辖范围
2. **输入校验**：核查必要输入材料是否齐全
3. **核心分析**：执行本部门的专业分析步骤
4. **交叉验证**：与其他部门数据或外部权威对照
5. **输出生成**：按标准化模板生成成果
6. **边界检查**：确认输出不越法律分析边界（不构成法律意见）

## 五、使用方式

Agent 执行任务时，读取对应 Persona 文件，将其内容注入当前上下文。Persona 的输出模板覆盖 Agent 的默认输出格式，SOP 检查清单追加为 Agent 的内部核查步骤。
