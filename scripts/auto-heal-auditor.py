#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: auto-heal-auditor.py
Description: 自愈式代码脱敏与完整性修复编排器 (Reflection Engine)
Depends:    Python 3.8+, requests, 安装: pip install requests

生命周期:
  1. 执行 audit-engine.sh → 获取 Exit Code
  2. Exit Code == 0 → 通过，退出(0)
  3. Exit Code != 0 → 捕获错误日志 + 暂存区源码 → 调用 AI 修复
  4. AI 返回结构化修复方案 → 应用文件修改 + git add
  5. 回到步骤 1，最多迭代 MAX_RETRIES 轮
"""

import os
import sys
import json
import subprocess

# ==================== 废弃警告 ====================
_DEPRECATION_WARNING = """
╔══════════════════════════════════════════════════════════╗
║  ⚠️  DEPRECATION WARNING — 此脚本已废弃                    ║
║                                                          ║
║  auto-heal-auditor.py 是 v2 单层自愈编排器。               ║
║  请使用 v3 matrix-converge-engine.py 替代，它提供：        ║
║    • 四层矩阵收敛（供应链 → 脱敏 → 语义 → TDD）           ║
║    • 震动退耦保护                                          ║
║    • 安全日志脱敏                                          ║
║    • 策略自学习                                            ║
║                                                          ║
║  迁移命令: python3 scripts/matrix-converge-engine.py       ║
╚══════════════════════════════════════════════════════════╝
"""

# 公共 subprocess 参数
_SUBPROCESS_KWARGS = {
    "shell": True,
    "capture_output": True,
    "text": True,
    "encoding": "utf-8",
    "errors": "surrogateescape",
}

# ==================== 配置中心 ====================
MAX_RETRIES = int(os.getenv("AUDIT_MAX_RETRIES", "3"))   # 最大自愈循环迭代次数
AUDIT_SCRIPT = os.getenv("AUDIT_SCRIPT_PATH", "./scripts/audit-engine.sh")
API_URL = os.getenv("AI_API_URL", "https://api.deepseek.com/v1/chat/completions")
API_KEY = os.getenv("AI_API_KEY", "")
MODEL_NAME = os.getenv("AI_MODEL_NAME", "deepseek-chat")

SYSTEM_PROMPT_FIXER = """你是一个代码安全重构专家。你的任务是根据给出的【L1 审计错误日志】和【问题源码内容】，对源码进行原子级的安全脱敏和环境对齐修复。

【硬性注入原则】：
1. 凭证泄露修复：绝不删改业务逻辑！必须将硬编码的密钥移出，改用 `process.env.XXX` 或 `os.getenv('XXX')` 替代。
2. 影子变量修复：如果检测到新增了环境变量，你必须在生成的修复方案中，附带给出对 `.env.example` 的追加追加内容。
3. 严格输出控制：为了确保编排器可解析，你必须输出标准的 JSON 格式，禁止任何 Markdown 包裹块之外的废话。

