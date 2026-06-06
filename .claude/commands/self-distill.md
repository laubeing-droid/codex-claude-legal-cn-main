---
name: self-distill
description: "自我蒸馏 — 扫描工作记录→发现模式→打包为SKILL→输出到D盘"
usage: "/self-distill [--full | --quick]"
---

# /self-distill —— 自我蒸馏与自动强化

## 一、定位

本命令是 ULA 系统的**元认知层**（Meta-Cognitive Layer）。它不参与任何具体的法律推理，而是定期审查系统自身的工作记录，发现重复模式，将其蒸馏为可复用的 WorkBuddy SKILL.md 包，输出到 `D:\Codex\skills-auto\`。

这是实现系统自我进化（Self-Improving Loop）的核心机制。

## 二、工作流程

```
/self-distill 执行时：
  │
  ├─ 1. 采集层：扫描工作记录
  │    ├─ D:\Codex\.workbuddy\memory\ 下最近 N 天的日志
  │    ├─ 会话历史中标记为"重复"的案件模式
  │    └─ user-dna.md 中已声明但未打包的方法论
  │
  ├─ 2. 识别层：发现重复模式
  │    ├─ 同一类型的任务出现 ≥2 次
  │    ├─ 输入/流程/输出 三要素稳定
  │    └─ WorkBuddy / ULA 现有系统尚未覆盖
  │
  ├─ 3. 蒸馏层：生成 SKILL.md
  │    ├─ 自动生成标准 YAML frontmatter
  │    ├─ 提取核心流程为可执行步骤
  │    ├─ 标记依赖的 Agent / MCP / 工具
  │    └─ 写入 D:\Codex\skills-auto\{skill-name}\SKILL.md
  │
  ├─ 4. 注册层：导入系统
  │    └─ 提示用户运行 /import-skill 路径导入
  │
  └─ 5. 报告层：输出蒸馏成果
       └─ 创建了什么、跳过了什么、还需要什么证据
```

## 三、采集源配置

| 源 | 优先级 | 说明 |
|:---|:------:|------|
| WorkBuddy 工作日志 | ★★★★★ | `D:\Codex\.workbuddy\memory\` 目录下的 daily 日志 |
| 会话历史 | ★★★★☆ | 通过 conversation_search 发现的重复模式 |
| user-dna.md 方法论 | ★★★☆☆ | 已声明但未独立打包的方法论片段 |
| 外部数据源 | ★★☆☆☆ | 同步网盘中的日志，需用户授权访问 |

## 四、蒸馏规则

### 自动化判定标准（必须全部满足）

1. **重复次数**：过去 30 天内发生 ≥2 次
2. **结构化程度**：有稳定的输入、可重复的流程、明确的输出
3. **ROI 判断**：打包为 Skill 后能实质改善速度、质量或可靠性
4. **覆盖检查**：确认 ULA 现有的 5 Agent + 4 Command + 17 Tools 没有等价的实现

### 输出形式选择

| 形式 | 适用场景 | 路径 |
|:----|:---------|:----|
| WorkBuddy SKILL.md | 纯提示词工作流 | `D:\Codex\skills-auto\{name}\SKILL.md` |
| Automation | 定时重复任务 | WorkBuddy 自动化系统 |
| Agent 内联升级 | 方法论需永久固化 | 追加到对应 Agent 定义 |
| Skip | 低频/无需自动化 | 仅记录到候选清单 |

## 五、输出结构

每次执行 `/self-distill` 后，在 `D:\Codex\skills-auto\` 下生成：

```
D:\Codex\skills-auto\
├── {skill-name}/
│   └── SKILL.md          ← 标准 WorkBuddy 格式
├── {another-skill}/
│   └── SKILL.md
└── distill-report-YYYY-MM-DD.md   ← 本次蒸馏报告
```

### SKILL.md 自动生成格式

```yaml
---
name: "{auto-detected-name}"
type: "domain | tool | methodology"
description: "{自动描述}"
source: "self-distill:YYYY-MM-DD"
dependencies: ["AgentA", "ToolB"]
version: "1.0.0"
---
```

## 六、用法

```
/self-distill              标准模式：扫描最近 7 天
/self-distill --full       全量模式：扫描最近 30 天
/self-distill --quick      快速模式：仅输出当前候选清单，不创建文件
```

## 七、注意事项

- 本命令不修改 ULA 核心文件（Agent 定义、命令等）
- 生成的 SKILL.md 需要用户自行运行 `/import-skill` 确认后导入
- 输出到 D:\Codex\skills-auto\ 后，用户可手动检查、编辑后提交到 ULA 仓库
