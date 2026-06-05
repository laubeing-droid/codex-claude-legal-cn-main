---
name: mineru-ocr
license: MIT
author: laubeing-droid
description: 文档转Markdown工具，基于MinerU云端API。默认使用免登录轻量模式开箱即用；配置Token后自动切换标准API。本技能应在用户需要PDF/图片/Office文档转Markdown、表格识别、公式提取或网页内容抓取时使用。
---

# MinerU 文档转换

## 一、模式与能力边界

(一) 双模式说明
1. 轻量模式——无需登录注册，直接调用官方免登录接口
2. 标准模式——需配置API Token，走完整v4 API

(二) 能力对比

| 维度 | 轻量模式 | 标准API |
|------|----------|---------|
| 本地文件（PDF/Docx/Pptx/图片） | 支持 | 支持 |
| 远端文档URL | 支持 | 支持 |
| 网页URL | 不支持 | 支持 |
| 单文件上限 | 10MB / 20页 | 200MB / 600页 |
| 表格识别 | 不支持 | 支持 |
| 公式识别 | 不支持 | 支持 |
| 输出格式 | Markdown | Zip包 + Markdown/JSON |

(三) Token配置方式
1. 注册MinerU账号后在 [API管理页](https://mineru.net/apiManage/token) 创建Token
2. 优先级：skill `.env` > 环境变量 `MINERU_API_TOKEN` > `MINERU_TOKEN` > 官方CLI配置

## 二、使用方式

(一) 命令格式
```bash
/usr/bin/osascript -l JavaScript .claude/skills/mineru-ocr/scripts/convert.js "输入路径或URL"
```

输入类型自动识别：
- 本地文件绝对路径
- 远程文档URL（PDF/图片等）
- 网页URL（需标准模式）

(二) Token自检
```bash
/usr/bin/osascript -l JavaScript .claude/skills/mineru-ocr/scripts/convert.js checktoken
```
反馈当前模式、Token状态或失效提示。

## 三、输出与归档

(一) 输出位置
- 本地文件——Markdown保存到源文件同级目录
- 远程URL——保存到当前工作目录

(二) 归档结构
转换结果自动归档到 `archive/日期_时间_文件名/`，包含：
- 转化后的Markdown文件
- 接口原始响应
- 可下载的图片资源清单

## 四、配置参考

编辑 `config/.env`：

| 选项 | 默认 | 说明 |
|------|------|------|
| MINERU_API_TOKEN | 空 | 填写后强制标准API |
| MINERU_ENABLE_OCR | true | OCR开关 |
| MINERU_ENABLE_TABLE | true | 表格识别（标准API） |
| MINERU_ENABLE_FORMULA | false | 公式识别（标准API） |
| MINERU_LANGUAGE_CODE | ch | 语言设置 |
| MINERU_API_BASE | https://mineru.net/api/v4 | API地址 |
| MINERU_MODEL_VERSION | pipeline | 模型版本；法律文档推荐pipeline |
| MINERU_PAGE_RANGES | 空 | 页码范围如 `1-20` |
| MINERU_POLL_MAX | 20 | 异步转换轮询上限 |
| MINERU_POLL_SLEEP | 10 | 轮询间隔（秒） |

## 五、法律文档建议

(一) 模型选择
1. 起诉状、证据目录、传票等正式文书优先 `pipeline`
2. 扫描质量差、版面极复杂、表格密集时可切换 `vlm`
3. 只需预览前几页可设 `MINERU_PAGE_RANGES=1-20`

## 六、故障排除

| 问题 | 解决方案 |
|------|----------|
| 轻量接口限频 | 等待后重试，或开通标准模式 |
| 文件超限 | 配置Token使用标准API |
| 网页URL无法解析 | 轻量模式不支持HTML，需标准API |
| 401未授权 | Token过期，重新申请并更新配置 |
| 转换超时 | 增大 `MINERU_POLL_MAX` 或检查文件体积 |
| 配额不足 | 检查账户额度 |
