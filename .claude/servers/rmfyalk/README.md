<!--
version: 3.0.2
module: -hub
status: active
-->

# 案例库 检索服务

基于人民法院案例库（rmfyalk.court.gov.cn）的 联网检索 封装

- 启动：`pip install -r requirements.txt && python scripts/server.py`
- 端口：localhost:18061
- 鉴权：Cookie Token（F12 → 网络请求 → 复制 Cookie）
- 配置项参考 `.env.example`