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

Use a source-class retrieval policy, not a blanket Tavily-first rule:

- Official guidelines, regulators, standards, and product docs:
  - go directly to the official source when known
  - otherwise use domain-targeted search first
- Primary papers and formal reviews:
  - prefer direct paper discovery and extraction over broad synthesis tools
- Broad or noisy topics:
  - use `tavily_search` for the initial fan-out across 5-10 search angles
  - use `tavily_extract` for shortlisted high-value pages
  - use `tavily_research` only as an escalation when search/extract is still too noisy or fragmented
- Structured sites:
  - use `tavily_map` or `tavily_crawl`

Launch the initial Tavily searches in one assistant message with multiple tool calls. Do not run them sequentially unless the work is inherently dependent.

When retrieval fails, use this fallback order:
1. retry with a narrower search or fewer filters
2. remove unsupported or brittle parameters
3. switch to official-source search
4. switch to direct page extraction
5. switch to generic browsing only when the above are insufficient

Known tool quirks to account for during retrieval and verification:
- Tavily parameters are strict and some values are rejected rather than ignored
- broad synthesis calls can time out
- some official and publisher pages block `HEAD` requests
- some publisher pages block automated access and require alternate links such as PubMed or PMC

Maintain a source ledger while retrieving. For every shortlisted source, track:
- citation number
- source type
- URL
- access status
- verification status
- publication date
- major claims the source is meant to support

Read [Complete Methodology](./reference/methodology.md) before running the full retrieval phase.

### 4. Verify

Always run report validation before delivery:

```bash
python scripts/verify_citations.py --report [path]
python scripts/validate_report.py --report [path]
```

Treat citation verification as robust verification, not just script pass/fail:
- if `verify_citations.py` reports blocked or unverified URLs, distinguish broken citations from network issues, publisher blocking, and `HEAD` false negatives
- use alternate links such as PubMed or PMC when the primary publisher URL blocks automation
- only ship with unresolved unverified citations if the limitation is explicitly documented

If validation fails, fix and retry. After two failures on the same issue, stop and report the blocker instead of silently shipping a weak report.

### 5. Deliver

Deliver a complete report, not loose notes:

- save markdown as the primary source artifact
- generate HTML with `scripts/build_report.py`
- generate PDF only if the current environment has a tested working export path; otherwise state the limitation explicitly at delivery time
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
- `scripts/md_to_html.py`: markdown-fragment conversion used by the builder
- `scripts/build_report.py`: canonical markdown-to-HTML report builder
- `scripts/verify_html.py`: HTML parity checks against markdown

## Progressive References

Load only what is needed for the current step:

- [Complete Methodology](./reference/methodology.md): phase-by-phase execution details
- [Reporting and Delivery](./reference/reporting.md): file layout, report assembly, HTML/PDF packaging
- [Quality and Validation](./reference/quality.md): anti-hallucination, writing standards, stop rules, acceptance checks
- [Report Template](./templates/report_template.md): exact output structure

Historical and supporting docs such as `README.md`, `QUICK_START.md`, and the analysis writeups can remain in the repo, but they are not part of the default runtime loading path for this skill.
