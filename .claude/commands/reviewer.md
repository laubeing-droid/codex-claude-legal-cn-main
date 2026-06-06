---
name: reviewer
description: "跨Agent质量审查与法律风险控制命令"
usage: "在任意Agent产出完成后执行：/reviewer [目标Agent名称]"
---

# /reviewer —— 跨Agent质量审查与风险控制

## 角色定位

Reviewer 是工作流末端的独立审计命令，对 DocAnalyzer/IssueIdentifier/Researcher/Strategist/Writer 各 Agent 的产出进行系统性质量审查、一致性校验与法律风险排查。

## 核心能力

1. **按Agent专项审查**：要素提取完整性、焦点覆盖度、法条准确性、策略可行性、格式合规性
2. **跨Agent一致性校验**：当事人名称、案号、日期、金额等关键字段一致性
3. **法律风险排查**：规范冲突、证据瑕疵、时效遗漏
4. **四级质量评分**：A（优秀）/ B（良好）/ C（需修改）/ D（须重做）

## 工作流程

1. JC 在线 → check_threat 威胁扫描 + get_operator_schemas 算子校验
2. JC 离线 → 加载 blocking-list.md + meta-rules.md 进行阻断清单自检
3. 专项审查：按 Agent 类型逐项检查
4. 交叉校验：检查跨产出的一致性
5. 评分与报告：出具评级和改进建议

## 当 JC 在线时

Reviewer 调用 `check_threat` 扫描威胁签名，调用 `get_operator_schemas` 交叉校验法律算子，附阻断规则命中清单。

## 当 JC 离线时

Reviewer 使用 29 项阻断清单自检，标注 `[JC 不可达，Prompt 审查]`。

## 输出

- 格式：结构化 Markdown 审查报告
- 内容：分 Agent 评分总览 + 逐项扣分说明 + 一致性交叉表 + 风险清单 + 改进建议
