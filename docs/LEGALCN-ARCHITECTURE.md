# AGENTS.md — laubeing-droid 多平台开发准则

> 本文件适用于 [laubeing-droid](https://github.com/laubeing-droid) 旗下全部仓库。
> 当你（AI Agent）处理该仓库的任何文件时，必须遵守以下准则。

---

## 一、核心准则：四平台兼容

本仓库的**所有代码、配置、技能、安装脚本**必须兼容以下四种 AI 编程平台：

| # | 平台 | 厂商 | 配置格式 | 技能路径 | 联网检索 格式 |
|:--|:-----|:-----|:---------|:---------|:---------|
| 1 | **Codex Desktop** | OpenAI | TOML | `~/.codex/skills/` | TOML `[mcp_servers.X]` |
| 2 | **Claude Code** | Anthropic | JSON | `~/.claude/skills/` | JSON `mcpServers` |
| 3 | **WorkBuddy** | Tencent | JSON | `~/.workbuddy/skills/` | JSON `mcpServers` + ZIP 包 |
| 4 | **Trae** | ByteDance | JSON | `~/.trae/skills/` | JSON `mcpServers` |

**规则：任何一个平台的接口缺失 = Bug，必须修复。**

---

## 二、平台接口要求

### 2.1 技能文件（SKILL.md）

每个 SKILL.md 必须包含以下 frontmatter，确保四平台可识别：

```yaml
---
name: skill-name # 英文标识（跨平台通用）
description: ... # 中文描述
platforms: [codex, claude-code, workbuddy, trae] # 必填
version: x.y.z
---
```

- `platforms` 字段声明该技能支持哪些平台
- 每个平台若需特殊配置，在同目录下创建 `codex.yaml` / `claude-code.json` / `workbuddy.json` / `trae.json`

### 2.2 安装脚本（install.ps1 / install.sh）

**强制规则**：
1. 安装脚本必须检测所有四个平台（参考 `platforms.ps1`）
2. 对已安装的平台，自动部署对应的技能文件/联网检索配置
3. 平台检测函数：`Get-AllPlatforms`（从 `platforms.ps1` 加载）
4. 平台特定配置统一使用 `Write-McpToPlatform` 函数

**安装脚本最小模板**：
```powershell
# 加载平台适配框架
. "$PSScriptRoot\..\platforms.ps1" # 或从独立路径加载

$platforms = Get-AllPlatforms
$active = $platforms | Where-Object { $_.Installed }

foreach ($p in $active) {
 switch ($p.Id) {
 'codex' { Deploy-ToCodex $p }
 'claude-code' { Deploy-ToClaudeCode $p }
 'workbuddy' { Deploy-ToWorkBuddy $p }
 'trae' { Deploy-ToTrae $p }
 }
}
```

### 2.3 外部检索服务配置

每个 检索服务 必须生成四种格式的配置：

| 平台 | 函数 | 配置示例 |
|:-----|:-----|:---------|
| Codex Desktop | `New-CodexMcpConfig` | `[mcp_servers.SERVER]` + `command = "..."` |
| Claude Code | `New-ClaudeMcpConfig` | `{"mcpServers": {"SERVER": {"command": "..."}}}` |
| WorkBuddy | `New-WorkBuddyMcpConfig` | `{"mcpServers": {"SERVER": {"command": "...", "type": "stdio"}}}` |
| Trae | `New-TraeMcpConfig` | `{"mcpServers": {"SERVER": {"command": "..."}}}` |

### 2.4 WorkBuddy 特殊要求

- 每技能独立打包为 ZIP（格式：`{领域}-{技能名}.zip`）
- ZIP 内必须包含 `SKILL.md` + `references/` 目录
- 同时部署解压版和 ZIP 版到 `~/.workbuddy/skills/`

### 2.5 Trae 特殊要求

- Trae 基于 VS Code 架构，配置文件在 `~/.trae/` 目录
- macOS 上可能在 `~/Library/Application Support/Trae/`
- 联网检索 配置使用 JSON 格式（与 Claude Code 相同）
- 技能部署为 VS Code 扩展兼容格式

---

## 三、仓库特定准则

### 3.1 legal-cn-main（技能主仓库）

- **skills/ 目录下全部子技能**的 SKILL.md 必须声明 `platforms` 字段
- `install.ps1` 必须部署到全部四个平台的技能目录
- 新增技能时同时生成四平台配置
- 护栏/阻断规则（blocking-list.md 中全部条目，数量会持续增长）四平台通用，但需确认 WorkBuddy 和 Trae 的加载路径

### 3.2 legal-cn-legal-cn-mcp-hub（外部检索服务）

- `detect.ps1` 必须检测全部四个平台
- 每个连接器的 `install-*` 函数必须输出四种 联网检索 配置
- `verify.ps1` 必须验证四种平台配置的正确性
- Python 检索服务 代码不受影响（平台无关），仅配置生成需要四路输出

### 3.3 legal-cn-core-codices（法律数据库）

- 本仓库是数据层，平台无关
- 但 `install.ps1` 必须确保数据 JSON 能被所有四个平台访问
- 符号链接策略：在四个平台的技能目录下创建指向数据的符号链接

### 3.4 alignment-framework（语义对齐）

- 框架文档是平台无关的纯文本
- 但 `install.ps1` 必须将框架注入到所有四个平台的 System Prompt / 知识库路径
- 对齐映射表的 JSON 版本需放在可被四平台共同访问的位置

### 3.5 legal-cn-judgment-predictor（裁判预测）

- `SKILL.md` 的 `platforms` 字段必填
- Prompt 文件（plaintiff/defendant/judge）平台无关
- `install.ps1` 部署到全部四个平台
- 联网检索 连接（类案检索）需确保四平台都可调用

---

## 四、开发流程

### 4.1 新增功能 Checklist

- [ ] 是否在全部四个平台测试了接口？
- [ ] SKILL.md 是否声明了 `platforms: [codex, claude-code, workbuddy, trae]`？
- [ ] install.ps1 是否对全部四个平台有部署逻辑？
- [ ] 联网检索 配置是否生成了全部四种格式？
- [ ] WorkBuddy ZIP 包是否正确生成？
- [ ] Trae 的配置路径是否正确（Windows/macOS 双平台）？

### 4.2 不允许的做法

- ❌ 只写 Codex Desktop 的 TOML 配置
- ❌ 硬编码 `` 路径
- ❌ 假设用户只使用一个平台
- ❌ SKILL.md 缺少 `platforms` 字段
- ❌ 联网检索 配置只输出 JSON 或只输出 TOML

### 4.3 正确做法示例

```powershell
# ✅ 正确：同时为全部平台配置
function Install-McpServer {
 $platforms = Get-AllPlatforms | Where-Object { $_.Installed }
 foreach ($p in $platforms) {
 Write-McpToPlatform -Platform $p -ServerName "my-server" -Command "python" -Args @("server.py")
 }
}

# ❌ 错误：只配置 Codex
function Install-McpServer-WRONG {
 $codexConfig = "$env:USERPROFILE\.codex\config.toml"
 Add-Content $codexConfig "[mcp_servers.my-server]`ncommand = `"python`""
}
```

---

## 五、平台检测优先级

当四个平台同时安装时，按以下优先级处理冲突：

1. **Codex Desktop** — 主开发平台，优先测试
2. **Claude Code** — 格式与 Trae 相似，合并测试
3. **WorkBuddy** — ZIP 打包逻辑独立
4. **Trae** — 与 Claude Code JSON 格式兼容

## 六、测试要求

> 详见 [十一、测试要求](#十一测试要求)

## 七、环境一致性校验（强制）

### 7.1 原则

**Python 3.9 在公司能跑、在家就炸** —— 这是典型的"环境不一致"问题。本仓库的 检索服务 依赖 `mcp>=1.0.0`（需要 Python 3.10+），`pydantic>=2.0.0`（与 v1 不兼容），`httpx>=0.27.0`。依赖链中任何一个版本漂移都会导致：

| 场景 | 表象 | 根因 |
|:-----|:-----|:-----|
| Python 3.9 | `import mcp` → SyntaxError (match/case) | mcp 需要 3.10+ |
| pydantic v1 | `from pydantic import BaseModel` → AttributeError | v2 API 不兼容 v1 |
| httpx 0.26 | AsyncClient 方法签名变化 | 0.27 breaking changes |
| Node.js 缺失 | 飞书连接器静默失败 | npm 联网检索 无法启动 |

**规则：install.ps1 的第一步必须是调用 `env-check.ps1`。阻断项存在时禁止继续安装。**

### 7.2 安装脚本集成

```powershell
# 每个 install.ps1 必须在开头加入：
$envCheck = Join-Path $PSScriptRoot "env-check.ps1"
if (Test-Path $envCheck) {
 & $envCheck
 if ($LASTEXITCODE -ne 0) {
 Write-Host "Environment check failed. Fix issues above and re-run." -ForegroundColor Red
 exit 1
 }
}
```

### 7.3 校验项目总表

| # | 检查项 | 最低要求 | 不满足后果 | 等级 |
|:--|:-----|:-----|:-----|:--|
| 1 | PowerShell | >=5.1 | 脚本语法错误 | 🔴 CRITICAL |
| 2 | Python | >=3.10 | mcp SDK 无法运行 | 🔴 CRITICAL |
| 3 | pip | 可用 | 无法安装 Python 包 | 🔴 CRITICAL |
| 4 | Git | 可用 | 无法克隆依赖仓库 | 🔴 CRITICAL |
| 5 | GitHub 可达 | 网络通 | 无法下载仓库 | 🔴 CRITICAL |
| 6 | PyPI 可达 | 网络通 | 无法安装 pip 包 | 🔴 CRITICAL |
| 7 | mcp 包 | >=1.0.0 | 检索服务 启动失败 | 🟡 WARNING |
| 8 | httpx 包 | >=0.27.0 | API 调用异常 | 🟡 WARNING |
| 9 | pydantic 包 | >=2.0.0 (非 v1) | server.py 崩溃 | 🔴 CRITICAL |
| 10 | Node.js | >=18.0 | 飞书连接器不可用 | 🟡 WARNING |
| 11 | 磁盘空间 | >=1 GB | 无法克隆仓库 | 🔴 CRITICAL |
| 12 | 平台检测 | 至少一个 | 没有部署目标 | 🟡 WARNING |

### 7.4 用户修复指引

校验失败时，输出精确的修复命令（而非笼统的"请升级 Python"）：

```
[X] [Python] Python 3.9 — mcp SDK requires >=3.10
 fix: winget install Python.Python.3.12

