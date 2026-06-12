#!/usr/bin/env bash
# ==============================================================================
# Script Name: audit-engine.sh
# Description: 自动化物理层脱敏与工程完整性自检引擎 (L1 屏障)
# Lifecycle:   Git Pre-commit Hook / CI Core Runner
# Version:     3.3.0
# Changes:
#   v3.3.0 - 新增 Phase 0 全仓扫描：对所有 git ls-files 中的文本文件执行凭证正则
#          - 自动跳过二进制文件(.png/.jpg/.svg/.pdf/.exe/.zip 等)
#          - 修复 safe_grep 空 flags 参数导致 grep 崩溃("Unmatched (")的 bug
#   v3.2.0 - 自清洁修复
#   v3.1.0 - 跨平台路径兼容
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
MAX_LINE_LENGTH=500

safe_grep() {
    local regex="$1"
    local input="$2"
    local flags="${3:-}"
    if [ -z "$input" ]; then
        return 0
    fi
    # 逐行过滤：跳过超长行，防止 ReDoS
    local filtered
    filtered=$(echo "$input" | while IFS= read -r line; do
        if [ ${#line} -le "$MAX_LINE_LENGTH" ]; then
            echo "$line"
        fi
    done)
    if [ -z "$filtered" ]; then
        return 0
    fi
    # 只有在有 flags 时才传递，避免空参数导致 grep 崩溃
    if [ -n "$flags" ]; then
        echo "$filtered" | grep -E $flags "$regex" || true
    else
        echo "$filtered" | grep -E -- "$regex" || true
    fi
}

safe_grep_count() {
    local regex="$1"
    local input="$2"
    local flags="${3:-}"
    safe_grep "$regex" "$input" "$flags" | wc -l
}

# 文本文件判断：跳过已知二进制扩展名
is_text_file() {
    local path="$1"
    local ext="${path##*.}"
    # 小写化扩展名
    ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    case "$ext" in
        png|jpg|jpeg|gif|ico|bmp|webp|tiff|tif)
            return 1 ;;
        pdf|doc|docx|xls|xlsx|ppt|pptx)
            return 1 ;;
        zip|tar|gz|bz2|xz|7z|rar|zst)
            return 1 ;;
        exe|dll|so|dylib|bin|obj|lib|a|o)
            return 1 ;;
        wav|mp3|mp4|avi|mov|mkv|flac|ogg)
            return 1 ;;
        ttf|otf|woff|woff2|eot)
            return 1 ;;
        class|pyc|pyo|pyd)
            return 1 ;;
        # SVG 是文本文件，不移出
        *)
            return 0 ;;
    esac
}

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}🚀 开源安全与完整性流水线: 正在执行物理层前置审计...${NC}"
echo -e "${BLUE}====================================================${NC}"

EXIT_CODE=0

# ==================== 正则矩阵定义 ====================
SECRETS_REGEX="(sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}|AIzaSy[a-zA-Z0-9_-]{33}|amzn\.mws\.[a-z0-9-]{36}|(password|passwd|secret|api_key)\s*=\s*['\"][^'\"]+['\"])"
# 简化版内网 IP 正则：去掉嵌套组和边界断言，防止 Git Bash grep 崩溃
INTERNAL_IP_REGEX="(192\.168\.[0-9]{1,3}\.[0-9]{1,3}|10\.([0-9]{1,3}\.){2}[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3})"
if [ "$PLATFORM" = "windows_gitbash" ]; then
    ABSOLUTE_PATH_REGEX="(\/[a-zA-Z]\/[a-zA-Z0-9_-]+\/|[a-zA-Z]:\\\\(Users|home)\\[a-zA-Z0-9_-]+\\)"
else
    ABSOLUTE_PATH_REGEX="(\/Users\/[a-zA-Z0-9_-]+\/|[a-zA-Z]:\\\\Users\\\\[a-zA-Z0-9_-]+\\\\)"
fi
DEBUG_KEYWORDS="(console\.log|debugger|print\(|throw new Error\(['\"]not implemented)"

# ==================== Phase 0: 全仓扫描（逐文件） ====================
echo -e "\n${BLUE}[Phase 0/5] 📂 全仓库文本文件凭证扫描（逐文件）...${NC}"

HIST_BLOCKER=0
HIST_MATCHES=""

