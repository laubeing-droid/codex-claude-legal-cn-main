---
license: MIT
author: laubeing-droid
name: sync-external
description: 跨项目文件同步 — 在当前项目创建 @include 引用指向外部源文件
---

# 跨项目引用同步

**版本**: v3.0
**更新日期**: 2026-06-05

## 一、功能定位

在当前项目的 `.claude/commands/` 或 `.claude/rules/` 下生成仅含 `@include` 指令的引用文件，指向另一项目的同名文件，实现单点维护、多处生效。

## 二、执行步骤

### （一）接收源路径

两种告知方式：

1. 直接在命令后附上完整路径：
   ```
   /sync-external [源项目]/.claude/commands/某命令.md
   ```

2. 分项提供：
   ```
   /sync-external
   源项目：[路径]
   文件类型：command / rule
   文件名：某文件.md
   ```

### （二）核验源文件

用 `test -f` 确认文件存在。不存在则报错终止。

### （三）确定目标位置

源在 commands 目录 → 目标落当前项目的 commands；源在 rules → 同理落入 rules。

### （四）写入引用

目标文件**仅此一行**，不加 YAML 头或注释：

```markdown
@include [源文件绝对路径]
```

### （五）反馈结果

```
✅ 引用文件已创建

目标：.claude/commands/某文件.md
源头：[源完整路径]
```

## 三、核心约束

- 只建引用，不拷内容
- 必须用绝对路径
- 目标文件没有任何附加文字
- 源文件改动后所有引用方自动同步
