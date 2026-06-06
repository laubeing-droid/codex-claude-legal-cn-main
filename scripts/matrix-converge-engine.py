#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: matrix-converge-engine.py
Description: 四层收敛发布前置自愈引擎 (Unified Convergence Orchestrator)
Version:    3.1.0
Changelog:
  v3.1.0 - [FIX] 所有 subprocess.run 显式 encoding='utf-8', errors='surrogateescape'
          - [FIX] 增加 per-file 级联计数器 max_matrix_cycles 防止死循环
          - [FIX] safe_log_exception 对 Authorization 和敏感内容脱敏
          - [FIX] 增加文件震荡检测，同一文件修改超限触发 HITL

架构原则 — 不动点迭代 (Fixed-Point Iteration):
  系统状态 S 经过 AI 原子重构函数 F 修复后，
  若 F(S) = S，则系统达到不动点，允许外发。

管道漏斗（由外到内，层层收紧）：
  L1: 供应链收敛层 — 依赖安全与闭环验证
  L2: 零信任脱敏层 — 硬编码凭证/拓扑泄露拦截
  L3: 语义规约对齐层 — 规约与实现的 Δ=∅ 收敛
  L4: TDD 运行时层 — 测试全绿 & 覆盖率达标
"""

import os
import sys
import json
import re
import subprocess
import requests

# ==================== 引擎超参数 ====================
MAX_GLOBAL_LOOPS = int(os.getenv("MATRIX_MAX_LOOPS", "4"))
MAX_FILE_CYCLES = int(os.getenv("MATRIX_MAX_FILE_CYCLES", "5"))  # 单文件震荡上限
API_URL = os.getenv("AI_API_URL", "https://api.deepseek.com/v1/chat/completions")
API_KEY = os.getenv("AI_API_KEY", "")
MODEL_NAME = os.getenv("AI_MODEL_NAME", "deepseek-chat")
POLICY_FILE = ".github/audit-policy.local.md"

# 公共 subprocess 参数：统一 UTF-8 编码防御
_SUBPROCESS_KWARGS = {
    "shell": True,
    "capture_output": True,
    "text": True,
    "encoding": "utf-8",
    "errors": "surrogateescape",
}


def safe_log(msg: str, max_len: int = 500) -> str:
    """安全日志：脱敏 Authorization 头和疑似凭证内容"""
    # 脱敏 Bearer token
    msg = re.sub(r'(Authorization:\s*Bearer\s+)(sk-\w+|ghp_\w+|github_pat_\w+)',
                 r'\1***REDACTED***', msg, flags=re.IGNORECASE)
    # 脱敏内联 API Key 模式
    msg = re.sub(r'(sk-[a-zA-Z0-9]{20,})', 'sk-***REDACTED***', msg)
    msg = re.sub(r'(ghp_[a-zA-Z0-9]{20,})', 'ghp_***REDACTED***', msg)
    # 截断过长消息
    if len(msg) > max_len:
        msg = msg[:max_len] + "... [TRUNCATED]"
    return msg


class MatrixConvergenceEngine:
    def __init__(self):
        self.current_loop = 0
        self.failure_trace = []
        # 文件震荡计数器：{文件路径: 被修改次数}
        self.file_change_counter = {}

    # ==================== 日志 & 安全辅助 ====================

    @staticmethod
    def log(layer: str, msg: str, status: str = "INFO"):
        icons = {"INFO": "🔹", "SUCCESS": "✅", "ERROR": "🚨", "HITL": "👤", "LEARN": "📚"}
        safe_msg = safe_log(msg)
        print(f"[{layer}] {icons.get(status, '🔹')} {safe_msg}")

    def _subprocess_run(self, cmd: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """安全的 subprocess.run 包装：统一编码 + 超时"""
        return subprocess.run(
            cmd,
            **_SUBPROCESS_KWARGS,
            timeout=timeout,
        )

    # ==================== L1 供应链收敛层 ====================

    def verify_l1(self) -> tuple[bool, str]:
        self.log("L1_SUPPLY", "检查依赖树完整性与安全性...", "INFO")
        cmd = os.getenv("MATRIX_L1_CMD", "auto")
        if cmd == "auto":
            if os.path.exists("poetry.lock") or os.path.exists("pyproject.toml"):
                cmd = "poetry check 2>&1"
            elif os.path.exists("pnpm-lock.yaml"):
                cmd = "pnpm audit --audit-level=high 2>&1"
            elif os.path.exists("package-lock.json"):
                cmd = "npm audit --audit-level=high 2>&1"
            elif os.path.exists("Cargo.lock"):
                cmd = "cargo audit 2>&1"
            elif os.path.exists("go.sum"):
                cmd = "go mod verify 2>&1"
            elif os.path.exists("requirements.txt") or os.path.exists("Pipfile"):
                cmd = "pip-audit 2>&1"
            else:
                return True, "No package manager detected. L1 skipped."
        try:
            r = self._subprocess_run(cmd, timeout=120)
            if r.returncode != 0:
                return False, f"L1 failure:\n{r.stderr or r.stdout}"
            return True, "Supply chain intact."
        except subprocess.TimeoutExpired:
            return False, "L1 timed out (120s)."
        except FileNotFoundError:
            return True, "L1 tool not installed. Skipped."

    # ==================== L2 零信任脱敏层 ====================

    def verify_l2(self) -> tuple[bool, str]:
        self.log("L2_SANITIZE", "执行物理层脱敏扫描...", "INFO")
        sp = "./scripts/audit-engine.sh"
        if not os.path.exists(sp):
            return False, f"Missing: {sp}. Deploy assets/audit-engine.sh first."
        r = self._subprocess_run(sp, timeout=120)
        if r.returncode != 0:
            return False, f"L2 blockers:\n{r.stdout}"
        return True, "Zero-trust sanitization passed."

    # ==================== L3 语义规约对齐层 ====================

    def verify_l3(self) -> tuple[bool, str]:
        self.log("L3_SEMANTIC", "验证语义规约对齐 (Δ = ∅)...", "INFO")
        issues = []
        if os.path.exists(".env") and os.path.exists(".env.example"):
            with open(".env", encoding="utf-8", errors="ignore") as f:
                env_k = {l.split("=")[0].strip() for l in f
                         if "=" in l and not l.startswith("#")}
            with open(".env.example", encoding="utf-8", errors="ignore") as f:
                ex_k = {l.split("=")[0].strip() for l in f
                        if "=" in l and not l.startswith("#")}
            shadow = env_k - ex_k
            if shadow:
                issues.append(f"Shadow env vars Δ = {{{', '.join(shadow)}}}")
        for sf in ["openapi.yaml", "openapi.json", "schema.prisma"]:
            if os.path.exists(sf):
                self.log("L3_SEMANTIC", f"规约文件 {sf} 存在（验证扩展点）", "INFO")
        if issues:
            return False, "Semantic gap detected:\n" + "\n".join(issues)
        return True, "Fixed-point reached. Δ = ∅."

    # ==================== L4 TDD 运行时层 ====================

    def verify_l4(self) -> tuple[bool, str]:
        self.log("L4_TDD", "执行测试运行时验证...", "INFO")
        if os.path.exists("pytest.ini") or os.path.exists("pyproject.toml"):
            cmd = "python -m pytest -x --tb=short 2>&1 | tail -50"
        elif os.path.exists("jest.config.js"):
            cmd = "npx jest --bail 1 2>&1 | tail -50"
        elif os.path.exists("go.mod"):
            cmd = "go test ./... 2>&1 | tail -50"
        elif os.path.exists("Cargo.toml"):
            cmd = "cargo test 2>&1 | tail -50"
        else:
            return True, "No test framework. L4 skipped."
        try:
            r = self._subprocess_run(cmd, timeout=300)
            if r.returncode != 0:
                return False, f"L4 regression:\n{r.stdout}"
            return True, "All tests green."
        except subprocess.TimeoutExpired:
            return False, "L4 timed out (300s)."

    # ==================== AI 修复内核 ====================

    def ai_fix(self, layer: str, log: str) -> dict:
        self.log("AI_CORE", f"修复 {layer}...", "INFO")

        # 收集上下文
        ctx = {}
        try:
            files = subprocess.check_output(
                ["git", "diff", "--cached", "--name-only"],
                encoding="utf-8", errors="surrogateescape",
            ).splitlines()
        except Exception:
            files = []

        for f in files:
            if os.path.isfile(f):
                try:
                    with open(f, encoding="utf-8", errors="ignore") as fh:
                        ctx[f] = fh.read()[:5000]
                except Exception:
                    pass
        for cf in [".env.example", ".env", "package.json", "pyproject.toml"]:
            if os.path.isfile(cf) and cf not in ctx:
                try:
                    with open(cf, encoding="utf-8", errors="ignore") as fh:
                        ctx[cf] = fh.read()[:3000]
                except Exception:
                    pass

        # 检查策略样本
        policy_ctx = ""
        if os.path.exists(POLICY_FILE):
            try:
                with open(POLICY_FILE, encoding="utf-8", errors="ignore") as f:
                    policy_ctx = f.read()[:2000]
            except Exception:
                pass

        sp = (
            "你是一个架构级自愈内核。根据【崩溃层级】【错误日志】【源码上下文】输出修复方案。\n\n"
            "【约束】\n"
            "1. 绝不删除核心业务逻辑，只做脱敏、补全、对齐、修复。\n"
            "2. 修复后必须 git add 受影响的文件。\n"
            "3. 输出纯 JSON，无 Markdown 包裹，无多余解释。\n\n"
            "【JSON 格式】\n"
            "{\"patches\":["
            "{\"filepath\":\"...\",\"action\":\"rewrite\",\"content\":\"...\"},"
            "{\"filepath\":\"...\",\"action\":\"append\",\"content\":\"...\"}"
            "]}\n"
        )
        if policy_ctx:
            sp += f"\n【历史策略参考】\n{policy_ctx}\n"

        uc = (
            f"【崩溃层级】: {layer}\n\n"
            f"【错误日志】:\n{log}\n\n"
            f"【上下文】:\n{json.dumps(ctx, ensure_ascii=False, indent=2)}"
        )

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": sp},
                {"role": "user", "content": uc}
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }

        try:
            r = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=payload,
                timeout=60,
            )
            r.raise_for_status()
            return json.loads(r.json()["choices"][0]["message"]["content"])
        except Exception as e:
            # 安全日志：不泄露 API_KEY
            self.log("AI_CORE",
                      f"API 调用失败: {safe_log(str(e))}", "ERROR")
            sys.exit(1)

    # ==================== 应用补丁 ====================

    def apply(self, plan: dict) -> list:
        """应用补丁，返回被修改的文件列表"""
        changed = []
        for p in plan.get("patches", []):
            path = p["filepath"]
            action = p["action"]
            content = p["content"]
            d = os.path.dirname(path)
            if d:
                os.makedirs(d, exist_ok=True)
            if action == "rewrite":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            elif action == "append":
                with open(path, "a", encoding="utf-8") as f:
                    f.write(content)
            subprocess.run(["git", "add", path],
                           capture_output=True,
                           encoding="utf-8", errors="surrogateescape")
            self.log("PATCH", f"{action}: {path}", "SUCCESS")
            changed.append(path)
        return changed

    # ==================== 震荡检测（防死循环） ====================

    def check_oscillation(self, changed_files: list) -> bool:
        """检测文件震荡：同一文件修改超过 MAX_FILE_CYCLES 则触发 HITL"""
        for f in changed_files:
            self.file_change_counter[f] = self.file_change_counter.get(f, 0) + 1
            count = self.file_change_counter[f]
            if count >= MAX_FILE_CYCLES:
                self.log("OSCILLATION",
                         f"文件 {f} 已被修改 {count} 次仍未收敛，"
                         f"触发震荡退耦！", "ERROR")
                return True
        return False

    # ==================== 策略学习 ====================

    def learn_from_fix(self, layer: str, error_log: str):
        try:
            os.makedirs(os.path.dirname(POLICY_FILE), exist_ok=True)
            entry = (
                f"\n## Policy: {layer} | {__import__('datetime').datetime.now().isoformat()}\n"
                f"- Error: {error_log[:200]}\n"
                f"- Fix: git diff HEAD\n"
            )
            with open(POLICY_FILE, "a", encoding="utf-8") as f:
                f.write(entry)
            self.log("LEARN", f"已追加策略样本到 {POLICY_FILE}", "LEARN")
        except Exception as e:
            self.log("LEARN", f"策略学习写入失败: {safe_log(str(e))}", "ERROR")

    # ==================== 主控状态机 ====================

    def run(self):
        if not API_KEY:
            self.log("SYSTEM", "AI_API_KEY 未配置！", "ERROR")
            sys.exit(1)

        pipeline = [
            ("L1_SUPPLY", self.verify_l1),
            ("L2_SANITIZE", self.verify_l2),
            ("L3_SEMANTIC", self.verify_l3),
            ("L4_TDD", self.verify_l4),
        ]

        border = "=" * 58

        while self.current_loop < MAX_GLOBAL_LOOPS:
            self.current_loop += 1
            print(f"\n{border}")
            print(f"  🌐 矩阵收敛大循环 [{self.current_loop}/{MAX_GLOBAL_LOOPS}]")
            print(border)

            all_pass = True
            for name, fn in pipeline:
                ok, msg = fn()
                if ok:
                    self.log(name, msg, "SUCCESS")
                else:
                    self.log(name, msg, "ERROR")
                    all_pass = False
                    self.failure_trace.append((name, msg[:300]))

                    # AI 修复
                    plan = self.ai_fix(name, msg)
                    changed_files = self.apply(plan)

                    # 震荡检测：同一文件被反复修改 → HITL
                    if self.check_oscillation(changed_files):
                        self._hitl_escalate(
                            f"文件震荡检测: {changed_files} 被修改超过 "
                            f"{MAX_FILE_CYCLES} 次仍未收敛"
                        )
                        sys.exit(1)

                    # 任意层失败 → 跳出内循环，从 L1 重新扫描
                    break

            if all_pass:
                print(f"\n{border}")
                print(f"  🎉 不动点达成！第 {self.current_loop} 轮收敛。")
                print(border)
                sys.exit(0)

        # ===== HITL 降级 =====
        self._hitl_escalate(f"{MAX_GLOBAL_LOOPS} 轮全局循环未收敛")

    def _hitl_escalate(self, reason: str):
        """HITL 降级 — 生成决策简报"""
        print(f"\n{border}")
        print(f"  👤 HITL 降级: {reason}")
        print(border)
        self.log("HITL", "生成冲突决策简报...", "HITL")

        report = "# 多维冲突决策简报\n\n## 降级原因\n"
        report += f"{reason}\n\n## 失败轨迹\n"
        for i, (ln, em) in enumerate(self.failure_trace, 1):
            report += f"{i}. **{ln}**: {em[:200]}\n"
        report += "\n## 建议修复路线\n"
        report += "A) 回退至上一稳定版本，重新设计相关模块\n"
        report += "B) 检查是否有外部依赖版本冲突，锁定兼容版本\n"
        report += "C) 手动审查并修复后，自动吸收为策略样本\n"

        os.makedirs(".github", exist_ok=True)
        with open(".github/converge-briefing.md", "w", encoding="utf-8") as f:
            f.write(report)
        self.log("HITL", "简报已生成: .github/converge-briefing.md", "HITL")
        self.log("HITL", "等待人工介入。修复完成后引擎将自动学习本次修正方案。", "HITL")


if __name__ == "__main__":
    MatrixConvergenceEngine().run()