if git rev-parse --git-dir > /dev/null 2>&1; then
    while IFS= read -r filepath; do
        if ! is_text_file "$filepath" || [ ! -f "$filepath" ]; then
            continue
        fi
        file_content=$(cat "$filepath" 2>/dev/null || true)
        [ -z "$file_content" ] && continue

        # 逐文件安全扫描（避免大字符串管道传递导致 grep 崩溃）
        file_secrets=$(echo "$file_content" | grep -E -i -- "$SECRETS_REGEX" 2>/dev/null || true)
        if [ -n "$file_secrets" ]; then
            echo -e "  ${RED}🔑 凭证: $filepath${NC}"
            echo "$file_secrets" | while IFS= read -r line; do echo "    $line"; done
            HIST_BLOCKER=1
        fi

        file_paths=$(echo "$file_content" | grep -E -- "$ABSOLUTE_PATH_REGEX" 2>/dev/null || true)
        if [ -n "$file_paths" ]; then
            echo -e "  ${RED}📁 路径: $filepath${NC}"
            echo "$file_paths" | while IFS= read -r line; do echo "    $line"; done
            HIST_BLOCKER=1
        fi

        file_ips=$(echo "$file_content" | grep -E -- "$INTERNAL_IP_REGEX" 2>/dev/null || true)
        if [ -n "$file_ips" ]; then
            echo -e "  ${YELLOW}🌐 内网IP: $filepath${NC}"
            echo "$file_ips" | while IFS= read -r line; do echo "    $line"; done
        fi
    done < <(git ls-files 2>/dev/null || true)
fi
if [ "$HIST_BLOCKER" -eq 0 ]; then
    echo -e "  ${GREEN}✅ 全仓库文本文件凭证扫描安全。${NC}"
fi
EXIT_CODE=$((EXIT_CODE + HIST_BLOCKER))

# ==================== Phase 1: 暂存区凭证扫描 ====================
echo -e "\n${BLUE}[Phase 1/5] 🔐 扫描暂存区变更 (凭证&签名)...${NC}"

STAGED_DIFF=$(git diff --cached 2>/dev/null || echo "")
if [ -z "$STAGED_DIFF" ]; then
    echo -e "  ${YELLOW}⚠️  暂存区无变更，跳过。${NC}"
else
    HAS_SECRET=$(safe_grep_count "$SECRETS_REGEX" "$STAGED_DIFF" "-i")
    if [ "$HAS_SECRET" -gt 0 ]; then
        echo -e "${RED}🚨 [BLOCKER] 检测到疑似硬编码凭证或敏感赋值!${NC}"
        safe_grep "$SECRETS_REGEX" "$STAGED_DIFF" "-n -i"
        EXIT_CODE=1
    else
        echo -e "  ${GREEN}✅ 凭证特征扫描安全。${NC}"
    fi
fi

# ==================== Phase 2: 网络拓扑&路径脱敏 ====================
echo -e "\n${BLUE}[Phase 2/5] 🌐 扫描基础设施拓扑残留...${NC}"

HAS_TOPOLOGY=0
if [ -n "$STAGED_DIFF" ]; then
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
fi

if [ "$HAS_TOPOLOGY" -eq 0 ]; then
    echo -e "  ${GREEN}✅ 拓扑与环境解耦检查通过。${NC}"
fi

# ==================== Phase 3: 影子环境变量 ====================
echo -e "\n${BLUE}[Phase 3/5] 📋 审计环境变量一致性...${NC}"
if [ -f ".env" ] && [ -f ".env.example" ]; then
    MISSING_KEYS=""
    ENV_KEYS=$(grep -v '^#' .env | grep '=' | cut -d= -f1 | tr -d ' ')
    for key in $ENV_KEYS; do
        if ! grep -q "^$key=" .env.example; then
            MISSING_KEYS="$MISSING_KEYS $key"
        fi
    done
    if [ -n "$MISSING_KEYS" ]; then
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

# ==================== Phase 4: 调试语句残留 ====================
echo -e "\n${BLUE}[Phase 4/5] 🧹 检查研发调试语句残留...${NC}"
if [ -n "$STAGED_DIFF" ]; then
    HAS_DEBUG=$(safe_grep_count "^\+.*$DEBUG_KEYWORDS" "$STAGED_DIFF" "")
    if [ "$HAS_DEBUG" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  [WARNING] 代码中包含临时调试语句或未实现占位符:${NC}"
        safe_grep "^\+.*$DEBUG_KEYWORDS" "$STAGED_DIFF" "-n"
    else
        echo -e "  ${GREEN}✅ 未发现显式调试残留。${NC}"
    fi
else
    echo -e "  ${GREEN}✅ 无暂存区变更，跳过调试语句检查。${NC}"
fi

# ==================== 总结 ====================
echo -e "\n${BLUE}====================================================${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}🎉 L1 物理层审计圆满通过! 项目处于就绪状态。${NC}"
else
    echo -e "${RED}❌ L1 审计不通过! 存在高危拦截项，流水线已强行终止。${NC}"
fi
echo -e "${BLUE}====================================================${NC}"

exit $EXIT_CODE
