---
name: scheduler
description: "案件流程调度与期限管理命令"
usage: "/scheduler [案件ID] --list | --status | --advance"
---

# /scheduler —— 案件流程调度与期限管理

## 角色定位

Scheduler 是案件流程调度的命令脚本，负责期限管理和案件阶段推进。非独立 Agent，不参与法律推理。

## 功能

1. **期限监控**：诉讼时效、保全到期、举证期限、上诉期限等关键日期
2. **阶段推进**：收案 → 立案 → 保全 → 举证 → 庭审 → 判决 → 执行
3. **任务提醒**：基于时间线自动生成待办清单

## 用法

```
/scheduler <案件ID> --list         列出当前案件所有期限
/scheduler <案件ID> --status       查看案件阶段状态
/scheduler <案件ID> --advance      推进到下一阶段
/scheduler <案件ID> --deadline N   设置第N个期限
```

## 输出

- 格式：结构化 Markdown 日历表
- 内容：案件各阶段起止时间 + 当前状态 + 即将到期提醒
