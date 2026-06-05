---
license: MIT
author: laubeing-droid
name: evidence-review
description: 证据质证 — 对新证据进行三性审查，输出质证意见与补充清单
---

# 证据质证

**版本**: v3.0
**更新日期**: 2026-06-05

## 一、功能说明

围绕新证据完成真实性、合法性、关联性三性分析，并输出质证意见书和证据补强建议。

## 二、调用方式

```bash
/evidence-review [参数]
```

### （一）必选参数

- `--evidence-path` 证据文件路径（pdf / docx / 图片）
- `--case-id` 案件编号

### （二）可选参数

- `--evidence-type` 证据类型（合同、发票、转账记录、聊天记录、邮件、录音、录像、照片、证言、鉴定报告、其他）
- `--evidence-source` 来源（己方提供、对方提供、法院调取、第三方提供）
- `--reviewer-name` 质证人姓名
- `--output-dir` 输出目录（默认按 AgentMapping.md 中 EvidenceAnalyzer 的主目录）

## 三、调用示例

### （一）单项证据
```bash
/evidence-review \
  --evidence-path "合同书.pdf" \
  --case-id "[2025]京0105民初1234号" \
  --evidence-type "合同" \
  --evidence-source "对方提供" \
  --reviewer-name "李四律师"
```

### （二）批量目录
```bash
/evidence-review \
  --evidence-path "证据材料/" \
  --case-id "[2025]京0105民初1234号" \
  --reviewer-name "赵六律师"
```

## 四、子智能体调用链

对应 Workflow.md 中的"新证据质证"场景：

1. DocAnalyzer — 解析证据，提取结构化字段
2. EvidenceAnalyzer — 三性质证，输出质证意见
3. Researcher — 关联法条与判例检索
4. Writer — 撰拟质证意见书与补充证据清单
5. Summarizer — 生成证据质证摘要

## 五、落盘目录

| 目录 | 负责智能体 | 典型产物 |
|------|-----------|---------|
| 05 证据材料 | EvidenceAnalyzer | 质证意见、补证建议 |
| 03 法律研究 | Researcher | 关联法条报告 |
| 06 法律文书 | Writer | 质证意见书 |
| 10 综合报告 | Summarizer | 质证综合报告 |

## 六、底层实现

- PDF/图片解析走 PDFProcessingRules.md 规范
- 三性分析由 EvidenceAnalyzer 执行
- 文书输出遵循 OutputStandards.md 格式约束
