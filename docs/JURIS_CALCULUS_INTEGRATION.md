# juris-calculus v2.0 MCP Integration Protocol

ULA Agent detects juris-calculus service availability and calls symbolic reasoning. Falls back to Prompt mode when unreachable.

## Tools (10)

| Tool | Parameters | Function | Agent |
|:---|:---|:---|:---|
| `trirail_collide` | `facts`, `scenario_id`, `context` | HKxUSxPRC tri-rail collision | Strategist |
| `check_threat` | `facts` | Threat signature + USC citation validation | Reviewer |
| `generate_memo` | `case_id`, `trirail_result` | Partner-ready cross-border memo | Writer |
| `route_state` | `raw_fact`, `state_code` | US state-level legal routing | Researcher |
| `get_citation` | `rule_id` | CBL/SPC rule statutory text | Researcher |
| `stratified_evaluate` | `facts` | 4-stage Horn+AAF pipeline (v2.0 new) | Strategist |
| `claims_detail` | `case_id` | Claims with trust_label (v2.0 new) | Writer |
| `blueprint_query` | `domain`, `query` | juris_blueprint.json query (v2.0 new) | Researcher |
| `neural_status` | — | NLNI cold-start status (v2.0 new) | Reviewer |
| `adversarial_audit` | `claims` | Reasoner/Auditor/Verifier pipeline (v2.0 new) | Strategist |

## Resources (12)

| URI | Content |
|:---|:---|
| `legal://blueprint` | juris_blueprint.json (5.8MB, v2.0 new) |
| `legal://blocking-rules` | 60 CBL blocking rules |
| `legal://spc-rules` | 23 SPC judicial tendency rules |
| `legal://term-mappings` | 131 tri-jurisdiction L0 term alignments |
| `legal://hk-rules` | 93 HK statutory Horn rules |
| `legal://hk-extended` | HK extended rules (v2.0 new) |
| `legal://us-rules` | 81 US federal Horn rules |
| `legal://us-courts` | 266 US court hierarchy index (v2.0 new) |
| `legal://cn-rules` | 2,117 CN statutory Horn rules |
| `legal://glossary/{jurisdiction}` | Merged jurisdiction glossary |
| `legal://state-router` | US 50-state topology router |
| `legal://operator-schemas` | All registered operator JSON Schemas |

## v2.0 Addon Architecture

```
addons/
  hk/    Hong Kong (Cap 26, 364 Horn rules, Common Law)
  us/    United States (UCC, 53 Title index, 266 courts, 419 terms, Common Law)
  federation/  Common-law pair-wise comparison engine
```

Core engine is China-law only. HK/US loaded via `plugin_registry.get()` on demand.

## Deployment

```bash
cd juris-calculus
pip install -r requirements.txt
python mcp_server.py
```

Set `JURIS_CONFIG_DIR` for personal YAML library (multi-lawyer sharing).
