---
name: skill-manager
license: MIT
author: laubeing-droid
description: 跨平台Skills安装与管理工具，兼容Claude Code/Codex/OpenClaw。支持本地符号链接安装、GitHub仓库克隆、安全检查、版本追踪与自动更新检测。本技能应在用户需要安装、卸载、列示或更新Agent技能时使用。
---

# Skill Manager

## 一、功能概述

统一管理多个Agent平台的Skills与Commands，覆盖安装、卸载、列表、更新检查全流程。

(一) 支持平台
1. Claude Code——`.claude/skills/`
2. Codex——`.codex/skills/`
3. OpenClaw——`.openclaw/skills/`

(二) 安装行为
1. 本地路径——创建符号链接，保持与源实时同步
2. GitHub仓库——浅克隆后删除 `.git`，转为静态副本
3. 本地集合目录——批量遍历子项分别安装
4. 冲突处理——已存在时先备份到 `.backup`

(三) Skill判定规则
一个目录被识别为有效Skill需包含：
- `SKILL.md`（标准格式）或 `skill.md`（变体）
- 或 `.codex`/`.claude`/`.openclaw` 子目录

Command判定：`.md` 扩展名文件。

## 二、命令参考

(一) 安装
```bash
scripts/install.sh [--target <dir>] <source>
```

来源格式：
- 本地路径：`~/dev/my-skills/pdf-tool`
- 本地批量：`~/dev/my-skills/`
- GitHub仓库：`https://github.com/owner/repo`
- 简写：`owner/repo`
- 子目录：`owner/repo/branch/path/to/skills`

(二) 列表与卸载
```bash
scripts/list.sh # 列出已安装项，标注类型
scripts/remove.sh <name> # 卸载指定Skill或Command
```

(三) 更新检查
```bash
scripts/check.sh # 检测所有远程安装的更新
scripts/update.sh [name] # 更新全部或指定Skill
```

检测逻辑：
- 有版本号→直接比较本地与远端版本
- 无版本号→对比远程最新Commit与安装时间
- 子目录安装→仅检查子目录路径下的变更

## 三、安全检查

从GitHub安装时自动触发安全审计（本地安装跳过）。

(一) 检测维度
1. 危险代码——命令执行、敏感文件访问、数据外泄、混淆
2. Skill特有风险——安装钩子、检索服务配置
3. 提示词安全——注入攻击、数据收集指令、欺骗性描述
4. 硬编码凭证——API Key、Token、密码

(二) 风险等级
- CRITICAL——极高风险，强烈不建议使用
- HIGH——高风险，需审计后决策
- MEDIUM——中等风险，使用前确认
- LOW——低风险，建议定期复查
- NONE——未检出风险

存在Python 3环境时自动执行；无Python时静默跳过。

## 四、注册表记录

安装和更新操作写入 `assets/skill-registry.json`，字段包括：
- `name`、`source`、`install_type`、`remote_url`
- `installed_at`、`last_updated`、`current_version`、`latest_version`
- `install_commit`、`remote_subpath`、`description`

查看记录：`python3 scripts/record.py list`

## 五、目标目录策略

脚本从调用位置向上查找Agent配置目录：
1. 位于 `.codex`/`.claude`/`.openclaw` 结构内时自动对齐
2. 全局配置文件目录（如 `~/.claude`）调用时通过git发现项目本地目录
3. 可通过 `--target` 参数或 `SKILL_MANAGER_TARGET_DIR` 环境变量强制指定