[X] [Pkg] pydantic v1 detected! v2 API incompatible
 fix: pip uninstall pydantic -y; pip install 'pydantic>=2.0.0'
```

---

## 八、提交规范（Conventional Commits）

### 8.1 格式

```
<type>(<scope>): <description>

[optional body]
```

### 8.2 Type 定义

| Type | 用途 | 示例 |
|:-----|:-----|:-----|
| `feat` | 新功能/新技能 | `feat(legal-cn-mcp-hub): add Trae 联网检索 config support` |
| `fix` | Bug 修复 | `fix(env-check): pydantic v1 detection false negative` |
| `docs` | 文档变更 | `docs: update PLATFORM_SPEC.md with Trae path` |
| `chore` | 构建/工具/依赖 | `chore: bump mcp from 1.0.0 to 1.1.0` |
| `refactor` | 重构（无功能变更） | `refactor(detect): extract platform enum` |
| `test` | 测试 | `test: add pydantic v1/v2 compatibility test` |
| `perf` | 性能优化 | `perf(server): reduce httpx timeout` |
| `security` | 安全修复 | `security: sanitize API key in logs` |

### 8.3 Scope 定义

| Scope | 含义 |
|:-----|:-----|
| `legal-cn-mcp-hub` | 外部检索服务中心 |
| `cn-main` | 法律技能主仓库 |
| `jdp` | 裁判预测 |
| `aln` | 中美法律对齐 |
| `codices` | 法律数据库 |
| `env-check` | 环境校验 |
| `platforms` | 平台适配框架 |

---

## 九、版本管理（Semantic Versioning）

### 9.1 规则

```
MAJOR.MINOR.PATCH
 │ │ └─ 修复：Bug fix，不改变 API
 │ └─────── 新增：向后兼容的新功能
 └───────────── 破坏性：不兼容的 API 变更
