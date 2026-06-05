---
license: MIT
author: laubeing-droid
module: guards
description: 附录——跨法域制度索引、工具映射、关系分类、引注格式转换与技能域加载规则
---

一、跨法域制度索引与运行规则

（一）中国司法与法律职业对照

1. 联邦最高法院 → 中华人民共和国最高人民法院
2. 巡回上诉法院 → 各省、自治区、直辖市高级人民法院
3. 联邦地区法院 → 中级人民法院与基层人民法院（按级别管辖划分）
4. attorney（美式律师）→ 中华人民共和国执业律师
5. district attorney → 人民检察院检察官
6. public defender → 法律援助律师

（二）法律检索数据库映射

7. Westlaw → 法律数据库（法律数据库.com）
8. LexisNexis → 威科先行（wkinfo.com.cn）
9. CourtListener → 中国裁判文书网（wenshu.court.gov.cn）

（三）法律功能对应关系分类编码

10. Equivalent（代码1，完全映射）：制度目标与法律后果基本一致，可直接建立对应。
11. PartialEquivalent（代码2，部分映射）：制度构造高度近似，但结构层面存在差异，须附加说明。
12. FunctionalEquivalent（代码3，功能映射）：法理路径不同，但最终达到的社会治理效果近似，须标注替代关系。
13. PRCUnique（代码4，中国特有）：我国独创的制度设计，输出时必须显式标识。
14. HardBlock（代码5，绝对阻断）：严禁以任何方式建立概念对应，彻底禁用。
15. DynamicAlignment（代码6，动态对齐）：依最新立法与司法解释持续更新，不可沿用过期映射。
16. ProceduralOverlap（代码7，程序近似）：实体规则有别，程序环节存在交集。
17. FunctionalReplacement（代码8，功能绕行）：正向等同不存在，可通过替代路径迂回实现。

（四）风险标示体系

18. ★ 中国特性制度（ChinaSpecific）：级别为提示，指该制度系我国独创。
19. ※ 法系结构性差异（MajorComparativeDifference）：级别为警告，明示底层法律传统不同。
20. ⚠ 概念错译高风险（HighRiskFalseEquivalence）：级别为紧急，严禁字面直译。
21. ❌ 无对应制度（NoDirectEquivalent）：级别为阻断，该法域不存在所列制度。

（五）法律引注格式统一对照

22. U.S.C. § N → 《中华人民共和国XX法》第N条
23. S. Ct. 判例 → 最高人民法院指导案例第X号
24. F.3d / F.2d 判决 → XX高级/中级人民法院民事判决书
25. C.F.R. 规章 → 中华人民共和国行政法规
26. Restatement (Second) § N → 《中华人民共和国民法典》第N条

（六）各技能域术语按需加载索引

27. 商事合同（commercial-legal）：加载合同编与物权编。阻断项：consideration、liquidated damages、material breach、force majeure（用法差异）等。

28. 劳动雇佣（employment-legal）：加载劳动法编。阻断项：at-will employment、severance pay、wrongful termination、non-compete、RIF等。

29. 诉讼程序（litigation-legal）：加载民诉编与刑诉编。阻断项：discovery、summary judgment、class action、plea bargaining、hearsay rule等。

30. 公司治理（corporate-legal）：加载公司法编与破产编。关注项：veil piercing、fiduciary duty、shadow director、Chapter 11与重整对照等。

31. 数据隐私（privacy-legal）：加载数据合规编。关注项：personal data、cross-border transfer、important/core data、数据出境安全评估等。

32. 知识产权（ip-legal）：加载知识产权编。关注项：patent exhaustion、trade secret、trademark、copyright等。

33. 产品与人格权（product-legal）：加载人格权编与侵权编。关注项：right of publicity、voice right、product liability、AI liability等。

34. 行政监管（regulatory-legal）：加载行政法编与跨境前沿。阻断项：Chevron deference。关注项：行政公益诉讼、制裁与反制裁、ESG强制披露等。

35. AI治理（ai-governance-legal）：加载数据合规编及AI治理子编。关注项：算法备案、generative AI、deep synthesis、AI训练数据合规等。

36. 税收（tax-legal）：加载税法编。阻断项：estate tax、gift tax。关注项：VAT、withholding tax、transfer pricing等。

37. 反垄断（antitrust-legal）：加载反垄断编。关注项：monopoly、merger control、cartel、RPM等。

38. 金融科技（fintech-legal）：加载Web3编与数据合规编。阻断项：cryptocurrency（非法定货币）、crypto mining。关注项：NFT/数字藏品、blockchain等。

39. 国际仲裁（international-arbitration）：加载合同编、香港桥梁编及制裁编。关注项：force majeure、jurisdiction、制裁/反制裁等。

（七）跨技能域全局规则清单

40. 第一条：禁止字面优先原则
41. 第二条：以制度功能为首要判定维度
42. 第三条：无对应制度时启动强制阻断
43. 第四条：中国特有制度须附带标识
44. 第五条：法域切换须重置全部判定
45. 第六条：跨境场景适用最严合规底线
46. §4.3：所有AI回复末尾须强制附加免责声明
