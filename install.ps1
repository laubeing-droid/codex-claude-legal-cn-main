# unified-legal-ai-cn 安装脚本
# 职责：环境检测 + Platform检测 + JC内核检测
# 设计目标：WorkBuddy主 + CodeX兼容

param()

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "unified-legal-ai-cn 环境部署" -ForegroundColor Cyan
Write-Host "主平台: WorkBuddy | 兼容: CodeX Desktop" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
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

# 2. 检测运行平台
Write-Host ""
Write-Host "[2/4] 检测运行平台..." -ForegroundColor Yellow

$isWorkBuddy = $env:CODEBUDDY_WORKSPACE -ne $null
if ($isWorkBuddy) {
 Write-Host " 平台: WorkBuddy" -ForegroundColor Green
 Write-Host " 提示: 请通过 Expert Center 注册 5 个 Expert"
 Write-Host "       在连接器面板注册 juris-calculus MCP"
} else {
 Write-Host " 平台: CodeX Desktop" -ForegroundColor Yellow
 Write-Host " 本仓库为 CodeX 兼容模式运行"

 # 生成 settings.local.json（仅CodeX需要）
 $ClaudeDir = "$RepoRoot\.claude"
 if (-not (Test-Path $ClaudeDir)) { New-Item -ItemType Directory -Path $ClaudeDir -Force | Out-Null }
 $SettingsPath = "$ClaudeDir\settings.local.json"
 if (-not (Test-Path $SettingsPath)) {
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
}

# 3. 检测 juris-calculus 推理内核
Write-Host ""
Write-Host "[3/4] 检测 juris-calculus 推理内核..." -ForegroundColor Yellow

$JcDir = "$RepoRoot\..\juris-calculus"
$JcMcp = "$JcDir\mcp_server.py"
if (Test-Path $JcMcp) {
 Write-Host " juris-calculus (推理内核): 已检测到" -ForegroundColor Green
 Write-Host "   启动命令: cd ..\juris-calculus && python mcp_server.py" -ForegroundColor Gray
 if ($isWorkBuddy) {
  Write-Host "   请在 WorkBuddy MCP 连接器中添加 juris-calculus stdio 连接" -ForegroundColor Gray
 } else {
  Write-Host "   请在 CodeX 的 config.toml 中添加 juris-calculus MCP 配置" -ForegroundColor Gray
 }
} else {
 Write-Host " juris-calculus (推理内核): 未检测到" -ForegroundColor Yellow
 Write-Host "   ULA 将以 Prompt 推理模式运行（功能不受影响）" -ForegroundColor Gray
 Write-Host "   如需启用内核推理，请将 juris-calculus 部署到同级目录" -ForegroundColor Gray
}

# 4. 验证核心资产
Write-Host ""
Write-Host "[4/4] 验证核心资产完整性..." -ForegroundColor Yellow

$Checks = @(
 @{Path=".claude\agents"; Name="5-Agent核心编排层"},
 @{Path=".claude\commands"; Name="命令脚本（含冷启动）"},
 @{Path=".claude\personas\core"; Name="核心画像模板"},
 @{Path="skills\knowledge"; Name="入口路由"},
 @{Path="skills\tools"; Name="法律工具池"},
 @{Path="skills\tools\legal-cn-appl"; Name="中国法领域应用"},
 @{Path=".claude\rules\guards\blocking-list.md"; Name="法律护栏（29项阻断清单）"}
)

foreach ($check in $Checks) {
 $fullPath = Join-Path $RepoRoot $check.Path
 if (Test-Path $fullPath) {
  Write-Host " $($check.Name):  ✅"
 } else {
  Write-Warning " $($check.Name): 缺失"
 }
}

Write-Host ""
Write-Host "部署完成。" -ForegroundColor Green

if ($isWorkBuddy) {
 Write-Host "下一步：" -ForegroundColor Gray
 Write-Host " 1. 在 WorkBuddy Expert Center 注册 5 个 Expert" -ForegroundColor Gray
 Write-Host " 2. 在连接器面板注册 juris-calculus MCP（可选）" -ForegroundColor Gray
 Write-Host " 3. 首次使用时运行 /cold-start 完成配置" -ForegroundColor Gray
} else {
 Write-Host "请将本仓库加载到 CodeX Desktop 中使用。" -ForegroundColor Gray
 Write-Host "首次使用时运行 /cold-start 完成配置。" -ForegroundColor Gray
}

Write-Host ""
Write-Host "外部数据插件（可选）：" -ForegroundColor Gray
Write-Host " juris-calculus: 符号化法律推理内核（MCP stdio 调用）" -ForegroundColor Gray
