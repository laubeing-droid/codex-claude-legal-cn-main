# unified-legal-ai-cn — 中国法律 AI 系统

面向法律实务工作者的 AI 辅助系统。覆盖诉讼全生命周期，从文档分析到文书输出。

**主运行平台：WorkBuddy（推荐，支持多Expert并行协作）**
**兼容平台：CodeX Desktop（串行工作流）**

---

## 架构

```
unified-legal-ai-cn/
├── .claude/
│   ├── agents/        5 个核心 Agent（WorkBuddy Expert / CodeX 兼容）
│   ├── commands/      3 个命令（cold-start / reviewer / scheduler）
│   ├── personas/core/ 5 个冷启动画像模板
│   └── rules/guards/  2 个法律护栏文件（条件加载）
├── skills/
│   ├── knowledge/     1 个入口路由（claude-legal-cn）
│   ├── tools/         17 个法律工具
│   │   └── legal-cn-appl/  9 个中国法领域应用（7核心+2可选）
│   ├── extensions/    用户自定义方法论技能（通过 /import-skill 导入）
│   └── shared/data/   法律语义对齐数据
├── data/              权威裁判规则数据库
├── docs/              核心文档
└── install.ps1        自动安装脚本
```

### 5-Agent 协作

| Agent | 职责 |
|-------|------|
| **DocAnalyzer** | 法律文档解析 + 证据三性评估 + 要素提取 |
| **IssueIdentifier** | 争议焦点识别 + 法律关系解构 + 论证链构建 |
| **Researcher** | 法条检索 + 构成要件拆解 + 类案搜索 + 规范效力校验 |
| **Strategist** | SWOT 态势分析 + 多策略方案 + 概率化预判 + 风险矩阵 |
| **Writer** | 文书起草 + 报告生成 + 双格式输出 |

### 4 个命令

| 命令 | 用途 |
|------|------|
| `/cold-start` | 首次使用冷启动访谈（有DNA文件时自动跳过） |
| `/reviewer` | 独立审计熔断命令 |
| `/scheduler` | 案件流程调度与期限管理 |
| `/import-skill` | 导入自定义 Skill（自动分类+审计+归位） |

### 法律护栏

- 29 项域外法律概念阻断清单
- 五层功能判定方法论
- JC 在线时由 juris-calculus 内核自动执行

### 推理内核（可选集成）

`juris-calculus` 是独立的符号化法律推理引擎，通过 MCP stdio 协议集成：
- 三轨对撞（PRC/HK/US）
- 2117 条民法典 Horn 规则
- SPC 裁判规则蒸馏
- prc_us_alignment.py 三层看门狗

详见 `docs/JURIS_CALCULUS_INTEGRATION.md`。

---

## 安装

### WorkBuddy 安装（推荐）

1. 将本仓库添加到 WorkBuddy 工作区
2. 在 **Expert Center** 中注册 5 个 Expert
3. 在 **连接器管理** 中注册 juris-calculus MCP（可选）
4. 首次使用时运行 `/cold-start` 完成配置

### CodeX Desktop 安装

```powershell
.\install.ps1
```

首次使用时运行 `/cold-start` 完成配置。

### 环境要求

- PowerShell 5.1+
- Python 3.12+（部分工具需要）

---

## 快速开始

```
运行 /cold-start         → 配置实践画像
上传起诉状/答辩状        → DocAnalyzer 自动解析
查看争议焦点分析        → IssueIdentifier 输出
检索相关法条与类案      → Researcher 执行
制定诉讼策略            → Strategist 输出策略方案
草拟法律文书            → Writer 生成 Markdown + DOCX
运行 /reviewer          → 审计熔断校验
```

---

## 外部数据源配置

| 数据源 | Token 配置 | 用途 |
|--------|-----------|------|
| 北大法宝 | pkulaw MCP 连接器（8 服务） | 法条检索 |
| 元典智库 | 环境变量配置 | 法律研究 |
| 智合法律 | 智合会员账号 | 交叉验证 |
| IMA 知识库 | ima-mcp 连接器（9 个） | 知识管理 |

---

## 许可证

MIT License. See `LICENSE` for details.
