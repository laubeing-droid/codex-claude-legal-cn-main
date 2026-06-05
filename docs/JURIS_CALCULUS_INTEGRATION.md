# juris-calculus 推理内核 MCP 调用协议

`juris-calculus` 为独立符号化法律推理内核，通过 MCP stdio JSON-RPC 协议暴露能力。ULA Agent 检测到 juris-calculus 服务可用时自动调用，不可达时降级为 Prompt 推理模式。

## 一、MCP 工具清单（7 个）

| 工具名 | 参数 | 功能 | ULA Agent |
|:---|:---|:---|:---|
| `trirail_collide` | `facts`, `scenario_id`, `context` | HK×US×PRC 三轨并发对撞 | Strategist |
| `check_threat` | `facts` | 检测是否命中 WI/NJ 威胁签名 | Reviewer |
| `generate_memo` | `case_id`, `trirail_result` | 生成合伙人级跨境争议处置备忘录 | Writer |
| `route_state` | `raw_fact`, `state_code` | 美国州级法律术语拓扑路由 | Researcher |
| `get_citation` | `rule_id` | 查询 CBL/SPC 规则对应的法条全文 | Researcher |
| `get_operator_schemas` | `filter`, `type_filter` | 获取全部已注册法律算子 Schema | Strategist, Researcher |
| `generate_task_schema` | `jurisdiction_focus` | 动态生成法律对抗任务定义 | Scheduler |

## 二、MCP 资源清单（9 个）

| URI | 内容 |
|:---|:---|
| `legal://blocking-rules` | 60 条 CBL 强制阻断规则 |
| `legal://spc-rules` | 23 条最高法裁判倾向 Horn 规则 |
| `legal://term-mappings` | 131 条三法域 L0 术语对齐 |
| `legal://hk-rules` | 93 条香港成文法 Horn 规则 |
| `legal://us-rules` | 81 条美国联邦法域 Horn 规则 |
| `legal://cn-rules` | 2,117 条中国成文法全量 Horn 规则 |
| `legal://glossary/{jurisdiction}` | 法域合并术语库 |
| `legal://state-router` | 美国 50 州拓扑路由器 |
| `legal://operator-schemas` | 全部已注册算子 JSON Schema |

## 三、调用示例

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "trirail_collide",
    "arguments": {
      "facts": [
        "原告提供了加盖有被告公章的施工图纸",
        "被告辩称公章系项目经理私自刻印，且项目经理已被追究刑事责任"
      ],
      "scenario_id": "const-001",
      "context": "境内"
    }
  },
  "id": "collide_001"
}
```

## 四、部署

```bash
cd juris-calculus
pip install -r requirements.txt
python mcp_server.py
```

ULA Agent 检测到 juris-calculus MCP 服务不可达时，自动降级为纯 Prompt 推理模式，不阻塞工作流。
