#!/usr/bin/env bash
# ==============================================================================
# Script Name: audit-engine.sh
# Description: 自动化物理层脱敏与工程完整性自检引擎 (L1 屏障)
# Lifecycle:   Git Pre-commit Hook / CI Core Runner
# Version:     3.1.0
# Changes:
#   v3.1.0 - 增加跨平台路径兼容（MINGW/MSYS /c/Users/ 格式）
#          - 增加单行长度限制防止 ReDoS
#          - 所有 subprocess 调用增加 UTF-8 编码防御
# ==============================================================================

set -e

# ANSI 颜色配置
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0;m' # No Color

# ==================== 跨平台探测 ====================
detect_platform() {
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*) echo "windows_gitbash" ;;
        Darwin*) echo "macos" ;;
        Linux*) echo "linux" ;;
        *) echo "unknown" ;;
    esac
}
PLATFORM=$(detect_platform)

# ==================== 安全正则辅助函数 ====================
# 防止 ReDoS：跳过单行超过 MAX_LINE_LENGTH 字符的行
MAX_LINE_LENGTH=500

safe_grep() {
    local regex="$1"
    local input="$2"
    local flags="${3:-}"
    # 逐行过滤：跳过超长行，防止 ReDoS
    echo "$input" | while IFS= read -r line; do
        line_len=${#line}
        if [ "$line_len" -gt "$MAX_LINE_LENGTH" ]; then
            continue
        fi
        echo "$line"
    done | grep -E $flags "$regex" || true
}

safe_grep_count() {
    local regex="$1"
    local input="$2"
    local flags="${3:-}"
    safe_grep "$regex" "$input" "$flags" | wc -l
}

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}🚀 开源安全与完整性流水线: 正在执行物理层前置审计...${NC}"
echo -e "${BLUE}====================================================${NC}"

EXIT_CODE=0
STAGED_DIFF=$(git diff --cached 2>/dev/null || echo "")

# 阶段一：检测暂存区是否为空
if [ -z "$STAGED_DIFF" ]; then
    echo -e "${YELLOW}⚠️  提示: 暂存区无任何代码变更，仅对全量工作区实施关键项扫描。${NC}"
    STAGED_DIFF=$(git diff HEAD 2>/dev/null || echo "")
fi

# 阶段二：硬核凭证与高危指纹正则匹配
echo -e "\n${BLUE}[Phase 1/4] 🔐 扫描凭证与签名安全...${NC}"

# 正则矩阵定义
SECRETS_REGEX="(sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}|AIzaSy[a-zA-Z0-9_-]{33}|amzn\.mws\.[a-z0-9-]{36}|(password|passwd|secret|api_key)\s*=\s*['\"][^'\"]+['\"])"

HAS_SECRET=$(safe_grep_count "$SECRETS_REGEX" "$STAGED_DIFF" "-i")
if [ "$HAS_SECRET" -gt 0 ]; then
    echo -e "${RED}🚨 [BLOCKER] 检测到疑似硬编码凭证或敏感赋值!${NC}"
    safe_grep "$SECRETS_REGEX" "$STAGED_DIFF" "-n -i"
    EXIT_CODE=1
else
    echo -e "  ${GREEN}✅ 凭证特征扫描安全。${NC}"
fi

# 阶段三：网络拓扑与本地物理路径脱敏
echo -e "\n${BLUE}[Phase 2/4] 🌐 扫描基础设施拓扑残留...${NC}"
INTERNAL_IP_REGEX="[^0-9](192\.168\.[0-9]{1,3}\.[0-9]{1,3}|10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]{1,3}\.[0-9]{1,3})[^0-9]"

# 跨平台路径正则：同时兼容 Windows 原生路径 和 Git Bash /c/Users/ 路径
if [ "$PLATFORM" = "windows_gitbash" ]; then
    # Git Bash 下：C:\Users\... 和 /c/Users/... 两种格式
    ABSOLUTE_PATH_REGEX="(\/[a-zA-Z]\/[a-zA-Z0-9_-]+\/|[a-zA-Z]:\\\\(Users|home)\\[a-zA-Z0-9_-]+\\)"
    echo -e "  ${BLUE}[检测到 Git Bash 环境，启用 /c/Users/ 路径兼容模式]${NC}"
