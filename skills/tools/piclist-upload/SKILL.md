---
name: piclist-upload
license: MIT
author: laubeing-droid
description: Markdown图片图床上传工具。通过PicList HTTP Server将本地图片引用批量替换为云端URL，上传后默认清理本地文件。本技能应在用户需要上传Markdown文档中的本地图片以实现跨设备访问时使用。
---

# PicList 图片上传

将 Markdown 中的本地图片链接批量替换为图床云端地址，支持单文件和目录批量处理。

## 一、前置条件

(一) 环境要求
1. 已安装并启动 PicList 应用，HTTP Server 默认端口 36677
2. 已在 PicList 中完成图床配置（SMMS/GitHub等）
3. 系统已安装 `curl` 和 `jq` 命令行工具

(二) 初始配置
详见 `references/setup.md` 中的安装与配置指南。

## 二、使用方式

(一) 核心规则
1. 必须通过 `scripts/process.sh` 脚本执行，禁止手动 curl 操作
2. 默认上传成功后自动删除本地图片文件
3. 仅在用户明确要求时使用 `--keep-local` 保留本地副本

(二) 命令格式

处理文件或目录（默认删除本地图片）：
```bash
bash scripts/process.sh --in-place <file.md|directory...>
```

保留本地图片（按需使用）：
```bash
bash scripts/process.sh --in-place --keep-local <file.md|directory...>
```

预览模式（不修改文件、不上传）：
```bash
bash scripts/process.sh --dry-run <file.md|directory...>
```

## 三、响应与统计

(一) 上传响应解析
PicList 返回 JSON 格式，脚本自动提取结果：
```json
{"success":true,"result":["https://example.com/image.png"]}
```

(二) 处理统计
完成后输出汇总：
- Uploaded——成功上传并替换的数量
- Skipped——已是云端URL无需处理的记录
- Failed——上传出错保留原路径的条目

## 四、错误处理

(一) 常见问题
1. Server 未运行——提示启动 PicList 应用，检查端口 36677
2. 文件不存在——跳过并标注警告，继续后续处理
3. 上传失败——保留原始本地路径，标记失败，不影响其他文件
4. 响应解析异常——视为上传失败，不做路径替换

(二) 配置覆盖
可通过环境变量指定非默认服务地址：
```bash
export PICLIST_SERVER=http://127.0.0.1:PORT
```

## 五、支持格式

png, jpg, jpeg, gif, webp, svg, bmp
