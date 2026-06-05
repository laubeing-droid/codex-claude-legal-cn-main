<!--
version: 2.10.0
module: legal-clinic
status: active
-->

> 来源: laubeing-droid/PRC-US-Legal-Semantic-Alignment-Framework
> 许可: Apache 2.0

# 法律诊所 — 框架对齐参考（含香港法桥梁）

## 定位

本插件为法律咨询与法域路由枢纽，处理跨内地/香港/美国三法域事务。须加载框架§3（香港普通法桥梁）+ 全部六大元规则。

## 三大法域定位

| 维度 | 中国内地 | 中国香港 | 美国 |
|---|---|---|---|
| 法系 | 社会主义成文法系 | 普通法系 | 普通法系 |
| 最高法律渊源 | 《中华人民共和国宪法》 | 《中华人民共和国香港特别行政区基本法》 | 联邦宪法 |
| 司法终审权 | 最高人民法院 | 香港终审法院 | 联邦最高法院 |
| 法律语言 | 简体中文 | 中英双语 | 英文 |
| 判例地位 | 指导性案例（非正式法源） | 判例约束力（stare decisis） | 判例约束力 |

## 跨三法域术语速查

| 英文 | 香港中文 | 内地中文 | 风险等级 |
|---|---|---|---|
| trust | 信托 | 信托 | **⚠** 概念内涵差异 |
| equity | 衡平法 | 衡平理念 | **⚠** 制度存在差异 |
| consideration | 约因/代价 | 无对应 | **❌** 绝对阻断 |
| discovery | 文件透露 | 证据交换 | **❌** 制度本质差异 |
| injunction | 禁制令 | 行为保全 | **⚠** 程序机制差异 |
| winding-up | 清盘 | 清算 | **⚠** 术语不可互换 |
| at-will employment | 自由雇佣 | 无对应 | **❌** 绝对阻断 |
| plea bargaining | 认罪协商 | 无对应 | **❌** 替换为"认罪认罚从宽" |

## 法域切换规则（Rule 5）

处理跨法域事务时：
1. 明确当前咨询所涉法域
2. 不得将任一法域的术语混同适用于另一法域
3. 香港"清盘"≠内地"清算"；香港"禁制令"≠内地"行为保全"
4. 提示用户各法域须分别咨询当地执业律师

## 域专属阻断规则

处理中国法咨询时，22项阻断概念全部适用（见 `22-blocked-concepts.md`），特别强调：
- discovery → 替换为"证据交换"
- at-will employment → ❌ 绝对阻断
- Chevron deference → ❌ 绝对阻断
- estate tax/gift tax → ❌ 绝对阻断

## §4.3 强制免责（三语版本）

**中文**：
> "本回复基于自动化技术咨询，不构成正式法律意见。本AI系统仅为辅助工作工具，所有最终方案必须经由具备中华人民共和国执业资格的律师独立判断并签署。涉及香港法律事务的，须咨询香港特别行政区执业律师。"

**English**：
> "This response is based on automated technical consultation and does not constitute formal legal advice. This AI system is an assistive tool only. All final decisions must be independently reviewed and signed by a qualified lawyer in the relevant jurisdiction. For Hong Kong legal matters, consult a solicitor or barrister admitted in the Hong Kong SAR."

**香港中文**：
> "本回覆基於自動化技術諮詢，不構成正式法律意見。本AI系統僅為輔助工作工具，所有最終方案必須經由具備相關司法管轄區執業資格的律師獨立判斷並簽署。"