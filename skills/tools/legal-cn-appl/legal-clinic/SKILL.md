---
license: MIT
author: laubeing-droid
name: legal-clinic
description: 法律援助接谈、客户信函、法律备忘录、检索路线图
platforms: [codex, claude-code, workbuddy, trae]
version: 2.10.0
module: legal-clinic
status: active
triggers: 法律援助, 公益, 法律咨询
---

# 法律诊所 法务技能

## 何时使用
- 法律工作任务属于「法律诊所」领域
- 关键词触发：法律诊所,法律援助,客户接谈,备忘录

## 工作指令

每次启用时根技能已自动拉取最新版本到 技能目录

## 本地资源（由自动更新同步）
- 主指令：./CLAUDE.md
- 说明：./README.md
- 中国法参考：./references/
- 子技能：./skills/

## 中国法概念索引

当处理涉及中国法律概念对应的问题时，参考以下对齐指南：

### 阻断清单（无对应中国法制度，须拦截）

### 制度映射参考
- client intake
- memo drafting
- legal research
- pro bono

如需完整映射表，见 patches/references/alignment/legal-clinic.md。

## 重要限制
- 所有输出均为律师审查草稿，不构成法律意见
- 引用法规、案例时必须另行核验现行有效性
- 任何提交、发送或依赖前需经执业律师审核

