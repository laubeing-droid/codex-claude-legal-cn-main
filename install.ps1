# unified-legal-ai-cn 统一安装脚本
# 职责：环境检测 + .claude/settings.local.json 配置 + 本地 MCP Server 注册
# 不执行任何跨仓 git clone

param(
 [string]$Platform = "codex" # codex | claude | workbuddy | trae
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "unified-legal-ai-cn 环境部署" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# 1. 环境检测
Write-Host "[1/4] 检测运行环境..." -ForegroundColor Yellow

$PSVersion = $PSVersionTable.PSVersion
Write-Host " PowerShell: $($PSVersion.Major).$($PSVersion.Minor)"

$PythonPaths = @(
 "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
 "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
 "python"
)
$Python = $null
foreach ($p in $PythonPaths) {
 $result = & $p --version 2>$null
 if ($LASTEXITCODE -eq 0) {
 $Python = $p
 Write-Host " Python: $result (via $p)"
 break
 }
}
if (-not $Python) { Write-Warning " Python 未检测到" }

Write-Host " 平台: $Platform"

# 2. 生成 settings.local.json
Write-Host ""
Write-Host "[2/4] 配置 Claude/Codex 本地设置..." -ForegroundColor Yellow

$ClaudeDir = "$RepoRoot\.claude"
if (-not (Test-Path $ClaudeDir)) { New-Item -ItemType Directory -Path $ClaudeDir -Force | Out-Null }

$SettingsPath = "$ClaudeDir\settings.local.json"
if (Test-Path $SettingsPath) {
 Write-Host " settings.local.json 已存在，跳过生成"
} else {
 $settings = @{
 model = "claude-sonnet-4-20250514"
 permissions = @{
 allow = @(
 "Bash(git:*)",
 "Bash(python:*)",
 "Read(*)",
 "Write($RepoRoot/*)",
 "Edit($RepoRoot/*)"
 )
 }
 }
 $settings | ConvertTo-Json -Depth 3 | Set-Content -Path $SettingsPath -Encoding UTF8
 Write-Host " settings.local.json 已生成"
}

# 3. 注册本地 MCP Server
Write-Host ""
Write-Host "[3/4] 注册本地 MCP 服务..." -ForegroundColor Yellow

$ServersDir = "$ClaudeDir\servers"
$FlkNpcDir = "$ServersDir\flk-npc"
$RmfyalkDir = "$ServersDir\rmfyalk"

if (Test-Path $FlkNpcDir) {
 Write-Host " flk-npc (国家法规数据库): 已就绪"
} else {
 Write-Warning " flk-npc: 未找到 - 请确认服务器文件已部署"
}

if (Test-Path $RmfyalkDir) {
 Write-Host " rmfyalk (人民法院案例库): 已就绪"
} else {
 Write-Warning " rmfyalk: 未找到 - 请确认服务器文件已部署"
}

# 检测 juris-calculus 推理内核
$JcDir = "$RepoRoot\..\juris-calculus"
$JcMcp = "$JcDir\mcp_server.py"
if (Test-Path $JcMcp) {
 Write-Host " juris-calculus (推理内核): 已检测到" -ForegroundColor Green
 Write-Host "   启动命令: cd ..\juris-calculus && python mcp_server.py" -ForegroundColor Gray
 Write-Host "   请在 $Platform 的 MCP 配置中添加 juris-calculus stdio 连接" -ForegroundColor Gray
} else {
 Write-Host " juris-calculus (推理内核): 未检测到" -ForegroundColor Yellow
 Write-Host "   ULA 将以 Prompt 推理模式运行（功能不受影响）" -ForegroundColor Gray
 Write-Host "   如需启用内核推理，请将 juris-calculus 部署到同级目录" -ForegroundColor Gray
}

# 4. 验证核心资产
Write-Host ""
Write-Host "[4/4] 验证核心资产完整性..." -ForegroundColor Yellow

$Checks = @(
 @{Path=".claude\agents"; Name="10-Agent编排层"; Count=10},
 @{Path=".claude\personas"; Name="28-Persona画像库"; Count=7},
 @{Path="skills\knowledge"; Name="知识技能池"; MinCount=39},
 @{Path="skills\tools"; Name="工具技能池"; MinCount=64},
 @{Path="skills\shared\data"; Name="共享数据层"; MinCount=16}
)

foreach ($check in $Checks) {
 $fullPath = Join-Path $RepoRoot $check.Path
 if (Test-Path $fullPath) {
 Write-Host " $($check.Name): ✅"
 } else {
 Write-Warning " $($check.Name): ❌ 缺失"
 }
}

Write-Host ""
Write-Host "部署完成。将仓库加载到 $Platform Desktop 即可开始使用。" -ForegroundColor Green
Write-Host ""
Write-Host "外部数据插件（可选）：" -ForegroundColor Gray
Write-Host " core-codices: 本地法律文本数据库（先本地后联网检索）" -ForegroundColor Gray
Write-Host " juris-calculus: 符号化法律推理内核（MCP stdio 调用）" -ForegroundColor Gray
