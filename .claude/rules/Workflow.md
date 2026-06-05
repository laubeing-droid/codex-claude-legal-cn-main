---
license: MIT
author: laubeing-droid
---

# 工作流路由配置

**版本**: v3.0
**更新日期**: 2026-06-05

## 一、路由机制

主智能体接收诉求后先判断任务类型：单一任务直接派发对应专项智能体；复合场景按预设工作流依次调度多个子智能体。

## 二、关键词路由速查

- **Writer（文书起草）**：写起诉状/答辩状/代理词/上诉状/申请书/质证意见/证据目录/委托合同/授权书
- **Researcher（法律检索）**：法律研究/找法条/查判例/司法解释/法律依据/案例分析
- **DocAnalyzer（文档解析）**：OCR/识别/解析/分析文档/提取信息/处理PDF/合同分析
- **EvidenceAnalyzer（证据分析）**：证据分析/质证/证据目录/证据审查/补充证据/证据链
- **IssueIdentifier（争议识别）**：争议焦点/争议分析/法律争议/核心争议
- **Strategist（策略分析）**：策略分析/诉讼策略/风险评估/策略制定/可行性分析/案件评估
- **Summarizer（摘要生成）**：生成摘要/简报/总结/归纳/案情概要/客户汇报
- **Scheduler（日程管理）**：期限管理/日程安排/工时统计/案件期限/开庭时间

## 三、文档自动识别

| 文档特征 | 识别词 | 对应场景 |
|---------|-------|---------|
| 起诉状 | 原告/被告/诉讼请求 | 被告应诉 |
| 证据材料 | 证据/附件/证明 | 证据质证 |
| 庭审笔录 | 庭审/审判员/当事人 | 庭审分析 |
| 判决书 | 判决/裁定/法院认为 | 判决分析 |
| 委托意向 | 委托/咨询/意向 | 法律服务方案 |
| 客户反馈 | 客户反馈/新情况/补充 | 策略优化 |
| 起诉准备 | 委托起诉/拟起诉 | 原告起诉 |
| 委托确定 | 确定委托/签署委托 | 制作委托材料 |

## 四、复合场景工作流

- **被告应诉**：DocAnalyzer → IssueIdentifier → Researcher → Strategist → Writer → Reviewer → Summarizer → Reporter
- **新证据质证**：DocAnalyzer → EvidenceAnalyzer → Researcher → Writer → Summarizer
- **庭审后分析**：DocAnalyzer → EvidenceAnalyzer → Strategist → Summarizer → Reporter
- **法律服务方案**：DocAnalyzer → IssueIdentifier → Strategist → Writer → Summarizer
- **策略优化**：DocAnalyzer → EvidenceAnalyzer → Strategist → Reporter
- **原告起诉**：DocAnalyzer → IssueIdentifier → Researcher → EvidenceAnalyzer → Writer → Summarizer → Reporter
- **制作委托材料**：DocAnalyzer → Writer → Summarizer → Reporter

## 五、执行原则

1. 主智能体统一编排，子智能体只返回结果
2. 前序子智能体输出作为后续上下文输入
3. 场景冲突时按优先级：被告应诉 > 证据质证 > 原告起诉 > 委托材料
4. 无法识别时回退通用分析流程或向用户确认

## 六、路由判定参数

- 最低关键词匹配数：2
- 启用模糊匹配与语义分析
- 置信度阈值：0.7
