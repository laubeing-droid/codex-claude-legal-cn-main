---
name: wechat-article-fetch
license: MIT
author: laubeing-droid
description: 微信公众号文章抓取工具。使用Playwright无头浏览器后台获取文章标题与正文，支持自动保存为Markdown、图片下载过滤、法律内容链式格式化。本技能应在用户需要抓取微信公众号文章内容时使用。
---

# 微信文章抓取

## 一、功能特性

(一) 核心能力
1. 无头模式运行——默认后台抓取，不弹浏览器窗口
2. 智能回退——无头模式失败自动切有头模式重试
3. 动态加载支持——等待页面完全渲染，处理懒加载内容
4. Markdown导出——提取标题与正文，保存为规范Markdown文件
5. 图片处理——自动下载文章内图片，过滤装饰性小图（<15KB）
6. 自动重试——失败时重试最多3次

(二) 抓取后法律格式化协议
完成抓取后判定内容属性，满足以下条件时自动调用 `legal-text-format` 技能：
- 内容满足法律判定（标题含案例/裁判/法规等关键词，或正文含案号/法院名称/法条引用）
- 项目中存在 `skills/legal-text-format/SKILL.md`

格式化后原始内容留存在本技能 `archive/`；格式化结果保存在 `legal-text-format` 的 `archive/`。

## 二、使用方式

(一) 命令行调用
```bash
# 控制台输出
node scripts/fetch.js "https://mp.weixin.qq.com/s/xxxxx"

# 保存为指定文件
node scripts/fetch.js "https://mp.weixin.qq.com/s/xxxxx" "./articles/output.md"

# 保存到目录（自动用标题命名）
node scripts/fetch.js "https://mp.weixin.qq.com/s/xxxxx" "./articles/"
```

(二) Markdown输出格式
```markdown
# 文章标题
> 原文链接: https://mp.weixin.qq.com/s/xxxxx
> 抓取时间: 2026-01-21 20:30:00
---
文章正文内容...
```

含图片时输出结构：
```
输出目录/
├── 文章标题.md
└── 文章标题_assets/
 ├── image_xxx_0.jpg
 └── image_xxx_1.jpg
```

## 三、技术实现

(一) 抓取流程
1. 检测并安装Playwright Chromium
2. 启动headless浏览器，配置反检测参数
3. 导航至目标页，等待网络空闲
4. 滚动触发懒加载
5. 提取 `#js_content` 区域内容
6. 清理HTML标签保留段落结构
7. 下载图片并生成本地资源文件夹

(二) 错误处理
1. 自动重试——每次失败等待3秒，最多3次
2. 无头失败回退——自动切换有头模式
3. 异常页面识别——检测"参数错误"等异常响应

(三) 依赖要求
1. Playwright——`npx playwright install chromium`
2. Node.js >= 14.0.0

## 四、跨平台兼容

(一) Windows——自动使用 `cmd.exe` 执行 npx 命令
(二) macOS/Linux——直接调用 npx
(三) 路径处理——自动规范化分隔符，过滤非法文件名字符

## 五、注意事项

1. 仅用于个人学习研究，遵守网站服务条款
2. 控制请求频率避免触发限流
3. 抓取内容版权归原作者所有
