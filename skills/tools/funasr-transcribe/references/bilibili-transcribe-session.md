# B站视频转录实战笔记（2026-05-10）

## 任务背景

下载 B 站视频 `BV1TfRfBJEZw`（标题：《解读Deepseek V4带来的杠杆机会，顺便聊聊我实践出的Token Efficiency》，作者：小天 fotos）并转录。

## STT 转录优先级（重要）

**正确顺序**：FunASR（主选）→ Whisper CLI（fallback）

> ⚠️ 用户明确纠正：FunASR 是主选，不要在没有先尝试 FunASR 的情况下直接用 Whisper。

## 踩坑记录

### 坑1：服务路径错误（根因）

**现象**：`funasr-onnx` 依赖明明已装，但 `/transcribe` 始终返回 500，错误 "缺少 funasr-onnx 依赖"。

**根因**：服务从 `.claude/skills/funasr-transcribe/` 启动，但 `auto_transcribe.py` 的 import 链加载了 `技能集合/skills/funasr-transcribe/scripts/server.py`（另一份旧版代码），后者路径下的依赖检查逻辑报了错误。

**排查命令**：
```bash
# 检查 funasr 是否可用
python3 -c "import funasr; print(funasr.__file__)"

# 检查 funasr_onnx 是否可用
python3 -c "import funasr_onnx" # 报错 "找不到模块" = 正常，说明没装

# 查看服务进程日志
process_log # 查看 proc_<session_id>
```

### 坑2：pip 安装 funasr-onnx 超时

`pip install funasr-onnx --break-system-packages` 在 300s 内无法完成（需要下载大模型文件）。

### 坑3：直接用 Whisper 而非先尝试 FunASR（被用户纠正）

**教训**：FunASR 中文质量更高，应优先尝试 FunASR 服务。只有在 FunASR 服务报错且 funasr-onnx 无法修复时，才用 Whisper CLI 作为 fallback。

## Whisper CLI Fallback（仅在 FunASR 不可用时）

```bash
# Step 1: 提取音频（16kHz 单声道）
ffmpeg -i "/path/to/video.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 -y "/tmp/audio.wav"

# Step 2: Whisper 转录（tiny 模型最快）
/opt/homebrew/bin/whisper "/tmp/audio.wav" \
 --model tiny \
 --language Chinese \
 --output_dir /tmp/transcript \
 --output_format all
```

性能参考：19 分钟音频，tiny 模型约 3-5 分钟跑完（Mac CPU）。

## 关键文件路径

| 文件 | 路径 |
|------|------|
| 视频下载脚本 | `.claude/skills/universal-media-downloader/scripts/download_media.py` |
| FunASR 服务 | `.claude/skills/funasr-transcribe/scripts/server-onnx.py` |
| Whisper CLI | `/opt/homebrew/bin/whisper` |
| 视频输出 | `/private/tmp/bilibili_video/` |
| 音频临时 | `/tmp/audio.wav` |
