#!/bin/bash

# Skill Manager - Auto Update Check
# 检查超过阈值的远程 Skill 更新状态
# 仅在发现更新时输出，否则静默退出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 &> /dev/null; then
    exit 0
fi

RECORD_SCRIPT="$SCRIPT_DIR/record.py"
if [ ! -f "$RECORD_SCRIPT" ]; then
    exit 0
fi

THRESHOLD="${SKILL_MANAGER_CHECK_THRESHOLD:-7}"

python3 "$RECORD_SCRIPT" auto-check --threshold "$THRESHOLD" 2>/dev/null
