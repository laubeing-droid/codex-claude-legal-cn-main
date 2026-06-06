# AGENTS.md — Agent 行为规范与系统拓扑

本文档定义 unified-legal-ai-cn 系统中所有 AI Agent 的行为准则。

**主运行平台：WorkBuddy（多Expert并行协作）**
**兼容平台：CodeX Desktop（串行工作流）**

---

# 第一部分：5-Agent 协作体系

## 系统定位

unified-legal-ai-cn 通过 5 个专业 Agent 处理诉讼全生命周期的分析工作。每个 Agent 内嵌了对应的法律推理知识（不再以独立知识技能文件加载），仅依赖工具技能（`skills/tools/`）执行具体操作。形成从文档输入到文书输出的完整流水线。

## Agent 拓扑

```
                    ┌──────────────┐
                    │  DocAnalyzer │  ← 文档入口 + 证据分析
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │IssueIdentifier│ ← 争议焦点识别
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼───┐ ┌─────▼────┐ ┌────▼─────┐
       │Researcher │ │Strategist│ │  Writer  │
       │ 法条检索  │ │策略规划  │ │ 文书起草  │
       └──────────┘ └──────────┘ └──────────┘
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼───────┐
                    │  /reviewer   │  ← 独立审计命令
                    └──────────────┘
```

## WorkBuddy 上的运行方式

在 WorkBuddy 平台上，5 个 Agent 注册为 5 个独立 Expert，通过 Team 机制并行协作：

- DocAnalyzer 与 IssueIdentifier 可同时运行
- Researcher 与 Strategist 可并行推理
- Writer 等待上游产出后执行
- Reviewer 作为独立命令在任意阶段触发审计

## CodeX 上的运行方式

在 CodeX Desktop 上，5 个 Agent 按工作流阶段串行执行：

```
DocAnalyzer → IssueIdentifier → [Researcher / Strategist] → Writer → /reviewer
```

## 协作核心原则

1. **理解用户意图优先** — 先理解用户想要什么结果，再执行操作
2. **遵循工作流** — WorkBuddy 上通过 Team 编排，CodeX 上串行执行
3. **信息连贯** — 案件关键信息在 Agent 间传递时保持完整
4. **中文优先** — 所有回复使用中文
5. **JC 检测优先** — 每个 Agent 启动时检测 juris-calculus 状态，有条件时委托内核

## 全局宪法层（DNA Layer）

系统启动时自动扫描 `.claude/personas/core/user-dna.md`：

- **存在** → 作为 `[GLOBAL_CONSTITUTION]` 注入上下文顶层，优先级 `CRITICAL_OVERRIDE`
  - 5 个 Agent 的 `agent_overrides` 约束直接生效（见 DNA 文件中的 `## Agent: xxx` 章节）
  - YAML frontmatter 中的 `current_posture` 和 `risk_tolerance` 作为运行时变量
  - 修改 YAML 字段后下一条指令即时生效（热重载，无需重启）
- **不存在** → 系统正常运行，无此层约束

所有 Agent 行为同时受到 DNA 层约束和 JC 内核的推理质量保证。

## Agent 清单

| Agent | 职责 | 内联知识 | 工具依赖 |
|-------|------|---------|---------|
| DocAnalyzer | 文档入口 + 证据分析 | evidence-evaluation, legal-document-summarization | legal-ocr, pdf-organizer, pdf-processor |
| IssueIdentifier | 争议焦点识别 | conflict-resolution, argument-chain-construction | — |
| Researcher | 法条与类案检索 | case-retrieval, legal-interpretation-argument | multi-search, yuandian-law-search, zhihe-legal-research |
| Strategist | 策略规划与风险评估 | legal-risk-assessment | litigation-analysis |
| Writer | 文书起草与报告生成 | legal-document-formatting, multi-document-summarization | docx, md2word, pptx, xlsx |

## 命令清单

| 命令 | 职责 | 用法 |
|------|------|------|
| `/reviewer` | 独立审计熔断 | `/reviewer [目标Agent名称]` |
| `/scheduler` | 案件流程调度 | `/scheduler [案件ID] --status` |
| `/cold-start` | 首次使用配置（有DNA文件时跳过提问） | `/cold-start` |
| `/import-skill` | 导入自定义 Skill（自动分类+审计+归位） | `/import-skill [文件路径]` |

---

## 自定义 Skill 处理规则

用户自行导入的 Skill 按类型分类归位：

| 类型 | 归位路径 | 说明 |
|------|---------|------|
| 领域应用型 (domain) | `skills/tools/legal-cn-appl/{domain}/skills/` | 挂到对应法领域下 |
| 工具扩展型 (tool) | `skills/tools/custom-{name}/` | 自带 SKILL.md + scripts/ |
| 方法论/逻辑型 (methodology) | `skills/extensions/{name}.md` | 不自动注入上下文 |

通过 `/import-skill` 命令导入，自动完成 YAML 校验、合规审计、物理归位和路由注册。

---

# 第二部分：juris-calculus 内核集成

所有 Agent 在工作流启动时执行推理内核检测：

```
Agent 启动 → 调用 tools/list → 检查 trirail_collide 是否可用
  ├─ 可用 → juris-calculus 模式
  │   Strategist: trirail_collide 三轨对撞 + check_threat
  │   Researcher: get_citation + legal://cn-rules
  │   Reviewer:   check_threat 威胁扫描
  │   Writer:     generate_memo 格式化备忘录
  │
  └─ 不可用 → Prompt 推理模式（标注 [JC 不可达]）
      工作流正常执行，不阻塞
```

---

# 第三部分：JC 条件加载

## 法律护栏

| 状态 | 加载策略 |
|------|---------|
| JC 在线 | 不加载 guards 文件（由 prc_us_alignment.py 三层看门狗执行） |
| JC 离线 | 加载 blocking-list.md（29项）+ meta-rules.md（五层判定） |

## 知识技能

| 状态 | 加载策略 |
|------|---------|
| JC 在线 | 不加载 knowledge（委托 JC 推理） |
| JC 离线 | 使用 Agent 定义中内联的知识模板降级 |

## 冷启动

| 条件 | 行为 |
|------|------|
| 首次使用 | 提示运行 `/cold-start` |
| 已配置 | 加载 `.claude/practice-profile.json` |
| `--redo` | 覆盖已有配置 |
