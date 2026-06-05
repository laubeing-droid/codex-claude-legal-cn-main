#!/bin/bash

# Skill & Command Manager - List Script
# 列出已安装的 skills 和 commands

ORIGINAL_PWD="$PWD"
# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGER_DIR="$(dirname "$SCRIPT_DIR")"
TARGET_HELPER="$SCRIPT_DIR/target.sh"

if [ -f "$TARGET_HELPER" ]; then
    # shellcheck source=target.sh
    source "$TARGET_HELPER"
else
    echo "❌ 错误: 找不到目标目录识别模块: $TARGET_HELPER"
    exit 1
fi

SCRIPT_AGENT_DIR="$(find_agent_config_dir "$MANAGER_DIR" "$PWD/.claude")"
AGENT_DIR="$(find_agent_config_dir "$ORIGINAL_PWD" "$SCRIPT_AGENT_DIR")"
SKILLS_DIR="$AGENT_DIR/skills"
COMMANDS_DIR="$AGENT_DIR/commands"

# 列出 skills
list_skills() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        return
    fi

    echo "📋 已安装的 Skills"
    echo ""

    count=0
    for item in "$dir"/*; do
        if [ -e "$item" ] && [ "$(basename "$item")" != "skill-manager" ]; then
            name=$(basename "$item")

            if [ -L "$item" ]; then
                # 符号链接
                target=$(readlink "$item")
                echo "🔗 $name"
                echo "   类型: 符号链接"
                echo "   指向: $target"
            elif [ -d "$item" ]; then
                # 目录
                if [ -d "$item/.git" ]; then
                    # Git 仓库
                    remote=$(cd "$item" && git remote get-url origin 2>/dev/null || echo "未知")
                    branch=$(cd "$item" && git branch --show-current 2>/dev/null || echo "未知")
                    echo "📦 $name"
                    echo "   类型: Git 克隆"
                    echo "   仓库: $remote"
                    echo "   分支: $branch"
                else
                    # 普通目录
                    echo "📁 $name"
                    echo "   类型: 本地目录"
                fi
            fi
            echo ""
            ((count++))
        fi
    done

    if [ "$count" -eq 0 ]; then
        echo "暂无已安装的 skills"
    else
        echo "总计: $count 个 skills"
    fi
}

# 列出 commands
list_commands() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        return
    fi

    echo ""
    echo "📋 已安装的 Commands"
    echo ""

    count=0
    for item in "$dir"/*.md; do
        if [ -e "$item" ]; then
            name=$(basename "$item" .md)

            if [ -L "$item" ]; then
                # 符号链接
                target=$(readlink "$item")
                echo "🔗 $name"
                echo "   类型: 符号链接"
                echo "   指向: $target"
            elif [ -f "$item" ]; then
                # 普通文件
                echo "📄 $name"
                echo "   类型: 本地文件"
            fi
            echo ""
            ((count++))
        fi
    done

    if [ "$count" -eq 0 ]; then
        echo "暂无已安装的 commands"
    else
        echo "总计: $count 个 commands"
    fi
}

# 执行列表
list_skills "$SKILLS_DIR"
list_commands "$COMMANDS_DIR"
