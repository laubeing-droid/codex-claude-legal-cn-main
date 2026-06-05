---
license: MIT
author: laubeing-droid
name: employment-legal
description: 劳动合同、竞业限制、社保工伤、规章制度的起草与审查
platforms: [codex, claude-code, workbuddy, trae]
version: 2.10.0
module: employment-legal
status: active
triggers: 劳动, 用工, 离职, 裁员, 竞业限制, 工伤
---

# 劳动用工 法务技能

## 何时使用
- 法律工作任务属于「劳动用工」领域
- 关键词触发：劳动,社保,解除,竞业,规章制度,工伤,裁员

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
- **at-will employment❌**

### 制度映射参考
- labor-core-rules
- severance
- wrongful termination
- non-compete
- RIF
- workers compensation

如需完整映射表，见 patches/references/alignment/employment-legal.md。

## 重要限制
- 所有输出均为律师审查草稿，不构成法律意见
- 引用法规、案例时必须另行核验现行有效性
- 任何提交、发送或依赖前需经执业律师审核

