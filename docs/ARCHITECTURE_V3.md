# unified-legal-ai-cn v3 Architecture Proposal

## Overview

v3 replaces the 5-agent linear pipeline with a **Loop Agent + Skill Marketplace + Legal Research** architecture.

## 1. CaseState Model

```json
{
  "case_id": "2026-CIV-001",
  "case_type": "合同纠纷",
  "phases": {
    "intake":   {"status": "pending", "missing": ["事实完整性"]},
    "analysis": {"status": "pending", "missing": ["法条依据", "违约金计算"]},
    "strategy": {"status": "skipped", "missing": []},
    "output":   {"status": "pending", "missing": ["审查意见书"]}
  },
  "iteration": 0,
  "max_iterations": 20,
  "converged": false
}
```

## 2. Skill Marketplace

### 2.1 marketplace.json

```json
{
  "version": "1.0.0",
  "sources": [
    {"name": "official", "url": "https://github.com/laubeing-droid/legal-skills-market"},
    {"name": "community", "url": "https://github.com/awesome-legal-ai-zh/community-skills"}
  ],
  "installed": {}
}
```

### 2.2 Skill Manifest

Each skill has manifest.json with: name, version, phase (intake/analysis/strategy/output/research), case_types, provides_tools, requires, replaceable.

### 2.3 CLI

```bash
python scripts/market.py install legal-research
python scripts/market.py install --repo github.com/someone/my-skill
python scripts/market.py remove trial-sim
python scripts/market.py list --available
```

## 3. Loop Agent

Single agent. Gap-driven iteration:

```
State = skill.case_state_template + lawyer_profile
LOOP:
  gap = max(State.missing)
  skill = marketplace.match(phase=gap.phase)
  result = call(skill)
  State = State.merge(result)
  if all_done or max_iterations: break
```

## 4. Legal Research

Standalone marketplace skill with provider abstraction. Providers declared in YAML, not code.

```
skills/core/legal-research/
  SKILL.md
  manifest.json
  providers/
    juris-calculus.yaml
    multi-search.yaml
```

## 5. Lawyer Profile

Per-lawyer config file. Clone-and-edit.

```json
{
  "defaults": {"court": "福建漳州", "jurisdiction": "CN"},
  "templates": {
    "合同纠纷": "contract-review",
    "侵权纠纷": "case-research -> evidence-check -> calculate-damages",
    "刑事案件": "grill-case -> scan-risks -> case-research -> trial-simulation"
  },
  "research_provider": "juris-calculus"
}
```

## 6. Third-Party Integration

Any GitHub repo is a skill if it has: SKILL.md + manifest.json (phase, case_types, tools)

## 7. Migration

P0: marketplace.json + market.py CLI + Legal Research core skill
P1: CaseState model + LoopAgent.md (coexists with legacy agents)
P2: Add manifest.json to core skills
P3: Validate vs 5-agent pipeline
P4: Mark legacy agents deprecated

## 8. Target File Tree

```
unified-legal-ai-cn/
  .claude/agents/LoopAgent.md       # NEW
  .claude/agents/*.md                # DEPRECATED (5 legacy)
  skills/marketplace.json            # NEW
  skills/core/legal-research/        # NEW
  skills/community/                  # NEW
  scripts/market.py                  # NEW
  lib/case_state.py                  # NEW
  lib/loop_controller.py             # NEW
  lawyer-profile.json.example        # NEW
```


## 9. Skill Marketplace Implementation

The marketplace engine is powered by the **legal-repo-consolidation** Codex skill (4-layer pipeline: topology merge -> dedup -> architecture -> license cleaning).

### 9.1 Architecture

```
marketplace-sources.json     # source registry (add repos here)
merge_marketplace.py         # discovery engine (Layer 1 + 2)
legal-repo-consolidation     # Codex skill (full 4-layer pipeline)

Pipeline:
  marketplace-sources.json
    -> merge_marketplace.py (discover, R_legal score, categorize)
    -> legal-repo-consolidation (deep merge via Codex)
    -> skills/{category}/ (6 output categories)
    -> marketplace-registry.json + marketplace-graph.json
```

### 9.2 R_legal Scoring

R_legal = Ch_legal / Ch_total. Measures legal citation density:
- HIGH (R_legal < 30%, Nctrl >= 5): clean-room rewrite candidate
- MEDIUM (30% <= R_legal <= 70%): sentence-level interpolation
- LOW (R_legal > 70%, Nctrl < 5): citation heap -> data/rules/

### 9.3 6 Output Categories

| Category | Description |
|----------|-------------|
| legal-research | 法条检索、类案搜索、裁判口径归纳 |
| document-generation | 起诉状、答辩状、代理词生成 |
| contract-review | 合同审查、条款分析、风险识别 |
| litigation-support | 质证、庭审模拟、判诉差异分析 |
| knowledge-management | 法律知识库、裁判规则库 |
| regulatory-compliance | 劳动仲裁、行政合规、数据隐私 |

### 9.4 CLI

```bash
python connectors/merge_marketplace.py           # sync all
python connectors/merge_marketplace.py --dry-run  # preview
python connectors/merge_marketplace.py --list     # installed by category
python connectors/merge_marketplace.py --graph    # knowledge graph
```

### 9.5 Adding a Source

Add to marketplace-sources.json:

```json
{"name": "my-source", "type": "github", "url": "https://github.com/user/repo",
 "branch": "main", "skill_pattern": "**/SKILL.md", "compatibility_min_score": 0.5}
```

Then `python connectors/merge_marketplace.py --source my-source`.

### 9.6 Integration with Loop Agent

Loop Agent discovers skills via marketplace-registry.json. Each entry has name, category, R_legal score, quality. Matches skills to CaseState gaps by phase -> category.

