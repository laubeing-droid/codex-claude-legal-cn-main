#!/bin/bash

# Skill & Command Manager - Remove Script
# 卸载指定的 skill 或 command

ITEM_NAME="$1"
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

# 检查参数
if [ -z "$ITEM_NAME" ]; then
    echo "❌ 错误: 请提供要卸载的 skill 或 command 名称"
    echo ""
    echo "使用方法: $0 <name>"
    echo ""
    echo "示例:"
    echo "  卸载 skill:    $0 pdf-tool"
    echo "  卸载 command:  $0 deepresearch"
    exit 1
fi

# 查找目标（先找 skill，再找 command）
SKILL_PATH="$SKILLS_DIR/$ITEM_NAME"
COMMAND_PATH="$COMMANDS_DIR/$ITEM_NAME.md"

TARGET_PATH=""
TARGET_TYPE=""

if [ -e "$SKILL_PATH" ]; then
    TARGET_PATH="$SKILL_PATH"
    TARGET_TYPE="skill"
elif [ -e "$COMMAND_PATH" ]; then
    TARGET_PATH="$COMMAND_PATH"
    TARGET_TYPE="command"
else
    echo "❌ 错误: 未找到 '$ITEM_NAME'"
    echo "   请确认名称是否正确"
    exit 1
fi

# 检查是否是 skill-manager 自身
if [ "$ITEM_NAME" = "skill-manager" ]; then
    echo "❌ 错误: 不能卸载 skill-manager 自身"
    exit 1
fi

# 确认删除
echo "⚠ 即将卸载: $ITEM_NAME"
if [ "$TARGET_TYPE" = "skill" ]; then
    if [ -L "$TARGET_PATH" ]; then
        echo "   类型: 符号链接 (skill)"
    elif [ -d "$TARGET_PATH/.git" ]; then
        echo "   类型: Git 克隆 (skill)"
    else
        echo "   类型: 本地目录 (skill)"
    fi
else
    if [ -L "$TARGET_PATH" ]; then
        echo "   类型: 符号链接 (command)"
    else
        echo "   类型: 本地文件 (command)"
    fi
fi

echo ""
read -p "确认删除? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# 执行删除
if [ -L "$TARGET_PATH" ]; then
    rm "$TARGET_PATH"
    echo "✓ 已删除符号链接"
elif [ -d "$TARGET_PATH" ]; then
    rm -rf "$TARGET_PATH"
    echo "✓ 已删除目录"
elif [ -f "$TARGET_PATH" ]; then
    rm "$TARGET_PATH"
    echo "✓ 已删除文件"
fi

echo "✓ $TARGET_TYPE '$ITEM_NAME' 已卸载"
