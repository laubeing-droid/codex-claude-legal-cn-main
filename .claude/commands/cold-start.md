---
name: cold-start
description: "首次使用冷启动访谈 — 配置实践画像"
usage: "/cold-start [--redo]"
---

# /cold-start —— 首次使用冷启动访谈

## 用途

首次使用 ULA 时的初始化配置命令。通过交互式访谈捕获用户的角色、立场、风险偏好和常用领域，写入 `.claude/practice-profile.json`。

## 触发条件

入口路由 `claude-legal-cn` 启动时检查 `.claude/practice-profile.json`：
- **存在** → 加载实践画像，按角色/立场/风险偏好调整输出
- **不存在** → 提示"首次使用请运行 `/cold-start`"

## 冷启动访谈

逐轮提问，写入 `.claude/practice-profile.json`：

```json
{
  "role": "法务 | 律所律师 | 独立执业",           // 用户角色
  "stance": "原告 | 被告 | 两者",                  // 立场
  "risk_tolerance": "激进 | 中性 | 保守",          // 风险校准
  "primary_domains": ["litigation", "commercial"],  // 常用领域
  "output_style": "详细论证 | 结论优先 | 要点列表", // 输出偏好
  "juris_calculus_path": "D:\\Codex\\juris-calculus" // JC路径（可选）
}
```

## 各字段影响

| 字段 | 影响范围 |
|------|---------|
| role | Agent 输出风格：法务=风险管理导向，律师=策略导向 |
| stance | 策略方向：原告=主动进攻，被告=防守反击 |
| risk_tolerance | 风险评估阈值：保守=低风险建议，激进=可能性分析 |
| primary_domains | 入口路由优先匹配的领域 |
| output_style | Writer 的文书输出风格 |
| juris_calculus_path | JC 内核路径，用于 MCP 检测 |

## 用法

```
/cold-start             第一次配置
/cold-start --redo      重新配置（覆盖已有画像）
```

## 输出

- `.claude/practice-profile.json`：实践画像文件
- 后续会话自动加载，无需重复配置
