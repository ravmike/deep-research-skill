---
name: deep-research
description: Conduct enterprise-grade research with multi-source synthesis, citation tracking, and verification. Use when the user needs comprehensive analysis, a research report, or a comparison that requires roughly 10+ sources, cross-source synthesis, or verified claims. Triggers include "deep research", "comprehensive analysis", "research report", "compare X vs Y", and "analyze trends". Do NOT use for simple lookups, debugging, or questions answerable with a couple of searches.
---

# Deep Research

## Purpose

Deliver citation-backed research reports through the 8-phase pipeline:
Scope -> Plan -> Retrieve -> Triangulate -> Outline Refinement -> Synthesize -> Critique -> Refine -> Package.

This skill is for high-effort investigation. It is not the default path for quick factual answers.

## Decide First

```text
Request analysis
|- Simple lookup or one-off fact check? -> Stop. Use Tavily MCP directly, not this skill.
|- Debugging or code repair? -> Stop. Use normal repo tools, not this skill.
`- Multi-source research or report request? -> Continue.

Mode selection
|- Quick -> 3 phases, 2-5 min, broad overview
|- Standard -> 6 phases, 5-10 min, default
|- Deep -> 8 phases, 10-20 min, higher verification
`- UltraDeep -> extended 8-phase investigation, 20-45 min
```

## Workflow

### 1. Clarify

Proceed autonomously by default.

Only ask questions when the request is genuinely incomprehensible or internally contradictory. If the user simply omitted preferences, infer reasonable defaults and continue.

### 2. Plan

Pick the lightest mode that still satisfies the task:

- `quick`: early exploration or time-boxed overview
- `standard`: default for most comparisons and research reports
- `deep`: important decisions that need stronger verification
- `ultradeep`: critical, open-ended, or exhaustive reviews

Announce the chosen mode, expected time range, and target source count, then continue without waiting.

### 3. Retrieve

Use a Tavily-first retrieval policy:

- `mcp__tavily__tavily_search` for the initial fan-out across 5-10 search angles
- `mcp__tavily__tavily_extract` for high-value pages that need detailed extraction
- `mcp__tavily__tavily_research` when the topic is broad, noisy, or benefits from a wider synthesis seed
- `mcp__tavily__tavily_map` or `mcp__tavily__tavily_crawl` for site-structured investigations such as docs portals, standards sites, or regulators

Launch the initial Tavily searches in one assistant message with multiple tool calls. Do not run them sequentially unless the work is inherently dependent.

Fallback to generic browsing only when Tavily is unavailable, blocked, or clearly insufficient for a specific source type.

Read [Complete Methodology](./reference/methodology.md) before running the full retrieval phase.

### 4. Verify

Always run both validation steps before delivery:

```bash
python scripts/verify_citations.py --report [path]
python scripts/validate_report.py --report [path]
```

If either validation fails, fix and retry. After two failures on the same issue, stop and report the blocker instead of silently shipping a weak report.

### 5. Deliver

Deliver a complete report, not loose notes:

- save markdown as the primary source artifact
- generate HTML from the markdown report
- generate PDF if the current environment provides a working PDF path; otherwise state the limitation explicitly
- tell the user where the files were written

Read [Reporting and Delivery](./reference/reporting.md) before packaging output.
Read [Quality and Validation](./reference/quality.md) before final review.

## Output Guardrails

Every report must:

- distinguish source-grounded facts from synthesis
- cite major factual claims inline
- include limitations and methodology
- include a complete bibliography with every cited source
- document any missing evidence or unavailable sources explicitly

Use [Report Template](./templates/report_template.md) as the required report shape.

## Scripts

Use the bundled scripts when they match the task:

- `scripts/research_engine.py`: orchestration prompts and state handling
- `scripts/verify_citations.py`: citation existence and metadata checks
- `scripts/validate_report.py`: report structure and quality checks
- `scripts/source_evaluator.py`: credibility scoring
- `scripts/md_to_html.py`: markdown-to-HTML conversion
- `scripts/verify_html.py`: HTML parity checks against markdown

## Progressive References

Load only what is needed for the current step:

- [Complete Methodology](./reference/methodology.md): phase-by-phase execution details
- [Reporting and Delivery](./reference/reporting.md): file layout, report assembly, HTML/PDF packaging
- [Quality and Validation](./reference/quality.md): anti-hallucination, writing standards, stop rules, acceptance checks
- [Report Template](./templates/report_template.md): exact output structure

Historical and supporting docs such as `README.md`, `QUICK_START.md`, and the analysis writeups can remain in the repo, but they are not part of the default runtime loading path for this skill.
