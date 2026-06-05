---
license: MIT
author: laubeing-droid
---

# 技能域术语映射索引

按技能域按需加载对应部门法编术语，避免全量注入造成上下文窗口浪费。

## 一、域到编对照

| 技能域 | 对应法律编 | 核心阻断术语 | 加载章节 |
|---|---|---|---|
| commercial-legal | 合同编、物权编 | consideration、nominal consideration、deed | 合同编全章及跨法系处理 |
| employment-legal | 劳动法编、合同编 | at-will employment、RIF | 劳动法编全章及跨境裁员阻断 |
| litigation-legal | 民诉编、刑诉编 | discovery、summary judgment、plea bargaining、Miranda rights、jury trial | 民诉及刑诉编全章 |
| corporate-legal | 公司法编、破产法编 | Chapter 11、automatic stay、DIP | 公司法编、破产法编及VIE架构 |
| privacy-legal | 数据合规编 | data localization、跨境传输 | 数据合规编及出境规则 |
| ip-legal | 知识产权编 | patent exhaustion、trade dress | 知识产权各子编 |
| product-legal | 人格权编、侵权编 | right of publicity | 人格权与侵权编全章 |
| regulatory-legal | 行政法编、跨境前沿 | Chevron deference、agency interpretation | 行政法及制裁反制编 |
| ai-governance-legal | 数据合规编及AI监管 | 深度合成、训练数据 | AI监管与声音权 |
| tax-legal | 税法编 | estate tax、gift tax | 税法子编 |
| antitrust-legal | 反垄断编 | cartel、RPM | 反垄断子编 |
| fintech-legal | Web3及数据合规 | cryptocurrency、crypto mining、NFT/数字藏品 | Web3与数据合规 |
| international-arbitration | 合同编、香港桥梁 | 制裁与反制裁 | 合同编、香港桥梁 |

## 二、全局加载规则

所有技能域始终加载六项基础规则：禁止字面优先、优先研判制度功能、无对应时强制阻断、中国特色制度须显式标注、法域切换不得混同、适用最严管辖规则。强制免责输出模板同样全局加载。