else
    ABSOLUTE_PATH_REGEX="(\/Users\/[a-zA-Z0-9_-]+\/|[a-zA-Z]:\\\\Users\\\\[a-zA-Z0-9_-]+\\\\)"
fi

HAS_TOPOLOGY=0

HAS_IP=$(safe_grep_count "$INTERNAL_IP_REGEX" "$STAGED_DIFF" "")
if [ "$HAS_IP" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  [WARNING] 代码中疑似包含内部局域网 IP 地址:${NC}"
    safe_grep "$INTERNAL_IP_REGEX" "$STAGED_DIFF" "-n"
    HAS_TOPOLOGY=1
fi

HAS_PATH=$(safe_grep_count "$ABSOLUTE_PATH_REGEX" "$STAGED_DIFF" "")
if [ "$HAS_PATH" -gt 0 ]; then
    echo -e "${RED}🚨 [BLOCKER] 包含硬编码的本地用户绝对物理路径:${NC}"
    safe_grep "$ABSOLUTE_PATH_REGEX" "$STAGED_DIFF" "-n"
    EXIT_CODE=1
    HAS_TOPOLOGY=1
fi

if [ "$HAS_TOPOLOGY" -eq 0 ]; then
    echo -e "  ${GREEN}✅ 拓扑与环境解耦检查通过。${NC}"
fi

# 阶段四：影子环境变量审计
echo -e "\n${BLUE}[Phase 3/4] 📋 审计环境变量一致性...${NC}"
if [ -f ".env" ] && [ -f ".env.example" ]; then
    MISSING_KEYS=""
    # 提取本地 .env 中的有效键名（排除注释和空行）
    ENV_KEYS=$(grep -v '^#' .env | grep '=' | cut -d= -f1 | tr -d ' ')

    for key in $ENV_KEYS; do
        if ! grep -q "^$key=" .env.example; then
            MISSING_KEYS="$MISSING_KEYS $key"
        fi
    done

    if [ ! -z "$MISSING_KEYS" ]; then
        echo -e "${RED}🚨 [BLOCKER] 发现影子环境变量! 以下变量存在于 .env 但未在 .env.example 中声明:${NC}"
        echo -e "${YELLOW}$MISSING_KEYS${NC}"
        echo -e "${BLUE}💡 修复对策: 请将这些变量加入 .env.example 并将值设为空占位符。${NC}"
        EXIT_CODE=1
    else
        echo -e "  ${GREEN}✅ 环境示例配置完全对齐。${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠️  跳过: 未在根目录下同时发现 .env 与 .env.example 文件。${NC}"
fi

# 阶段五：研发残留代码自检
echo -e "\n${BLUE}[Phase 4/4] 🧹 检查研发调试语句残留...${NC}"
DEBUG_KEYWORDS="(console\.log|debugger|print\(|throw new Error\(['\"]not implemented)"

HAS_DEBUG=$(safe_grep_count "^\+.*$DEBUG_KEYWORDS" "$STAGED_DIFF" "")
if [ "$HAS_DEBUG" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  [WARNING] 代码中包含临时调试语句或未实现占位符:${NC}"
    safe_grep "^\+.*$DEBUG_KEYWORDS" "$STAGED_DIFF" "-n"
else
    echo -e "  ${GREEN}✅ 未发现显式调试残留。${NC}"
fi

# 总结审计状态
echo -e "\n${BLUE}====================================================${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}🎉 L1 物理层审计圆满通过! 项目处于就绪状态。${NC}"
else
    echo -e "${RED}❌ L1 审计不通过! 存在高危拦截项，流水线已强行终止。${NC}"
fi
echo -e "${BLUE}====================================================${NC}"

exit $EXIT_CODE
