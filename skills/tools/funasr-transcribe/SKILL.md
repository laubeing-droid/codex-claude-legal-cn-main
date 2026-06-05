---
name: funasr-transcribe
license: MIT
author: laubeing-droid
description: 本地FunASR语音转文字服务，将音视频文件转录为带时间戳的Markdown。支持说话人分离、ONNX加速、视频关键帧提取和AI自动总结。本技能应在用户需要语音转文字、会议记录、视频字幕或播客转录时使用。
---

# FunASR 语音转文字

## 一、功能概述

本地运行的语音识别服务，将音视频转为结构化Markdown文档。

(一) 支持特性
1. 多格式——mp4/mov/mp3/wav/m4a/flac等
2. 时间戳——自动生成带时间轴的发言人标注
3. 说话人分离——diarization默认启用，可关闭做单人快速模式
4. ONNX加速——`paraformer-onnx`路径，VAD分段+标点恢复
5. 视频截图——自动检测PPT切换帧并插入对应位置
6. AI总结——转录后附带提示词，可一步完成结构化摘要

(二) 模型清单
- ASR主模型(Paraformer)——867MB
- SenseVoice-Small——ONNX实验性单人路径，按需下载
- VAD——4MB / 标点——283MB / 说话人分离——28MB

## 二、Agent默认工作流

转录 + 自动总结，一步完成：

(一) 环境准备
首次运行检测并生成 `assets/skill-env.json`：
```bash
python3 scripts/init_env.py
```
失败时运行安装：`python3 scripts/setup.py`

(二) 启动服务
检查健康：`curl -s http://127.0.0.1:8765/health`
未运行时后台启动：`python3 scripts/server.py --idle-timeout 600 &`
等待 `/health` 返回200。

(三) 执行转录
```bash
curl -s -X POST http://127.0.0.1:8765/transcribe \
 -H "Content-Type: application/json" \
 -d '{"file_path": "/path/to/audio.aac"}'
```

关键参数：
- `diarize`——默认true，单人可设false
- `fast: true`——关闭说话人分离
- `model: "paraformer-onnx"`——ONNX加速
- `extract_slides`——视频自动提取关键帧

响应包含 `output_path`、`text`、`summary_prompt` 等字段。

(四) 生成并注入总结
1. 根据 `summary_prompt` 生成结构化JSON（全文总结≥400字、发言人总结≥180字/人、6-10条重点、5-8个关键词）
2. 写JSON到临时文件后注入：
```bash
python3 scripts/summary.py inject "<output_path>" /tmp/summary_xxx.json
```
3. 验证注入：`python3 scripts/summary.py verify "<output_path>"`，失败则重试

## 三、命令行使用

(一) 转录
```bash
# 单文件
python3 scripts/transcribe.py /path/to/audio.mp3

# 指定输出 + 说话人分离
python3 scripts/transcribe.py /path/to/meeting.m4a -o transcript.md --diarize

# ONNX加速 + 单人路径
python3 scripts/transcribe.py /path/to/course.m4a --model paraformer-onnx --no-diarize

# 批量转录目录
python3 scripts/transcribe.py /path/to/media_folder/

# 视频关键帧提取
python3 scripts/transcribe.py /path/to/video.mp4 --slides
```

(二) 自动化脚本（推荐）
```bash
python3 scripts/auto_transcribe.py /path/to/audio.aac
python3 scripts/auto_transcribe.py /path/to/course.m4a --fast
```

## 四、API端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/transcribe` | POST | 转录音视频 |
| `/batch_transcribe` | POST | 批量转录 |
| `/summary` | POST | 生成总结提示词 |
| `/inject_summary` | POST | 注入Markdown文件 |
| `/verify_summary` | POST | 验证摘要存在 |

Swagger UI：`http://127.0.0.1:8765/docs`

## 五、转录优先级

**FunASR优先 → Whisper CLI fallback**

仅在FunASR不可用时（服务报错500、funasr-onnx安装失败）使用Whisper作为后备：
```bash
ffmpeg -i "/path/to/video.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 -y "/tmp/audio.wav"
whisper "/tmp/audio.wav" --model tiny --language Chinese --output_format all
```

## 六、故障排除

| 问题 | 解决 |
|------|------|
| 端口占用 | `lsof -ti:8765 \| xargs kill -9` |
| cv2导入失败 | `python3 -m pip install opencv-python-headless --break-system-packages` |
| 首次加载慢 | 等待模型下载(约1-2GB)，后续使用已缓存 |

## 七、依赖与环境

系统依赖：Python 3.8+、curl、ffmpeg

Python包：`funasr`、`funasr-onnx`、`scenedetect[opencv]`、`imagehash`

一键安装：`python3 scripts/setup.py`

验证：`python3 scripts/setup.py --verify`
