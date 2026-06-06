---
name: cold-start
description: "首次使用冷启动 — 检测DNA文件则跳过访谈，直接导入"
usage: "/cold-start"
---

# /cold-start —— 系统初始化

## 检测逻辑

```
/cold-start 执行时：
  ├─ 检查 .claude/personas/core/user-dna.md 是否存在
  │   ├─ 存在 → DNA 导入模式（跳过常规提问）
  │   │     输出："检测到 user-dna.md，已直接加载为全局宪法层。
  │   │            当前配置：[current_posture] / [risk_tolerance]
  │   │            如需调整，直接编辑 user-dna.md 的 YAML frontmatter 即可。"
  │   │
  │   └─ 不存在 → 标准访谈模式
  │         逐轮提问：角色 / 立场 / 风险偏好 / 常用领域 / 输出风格
  │         写入 .claude/practice-profile.json
  │
  └─ 输出：系统就绪
```

## DNA 导入模式（有 user-dna.md 时）

1. 读取 `user-dna.md` 的 YAML frontmatter，提取 `current_posture` 和 `risk_tolerance`
2. 将这两个运行时变量注入上下文（不写 JSON 中间文件）
3. 输出当前配置摘要，提示用户如需调整直接编辑 DNA 文件

## 标准访谈模式（无 user-dna.md 时）

逐轮提问：
1. 你的角色：法务 / 律所律师 / 独立执业
2. 案件立场：原告 / 被告 / 两者
3. 风险偏好：保守 / 中性 / 激进
4. 常用领域：litigation, commercial, corporate, employment, privacy 等
5. 输出风格：详细论证 / 结论优先 / 要点列表
6. JC 路径：D:\Codex\juris-calculus（可选）

写入 `.claude/practice-profile.json`。

## 核心原则

- **声明式优于交互式**：有 user-dna.md 时，冷启动只做确认，不做提问
- **热重载**：修改 `user-dna.md` 的 YAML 字段后，下一条指令即时生效，无需重新运行 cold-start
- **零状态文件**：DNA 模式下不生成 practice-profile.json，避免状态不同步
