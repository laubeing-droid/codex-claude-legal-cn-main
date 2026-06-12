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

The marketplace engine lives in the dynamic-update system:

```
liuweibin-legal-skills_dynamic-update/
  liuweibin-legal-skills/
    connectors/
      marketplace-sources.json     # marketplace source definitions
      merge_marketplace.py         # sync/merge engine (Python)
    skills/
      community/                   # installed 3rd-party skills
        marketplace.json           # auto-generated manifest
```

### 9.1 marketplace-sources.json

Defines which GitHub repos to pull from. Any repo with SKILL.md files can be a source.

### 9.2 merge_marketplace.py

```bash
python connectors/merge_marketplace.py           # sync all
python connectors/merge_marketplace.py --dry-run  # preview
python connectors/merge_marketplace.py --list     # show installed
```

Pipeline: clone/pull repo -> find SKILL.md -> compute compatibility score -> filter by min_score -> copy to skills/community/ -> update marketplace.json manifest.

### 9.3 Integration with Loop Agent

Loop Agent reads `skills/community/marketplace.json` at startup to discover installed skills. Each skill entry has: name, version, source, compatibility score. Loop Agent matches skills to CaseState gaps by phase and case_type.

### 9.4 Adding a Third-Party Source

Add to marketplace-sources.json:

```json
{
  "name": "my-favorite-skills",
  "type": "github",
  "url": "https://github.com/someone/legal-skills",
  "branch": "main",
  "skill_pattern": "**/SKILL.md",
  "auto_update": false,
  "compatibility_min_score": 0.6
}
```

Then `python connectors/merge_marketplace.py --source my-favorite-skills`.

