# AGENTS.md — Agent 行为规范与技能工程标准

本文档定义 unified-legal-ai-cn 系统中所有 AI Agent 的行为准则。分为两部分：前半部分定义 10-Agent 协作体系（面向诉讼全生命周期），后半部分定义技能工程化开发规范（面向系统扩展）。

---

# 第一部分：10-Agent 协作体系

## 系统定位

unified-legal-ai-cn 通过 10 个专业 Agent 处理诉讼全生命周期的分析工作。每个 Agent 搭载对应的法律推理知识技能（`skills/knowledge/`）和工程化工具技能（`skills/tools/`），形成从文档输入到文书输出的完整流水线。

## 核心工作模式

**两种入口，任选其一：**

1. **文档入口**：上传法律文档 → 自动识别类型 → 触发对应工作流
2. **场景入口**：描述需求（如"我收到了起诉状"）→ 自动匹配工作流

详细工作流定义见 `.claude/rules/Workflow.md`。

## 协作核心原则

1. **理解用户意图优先** — 在执行任何操作前，先理解用户想要什么结果
2. **遵循工作流规范** — 使用预设工作流或自由组合 Agent，减少手动操作
3. **保持上下文连贯** — 案件信息在 Agent 间传递时，确保关键信息不丢失
4. **输出到正确位置** — 每个 Agent 有固定的输出目录，遵循 `.claude/rules/AgentMapping.md`
5. **文档边界清晰** — 项目建设文档（`docs/`）与案件档案严格分开
6. **技能自动加载** — 每个 Agent 定义文件头部声明了其搭载的知识技能和工具技能，启动时自动注入
7. **中文优先** — 所有回复必须使用中文，无论用户使用何种语言提问

## 重要指令

- Do what has been asked; nothing more, nothing less.
- NEVER create files unless they're absolutely necessary.
- ALWAYS prefer editing an existing file to creating a new one.
- NEVER proactively create documentation files (*.md) unless requested.

## 规范文件索引（按需查阅）

| 目录 | 何时查阅 |
|------|---------|
| `.claude/agents/` | 定义某个 Agent 的详细职责和注入技能 |
| `.claude/rules/` | 工作流、输出标准、时间规范等核心规则 |
| `.claude/commands/` | /new-case、/deepresearch 等命令用法 |
| `skills/knowledge/` | 38 个法律推理知识技能（Agent 知识增强层） |
| `skills/tools/` | 50 个工程化工具技能（Agent 工具能力层） |
| `docs/` | 技能开发、评估、编排指南 |

### juris-calculus 推理内核集成

所有 Agent 在工作流启动时执行推理内核检测：

```
Agent 启动 → 调用 tools/list → 检查 trirail_collide 是否可用
  ├─ 可用 → juris-calculus 模式
  │   Strategist: trirail_collide 三轨对撞 + check_threat
  │   Researcher: get_citation + legal://cn-rules + route_state
  │   Reviewer:   check_threat 威胁扫描 + get_operator_schemas
  │   Writer:     generate_memo 格式化备忘录
  │   Scheduler:  route_state + generate_task_schema
  │
  └─ 不可用 → Prompt 推理模式（标注 [JC 不可达]）
      工作流正常执行，不阻塞、不报错
```

内核检测逻辑实现于各 Agent 的 `工作流程` 第一节，入口路由技能（`claude-legal-cn`）在任务启动前执行全局检测。

---

# 第二部分：技能工程化开发规范

## 核心原则

- **技能导向**：每个技能独立成树，根目录直接包含 `SKILL.md`、`references/` 等资源和配套文档
- **文档即上下文**：关键决策、路线、任务、变更、日志记录在各技能目录下
- **透明变更**：任何对用户或协作者有影响的修改写入 `CHANGELOG.md`，重要决策写入 `DECISIONS.md`
- **技能级文档**：`CHANGELOG.md`、`DECISIONS.md`、`TASKS.md` 等文档均为技能级别
- **保留证据**：输出引用需可回溯到来源文件；缺失信息明确标注"未提及/待补充"

## 目录约定

每个技能目录的标准结构：

```
skills/{layer}/{skill-name}/
├── SKILL.md # 必填，含 Unified Frontmatter
├── README.md # 可选
├── CHANGELOG.md # 变更日志
├── DECISIONS.md # 决策记录
├── TASKS.md # 任务跟踪
├── LICENSE.txt # 可选
├── config/ # 配置模板
├── references/ # 参考文档
├── scripts/ # Python/JS 脚本
├── assets/ # 静态资源
└── templates/ # 输出模板
```

### Unified Frontmatter 规范

所有 `SKILL.md` 头部的 YAML frontmatter 使用统一格式：

```yaml
---
id: "legal-ai:skill:{skill-name}" # 统一命名空间
name: "Human Readable Name"
layer: "knowledge" | "tools" # 所属层级
category: "fact-processing" # 对应功能大类
tags: ["tag1", "tag2"]
version: "1.0.0"
license: "MIT" | "MIT" # 具体许可证
author: "Author Name"
dependencies: # 依赖项
 - type: "agent"
 id: "AgentName"
---
```

## 依赖管理

### SKILL.md 依赖章节格式

```markdown
## 依赖

### 系统依赖
| 依赖 | 安装方式 |
|------|----------|
| 软件名 | macOS: `brew install xxx`<br>Linux: `sudo apt-get install xxx` |

### Python 包
| 包名 | 用途 | 安装命令 |
|------|------|----------|
| `package-name` | 用途说明 | `pip install package-name` |
```

### 脚本依赖防护

**所有包含外部依赖的脚本必须做优雅降级处理**：
- **硬依赖**：try/except 包裹 import，捕获后输出清晰的安装提示并退出
- **可选依赖**：try/except 包裹 import，设置 `HAS_XXX = False` 标志降级处理

## 命名规范

- 所有目录名统一使用 **kebab-case**（小写字母 + 连字符）
- 技能 ID 格式：`legal-ai:skill:{kebab-case-name}`
- 禁止 PascalCase 或 camelCase 目录名

## 测试标准

- 每个包含脚本的技能应提供 `scripts/tests/` 目录
- 核心功能路径必须有回归测试
- 测试使用技能根目录的相对路径（`SKILL_ROOT = Path(__file__).resolve().parents[2]`）
