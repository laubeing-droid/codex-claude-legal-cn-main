#!/usr/bin/env bash
# agent-email operations — mail-cli 封装函数库
#
# 使用方式：
#   source skills/agent-email/scripts/mail-ops.sh
#   claw_send --to "bot@claw.163.com" --subject "任务" --body "内容"
#   claw_list --fid 1 --limit 10

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载 .env 配置
if [[ -f "${SCRIPT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${SCRIPT_DIR}/.env"
  set +a
fi

# 默认值
AGENT_EMAIL="${AGENT_EMAIL:-}"
DISPLAY_NAME="${DISPLAY_NAME:-}"
INBOX_FID="${INBOX_FID:-1}"
SENT_FID="${SENT_FID:-3}"

# 默认使用 npx 调用 mail-cli（无需全局安装）
_CLI() {
  npx --yes "@clawemail/mail-cli@latest" "$@"
}

# 列出文件夹
claw_folders() {
  _CLI folder list "$@"
}

# 列出邮件
# 用法: claw_list --fid <id> [--limit N] [--profile P]
claw_list() {
  _CLI mail list "$@"
}

# 读取邮件正文
claw_body() {
  local mail_id="$1"; shift
  _CLI read body "$mail_id" "$@"
}

# 读取邮件结构（含附件列表）
claw_structure() {
  local mail_id="$1"; shift
  _CLI read structure "$mail_id" "$@"
}

# 搜索邮件
# 用法: claw_search --fid <id> "关键词"
claw_search() {
  _CLI mail search "$@"
}

# 发送邮件
# 用法: claw_send --to <addr> --subject <subj> --body <text>
claw_send() {
  local to=""
  local subject=""
  local body=""
  local html=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --to)      to="$2"; shift 2 ;;
      --subject) subject="$2"; shift 2 ;;
      --body)    body="$2"; shift 2 ;;
      --html)    html="--html"; shift ;;
      *)         shift ;;
    esac
  done

  if [[ -z "$to" || -z "$subject" ]]; then
    echo "错误: 需要指定 --to 和 --subject" >&2
    return 1
  fi

  local args=(compose send)
  if [[ -n "$AGENT_EMAIL" && -n "$DISPLAY_NAME" ]]; then
    args+=(--from "\"${DISPLAY_NAME}\" <${AGENT_EMAIL}>")
  fi

  args+=(--to "$to" --subject "$subject")
  if [[ -n "$body" ]]; then
    args+=(--body "$body")
  fi
  if [[ -n "$html" ]]; then
    args+=(--html)
  fi

  _CLI "${args[@]}"
}

# 下载附件
# 用法: claw_download <mail-id>
claw_download() {
  local mail_id="$1"; shift
  _CLI read attachment "$mail_id" --download "$@"
}

# 查看所有邮箱
claw_mailboxes() {
  _CLI clawemail list "$@"
}

# 创建子邮箱
claw_create() {
  _CLI clawemail create "$@"
}

# ── 首次配置 ──────────────────────────────────────────────

# 从认证 URL 配置邮箱（一键初始化）
# 用法: claw_init "t1/xxxxxxxxxx"
claw_init() {
  local auth_url="$1"

  # 1. 解析认证 URL 获取凭证
  echo "→ 解析认证 URL..."
  local creds
  creds=$(curl -sL "https://u.163.com/${auth_url}")
  if [[ -z "$creds" ]]; then
    echo "错误: 认证 URL 无效或已过期（有效期 30 分钟）" >&2
    return 1
  fi

  # 解析：第一行 name:account-id:，第二行 __apikey__:workspace:ck_live_xxx
  local name account_id apikey
  name=$(echo "$creds" | head -1 | cut -d: -f1)
  account_id=$(echo "$creds" | head -1 | cut -d: -f2)
  apikey=$(echo "$creds" | grep "__apikey__" | cut -d: -f3)

  if [[ -z "$apikey" ]]; then
    echo "错误: 未能从认证 URL 获取 API Key" >&2
    return 1
  fi

  echo "  邮箱: ${name}@claw.163.com"

  # 2. 存储 API Key
  echo "→ 存储 API Key..."
  _CLI auth apikey set "$apikey"

  # 3. 创建默认 Profile
  echo "→ 配置 Profile..."
  _CLI auth login --user "${name}@claw.163.com" --auth-method password --password "$apikey"

  # 4. 验证
  echo "→ 验证连通..."
  _CLI folder list

  echo ""
  echo "✅ 配置完成！邮箱: ${name}@claw.163.com"

  # 5. 写入 .env 备份配置
  local display_name="${2:-${name}}"
  printf -v display_name_q '%q' "$display_name"
  cat > "${SCRIPT_DIR}/.env" <<EOF
# Agent Email 环境配置
AGENT_EMAIL=${name}@claw.163.com
DISPLAY_NAME=${display_name_q}
CLAW_PREFIX=${name}
CLAW_PROFILE=default
INBOX_FID=1
SENT_FID=3
EOF
  echo "  配置已写入 ${SCRIPT_DIR}/.env"
  echo "  发送邮件: claw_send --to 'xxx@example.com' --subject '主题' --body '内容'"
  echo "  查看收件箱: claw_list --fid 1"
}