```

### 9.2 触发条件

| 变更 | 版本 | 要求 |
|:-----|:--|:-----|
| 新增技能/连接器 | MINOR++ | CHANGELOG 条目 |
| 修复 Bug | PATCH++ | CHANGELOG 条目 |
| 删除/重命名 API | MAJOR++ | CHANGELOG + 迁移指南 |
| 平台支持变更 | MINOR++ | PLATFORM_SPEC.md 同步更新 |
| 新增依赖 | MINOR++ | requirements.txt + env-check 同步 |

### 9.3 版本同步

所有五个仓库的版本号**独立管理**，但在 ECOSYSTEM.md 中记录对照表。

---

## 十、安全准则（强制）

### 10.1 凭证管理

```
❌ 禁止：API Key / Token / 密码 硬编码在代码中
❌ 禁止：.env 文件提交到 Git
✅ 必须：使用环境变量或 .env.example 模板
✅ 必须：日志/错误信息中脱敏凭证
```

### 10.2 .gitignore 最小要求

```gitignore
.env
*.key
*.pem
*.token
credentials.json
**/__pycache__/
node_modules/
```

### 10.3 敏感信息检测

提交前检查：
- [ ] 无硬编码 API Key
- [ ] 无硬编码 Token/Cookie
- [ ] 无内网 IP/域名
- [ ] 无真实客户案件数据

---

## 十一、测试要求

### 11.1 最低要求

| 仓库 | 提交前必测 | 测试方式 |
|:-----|:-----|:-----|
| legal-cn-mcp-hub | 检索服务 启动 | `python servers/*/scripts/server.py --help` |
| legal-cn-mcp-hub | 配置生成 | `.\verify.ps1` |
| legal-cn-main | 技能加载 | Codex Desktop 中验证 |
| legal-cn-main | 护栏有效 | `.\benchmark\run-benchmark.ps1` |
| JDP | Prompt 有效 | 模拟输入测试 |
| codices | JSON 格式 | `python -m json.tool` 校验 |
| ALN | 阻断清单完整 | blocking-list.md 中全部条目存在 |

### 11.2 不要求

- 不要求覆盖率指标（法律 AI 不适合传统单元测试）
- 不要求 CI 全绿（部分测试依赖外部 API）

---

## 十二、分支与 PR 规范

### 12.1 分支策略

```
main ─────●──────────●──────────●──→ 生产就绪
 \ /
feature/A ──●──●──●─┘
```

- **main**：受保护，直接推送仅限维护者
- **feature/***：功能分支，合并后删除
- **fix/***：Bug 修复分支

### 12.2 PR 最小 Checklist

```
[ ] 四平台兼容（Codex / Claude Code / WorkBuddy / Trae）
[ ] env-check.ps1 通过
[ ] 无硬编码凭证
[ ] CHANGELOG 已更新
[ ] 版本号已更新（如有需要）
[ ] 相关文档已同步
```

---

## 十三、文档要求

### 13.1 代码与文档同步

- 任何 API / 配置 / 接口变更，**必须同步更新**对应 `.md` 文档
- 新增技能必须更新 `ECOSYSTEM.md` 或 `FILE_INDEX.md`
- 新增 外部检索服务必须更新 `detect.ps1`

### 13.2 法律引用标准

所有法条引用必须使用可核验格式：
```
✅ 《民法典》第 584 条
✅ 《刑法》第 232 条
❌ "根据相关法律规定"
❌ 未标注来源的司法解释
```

---

## 十四、依赖管理

### 14.1 版本锁定

| 语言 | 锁定文件 | 更新方式 |
|:-----|:-----|:-----|
| Python | `requirements.txt`（下限版本） | 手动审查后 bump |
| PowerShell | `#Requires -Version` 声明 | 同步 env-check 阈值 |
| Node.js | `package.json`（如有） | 手动审查后 bump |

### 14.2 依赖添加流程

1. 在分支中修改 `requirements.txt`
2. 同步更新 `env-check.ps1` 中的最低版本要求
3. 测试 检索服务 启动
4. PR 中说明新增依赖的理由

---

> **规则优先级**：安全准则 > 环境校验 > 四平台兼容 > 版本管理 > 提交规范 > 其他
---

## 十五、AI 自动代码审计（强制）

> 当你（AI Agent）处理本仓库任何文件时，**每次操作后自动执行以下审计**。审计结果分级输出，阻断项必须在提交前修复。

### 15.1 审计时机

| 时机 | 审计范围 | 阻断级别 |
|:-----|:-----|:--|
| **每次文件修改后** | 被修改文件 + 直接依赖文件 | 🔴 CRITICAL |
| **git commit 前** | 全部变更文件 | 🔴 CRITICAL |
| **git push 前** | 全仓库快扫 | 🟡 WARNING |
| **每周自动** | 全仓库深度扫描（CI） | 🟡 WARNING |

### 15.2 审计规则表

#### A. 安全审计（Security）

| # | 规则 | 检测方式 | 级别 | 自动修复 |
|:--|:-----|:-----|:--|:--|
| S1 | 无硬编码 API Key / Token / 密码 | 正则匹配 `ghp_` `sk-` `Bearer` + 长度>20 的 base64 | 🔴 | ❌ 人工 |
| S2 | 无硬编码 Cookie / Session | 正则匹配 `Cookie:` `SESSION=` 含长字符串 | 🔴 | ❌ 人工 |
| S3 | 无内网 IP / 域名 | 正则 `10.\d+` `192.168.` `172.16-31.` | 🔴 | ❌ 人工 |
| S4 | 无真实客户案件数据 | 含身份证号/手机号/案号的非示例数据 | 🔴 | ❌ 人工 |
| S5 | .env 在 .gitignore 中 | 检查 `.gitignore` 是否含 `.env` | 🔴 | ✅ 自动 |
| S6 | 日志中凭证脱敏 | `Write-Host` / `print()` 含 key/token 参数 | 🟡 | ✅ 自动 |

#### B. 平台兼容审计（Platform）

| # | 规则 | 检测方式 | 级别 | 自动修复 |
|:--|:-----|:-----|:--|:--|
| P1 | SKILL.md 声明 platforms 字段 | 正则 `platforms:` 是否存在 | 🔴 | ✅ 自动 |
| P2 | install.ps1 含四平台部署逻辑 | 检查是否有 codex/claude/workbuddy/trae 分支 | 🔴 | ❌ 人工 |
| P3 | 联网检索 配置生成全部四种格式 | 检查 TOML + JSON 输出 | 🔴 | ❌ 人工 |
| P4 | 平台路径不使用硬编码 | 检查无 `` 字符串 | 🟡 | ✅ 自动 |
| P5 | 新增文件在四个平台均可达 | 检查路径引用方式 | 🟡 | ❌ 人工 |

#### C. 依赖审计（Dependency）

| # | 规则 | 检测方式 | 级别 | 自动修复 |
|:--|:-----|:-----|:--|:--|
| D1 | requirements.txt 版本与 env-check 一致 | 逐行比对最低版本 | 🔴 | ✅ 自动 |
| D2 | 无已知漏洞依赖 | `pip-audit` 或 `npm audit` | 🟡 | ❌ 人工 |
| D3 | 无循环依赖 | 检查仓库间引用 | 🔴 | ❌ 人工 |
| D4 | Python >=3.10 / Node >=18 | 与 env-check.ps1 阈值一致 | 🔴 | ❌ 人工 |

#### D. 法律内容审计（Legal）

| # | 规则 | 检测方式 | 级别 | 自动修复 |
|:--|:-----|:-----|:--|:--|
| L1 | 法条引用格式可核验 | 正则 `《.+》第 \d+ 条` 或标准格式 | 🟡 | ✅ 自动 |
| L2 | 无美式法律概念渗入 | 检测 blocking-list.md 中全部阻断关键词 | 🔴 | ✅ 自动 |
| L3 | 引用标注来源 | `[需核验]` `[来源:XXX]` 格式 | 🟡 | ✅ 自动 |
| L4 | 免责声明完整 | SKILL.md 含 `不构成正式法律意见` | 🔴 | ✅ 自动 |

#### E. 代码质量审计（Quality）

| # | 规则 | 检测方式 | 级别 | 自动修复 |
|:--|:-----|:-----|:--|:--|
| Q1 | PowerShell 脚本有 `#Requires` 声明 | 检查 .ps1 文件头 | 🟡 | ✅ 自动 |
| Q2 | 函数有注释帮助 | `Get-Help` 可解析的注释块 | 🟡 | ❌ 人工 |
| Q3 | 无 `Write-Host` 在库函数中 | 库函数用 `Write-Output` | 🟡 | ✅ 自动 |
| Q4 | Python 文件无语法错误 | `python -m py_compile` | 🔴 | ❌ 人工 |
| Q5 | JSON 文件格式合法 | `python -m json.tool` 校验 | 🔴 | ✅ 自动 |

### 15.3 审计输出格式

每次审计输出单行摘要 + 问题清单：

```
[审计] 文件: 12 | 🔴 2 | 🟡 3 | ✅ 7
 🔴 [S1] install.ps1:30 — 疑似硬编码 Token
 修复: 替换为 $env:API_TOKEN
 🔴 [P1] my-skill/SKILL.md — 缺少 platforms 字段
 修复: 添加 platforms: [codex, claude-code, workbuddy, trae]
 🟡 [L1] contract-review/SKILL.md:42 — 法条引用格式不规范
 修复: "民法典584条" → "《民法典》第 584 条"
```

### 15.4 自动修复权限

| 可自动修复 | 需人工确认 |
|:-----|:-----|
| ✅ 添加缺失的 platforms 字段 | ❌ 涉及 API Key / Token 的任何代码 |
| ✅ 修复法条引用格式 | ❌ 修改业务逻辑 |
| ✅ 添加 .gitignore 条目 | ❌ 删除/修改文件内容 |
| ✅ 修复 JSON 格式 | ❌ 新增/删除依赖 |
| ✅ 日志脱敏 | ❌ 跨平台接口变更 |
| ✅ 添加 `#Requires` 声明 | ❌ 法律内容准确性判断 |

### 15.5 审计豁免

以下情况可标注 `@audit-skip` 跳过特定规则：
```powershell
# @audit-skip: S1 — 这是示例 Token，仅用于文档演示
$EXAMPLE_TOKEN = "ghp_example_do_not_use"
```

> 豁免必须在同一行注释中说明理由，否则视为违规。

---

## 十六、技能参数映射（`@param:` 引用）

### 16.1 规则

技能文件中的行为调优参数**不得硬编码数字**。统一使用 `@param:KEY` 格式引用，
实际值从 `skills/references/guidance-defaults.md` 解析。

```
✅ 目标覆盖 `@param:cold-start:target-items` 项
❌ 目标覆盖 10-20 项
```

### 16.2 解析流程

AI Agent 执行技能时：
1. 遇到 `@param:KEY` → 读取 `guidance-defaults.md` 中对应值
2. 值可能是数字范围（`2-5`）、阈值（`10`）、语义描述（`适量`）
3. 数字范围解析为推荐区间，AI 根据上下文选择具体值
4. 找不到键 → 使用文件中内联的默认值

### 16.3 新增参数

在 `guidance-defaults.md` 中添加一行即可，无需修改任何技能文件。
键名规范：`@param:<类别>:<描述>`，全小写，连字符分隔。

---

## 十七、硬编码数字禁令

### 17.1 原则

**项目规模的任何数字描述都会过时。当文档写"150 个技能"而实际有 200 个时，AI Agent 会被误导。**

### 17.2 禁止

| ❌ 禁止 | ✅ 替代 |
|:-----|:-----|
| `150+ 子技能` | `skills/ 目录下全部子技能` |
| `29 项阻断` | `blocking-list.md 中的全部条目` |
| `162 部法律` | `laws/ 目录下全部法律` |
| `12 个领域` | `skills/ 目录下全部领域` |
| `3 轮辩论` | `debate/rounds.md 定义的辩论轮次` |
| `22 个概念` | `全部已登记概念（见对应文件）` |
| `603 文件` | 引用目录路径，不写文件数 |
| `8 科室 27 技能` | `skills/solo-law-firm/ 下全部技能` |

### 17.3 例外

以下数字**允许**（不会因项目成长而过时）：

| 类别 | 示例 | 原因 |
|:-----|:-----|:-----|
| 版本号 | `v2.10.0` | 有明确的变更流程 |
| 法条编号 | `《民法典》第 584 条` | 法律原文约束 |
| 端口号 | `port=18062` | 技术常量 |
| 超时值 | `timeout=30.0` | 技术常量 |
| 步骤编号 | `第1步` | 流程骨架，改流程必改编号 |
| 行为参数 | `@param:cold-start:target-items` | 通过 guidance-defaults.md 映射 |

### 17.4 CI 检查

`.github/workflows/law-citation-scan.yml` 扩展检测规则：
- 扫描 `*.md` 文件中的 `\d+\s*[\+～~]*\s*(项|部|个|条|种|轮|步|层|科|文件|领域|工具|服务|蓝图|插件|仓库|模块|连接器|技能|阻断)\b` 模式
- 匹配到 → CI 警告，提示替换为文件/目录引用
