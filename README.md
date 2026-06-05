# unified-legal-ai-cn — 中国法律 AI 技能集合

面向 AI 编程助手的中国法律推理技能系统。覆盖诉讼全生命周期，从文档分析到文书输出。

---

## 一、架构

```
unified-legal-ai-cn/
├── .claude/
│   ├── agents/       10 个专业 Agent（诉讼全生命周期）
│   ├── personas/     28 个法律画像（7 部门，幽灵变身）
│   ├── rules/        8 个行为规范 + 6 个法律护栏
│   ├── servers/      2 个自建 MCP Server（法规库 + 案例库）
│   └── commands/     3 个自定义命令
├── skills/
│   ├── knowledge/    40 个法律推理知识技能（纯提示词）
│   ├── tools/        50 个工程化工具技能（含脚本/配置）
│   │   └── legal-cn-appl/  14 领域中国法应用技能（150+子技能）
│   └── shared/data/  插件注册表 + 法律语义对齐数据
├── data/             外部数据插件（裁判规则库）
├── docs/             开发指南与集成文档
└── install.ps1       统一部署脚本
```

### 双池 + 编排

```
编排层：10 Agent 协作（输入→分析→推理→策略→文书→审核）
    │
    ├─→ 知识池（knowledge/）  38 纯提示词法律推理技能
    └─→ 工具池（tools/）      50 工程化技能 + 14 领域应用
```

---

## 二、核心能力

### 10-Agent 协作体系

| Agent | 职责 | 搭载技能 |
|:---|:---|:---|
| DocAnalyzer | 文档分析/OCR/要素提取 | 3 |
| EvidenceAnalyzer | 证据三性评估/链路分析 | 2 |
| IssueIdentifier | 争议焦点识别/对抗盲点 | 1 |
| Researcher | 法条检索/要件拆解/类案 | 3 |
| Strategist | 策略规划/风险评估/JC三轨对撞 | 6 |
| Writer | 文书起草/论证链构建 | 3 |
| Summarizer | 材料摘要/要点提炼 | 2 |
| Reporter | 综合/阶段/专题报告 | — |
| Scheduler | 流程调度/期限管理 | 3 |
| Reviewer | 四级质量审查/风险排查 | 3 |

### 28 Persona 部门体系

7 大部门 × 28 画像，Agent 按业务属性动态加载对应 SOP 和输出模板。

### 法律护栏

- 29 项域外法律概念阻断清单（输出层速查）
- 中国法特有制度索引（28 项）
- 三法域桥接规范（内地/香港/美国术语对照）
- 强制推理链锁定（请求权基础分析/行政行为合法性审查）

---

## 三、推理内核（可选集成）

```
Agent 启动 → tools/list 检测 trirail_collide
  ├─ 可用 → juris-calculus 模式
  │   三轨对撞 + 阻断自动校验 + 格式化备忘录 + 算子辅助
  │
  └─ 不可用 → Prompt 推理模式（标注 [JC 不可达]）
      工作流正常执行，不阻塞
```

`juris-calculus` 为独立符号化推理内核，通过 MCP stdio 协议集成。详见 `docs/JURIS_CALCULUS_INTEGRATION.md`。

---

## 四、快速开始

### 安装

```powershell
.\install.ps1
```

脚本自动检测环境、生成配置、注册本地 MCP Server，并提示 juris-calculus 状态。

### 使用

将仓库加载到 AI 编程助手的技能目录。入口路由技能 `claude-legal-cn` 自动识别律师工作场景并路由到对应领域。

---

## 五、平台兼容

| 平台 | 厂商 | 配置格式 |
|:---|:---|:---|
| CodeX Desktop | OpenAI | TOML |
| Claude Code | Anthropic | JSON |
| WorkBuddy | Tencent | JSON |
| Trae | ByteDance | JSON |

详见 `docs/LEGALCN-ARCHITECTURE.md`。

---

## 六、许可

MIT License。详见 `LICENSE`。