【输出 JSON 格式规范】：
{
  "changed_files": [
    {
      "filepath": "src/config.ts",
      "action": "rewrite",
      "content": "// 修复后的全量完整代码..."
    },
    {
      "filepath": ".env.example",
      "action": "append",
      "content": "NEW_KEY=\\n"
    }
  ]
}"""


# ==================== 核心函数 ====================

def run_audit() -> tuple[int, str]:
    """运行底层审计脚本，捕获状态码与日志"""
    try:
        result = subprocess.run(
            AUDIT_SCRIPT,
            **_SUBPROCESS_KWARGS
        )
        return result.returncode, result.stdout
    except subprocess.TimeoutExpired:
        return 1, "[FATAL] 审计脚本执行超时"
    except Exception as e:
        return 1, f"[FATAL] 审计脚本执行失败: {str(e)}"


def get_staged_files_content() -> str:
    """获取当前暂存区发生变更的文件上下文，供 AI 参考"""
    try:
        diff_files = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"],
            text=True
        ).splitlines()
    except subprocess.CalledProcessError:
        return "{}"

    context = {}
    for f in diff_files:
        if os.path.exists(f) and os.path.isfile(f):
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
                    context[f] = fh.read()
            except Exception:
                context[f] = "[读取失败]"
    return json.dumps(context, ensure_ascii=False, indent=2)


def call_ai_repair(error_log: str, source_context: str) -> dict:
    """调用大模型获取结构化修复方案"""
    if not API_KEY:
        print("❌ 错误: 未配置 AI_API_KEY 环境变量，无法执行自动修复。")
        print("   请设置: export AI_API_KEY='your-llm-api-key'")
        sys.exit(1)

    user_content = (
        f"【L1 审计错误日志】:\n{error_log}\n\n"
        f"【当前仓库暂存区源码上下文】:\n{source_context}"
    )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_FIXER},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.1
    }

    # 部分 API 支持 JSON Mode 输出；若不支持，通过指令约束输出格式
    try:
        payload["response_format"] = {"type": "json_object"}
    except Exception:
        pass  # 不支持则回退到指令约束

    import requests
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        res_json = response.json()
        raw_content = res_json["choices"][0]["message"]["content"]
        return json.loads(raw_content)
    except requests.exceptions.RequestException as e:
        print(f"❌ [API 调用失败] {str(e)}")
        sys.exit(1)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"❌ [API 响应解析失败] {str(e)}")
        sys.exit(1)


def apply_fixes(fix_plan: dict):
    """将 AI 的修复方案落地到本地文件系统并重新 Stage"""
    for item in fix_plan.get("changed_files", []):
        path = item["filepath"]
        action = item["action"]
        content = item["content"]

        # 确保目标目录存在
        dirpath = os.path.dirname(path)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)

        if action == "rewrite":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  🔧 [重写] {path}")
        elif action == "append":
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
            print(f"  🔧 [追加] {path}")
        elif action == "delete":
            if os.path.exists(path):
                os.remove(path)
                print(f"  🗑️ [删除] {path}")
        else:
            print(f"  ⚠️  [未知动作] {action} 跳过: {path}")
            continue

        # 重新加入 Git 暂存区
        subprocess.run(["git", "add", path], capture_output=True)


def print_summary_header(loop_count: int, max_retries: int):
    """打印迭代轮次标题"""
    print()
    border = "=" * 56
    print(border)
    print(f"  🔄 自愈迭代轮次 [{loop_count}/{max_retries}]")
    print(border)


def print_final_result(exit_code: int, max_retries: int):
    """打印最终审计结果"""
    print()
    border = "=" * 56
    print(border)
    if exit_code == 0:
        print("  🎉 审计完全通过！代码已处于安全就绪状态。")
    else:
        print(f"  ❌ 经 {max_retries} 轮自愈尝试后仍未通过，请人工介入。")
    print(border)


# ==================== 主入口 ====================

def main():
    print(_DEPRECATION_WARNING)
    print("🔄 [Reflection Engine] 启动全自动自愈审计流水线...")
    print(f"   审计脚本: {AUDIT_SCRIPT}")
    print(f"   API 端点: {API_URL}")
    print(f"   模型名称: {MODEL_NAME}")
    print(f"   最大轮次: {MAX_RETRIES}")

    for loop_count in range(1, MAX_RETRIES + 1):
        print_summary_header(loop_count, MAX_RETRIES)

        # 步骤 1: 执行 L1 审计
        code, log = run_audit()

        if code == 0:
            print_final_result(0, MAX_RETRIES)
            # 清理审计产物
            for _f in [AUDIT_SCRIPT, __file__]:
                if os.path.exists(_f):
                    try:
                        os.remove(_f)
                        print(f"  🧹 已清理: {_f}")
                    except Exception:
                        pass
            sys.exit(0)

        # 步骤 2: 审计失败，准备自愈修复
        print("  ⚠️  检测到阻断项，唤起 AI 修复内核...")

        # 步骤 3: 获取暂存区源码上下文
        source_context = get_staged_files_content()

        # 步骤 4: 呼叫 AI 生成修复方案
        try:
            print("  🤖 AI 修复内核正在分析并生成补丁...")
            fix_plan = call_ai_repair(log, source_context)
        except Exception as e:
            print(f"  ❌ [AI 修复失败] {str(e)}")
            sys.exit(1)

        # 步骤 5: 应用修复方案
        print("  📝 正在应用修复补丁...")
        apply_fixes(fix_plan)

        # 自动推进到下一轮循环

    print_final_result(1, MAX_RETRIES)
    sys.exit(1)


if __name__ == "__main__":
    main()
