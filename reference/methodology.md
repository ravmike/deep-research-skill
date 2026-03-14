# Deep Research Methodology: 8-Phase Pipeline

## Contents

- Overview
- Phase 1: Scope
- Phase 2: Plan
- Phase 3: Retrieve
- Phase 4: Triangulate
- Phase 4.5: Outline Refinement
- Phase 5: Synthesize
- Phase 6: Critique
- Phase 7: Refine
- Phase 8: Package
- Advanced Features

## Overview

This document contains the detailed execution guidance for the deep-research pipeline. Use it once the skill has already triggered and the work clearly requires multi-source investigation.

The default operating pattern is:

1. Frame the question well.
2. Retrieve evidence in parallel.
3. Verify major claims across independent sources.
4. Synthesize only after the fact base is stable.
5. Package the report with validation before delivery.

## Phase 1: Scope

**Objective:** Define research boundaries and success criteria.

**Activities:**
1. Decompose the question into core components.
2. Identify stakeholder perspectives.
3. Define scope boundaries.
4. Establish success criteria.
5. List assumptions that need validation.

**Output:** Structured scope with boundaries, perspectives, and assumptions.

## Phase 2: Plan

**Objective:** Create a research roadmap before retrieval starts.

**Activities:**
1. Identify primary and secondary source types.
2. Map knowledge dependencies.
3. Draft search-query variants.
4. Plan triangulation for major claims.
5. Estimate effort by phase.
6. Define quality gates.

**Output:** Research plan with prioritized investigation paths and verification strategy.

## Phase 3: Retrieve

**Objective:** Collect evidence quickly and systematically using source-class routing plus targeted retrieval.

**Core rule:** Decompose the question into 5-10 independent search angles before launching any search calls, then launch the initial search batch in one assistant message with multiple Tavily tool calls.

### Query Decomposition Strategy

Cover as many of these angles as the topic warrants:

1. Core topic framing
2. Technical details or implementation specifics
3. Recent developments
4. Academic or formal analysis
5. Alternative perspectives and criticisms
6. Statistical or benchmark evidence
7. Industry or market context
8. Failure modes, limitations, and edge cases

### Source-Class Routing

Do not treat every topic as a Tavily fan-out problem.

- Official guidelines, regulators, and standards:
  - route to official sources first
  - use domain-constrained search only when the official page is unknown
- Primary papers:
  - prefer direct paper records, PubMed/PMC, DOI pages, or official journal pages
- Broad or noisy topics:
  - use Tavily search fan-out, then extract
- Structured sites:
  - use map or crawl

### Tavily Tool Selection

Use the narrowest Tavily tool that matches the step:

- `tavily_search`
  - Default for the initial fan-out.
  - Use `query`, `topic`, `search_depth`, `max_results`, and date/domain filters as needed.
- `tavily_extract`
  - Use after shortlist creation.
  - Pull detailed page content from 5-10 promising URLs.
- `tavily_research`
  - Use only after search/extract when the topic is still broad, noisy, or spans many subtopics.
  - Treat it as a synthesis seed, not as a replacement for independent verification.
- `tavily_map` or `tavily_crawl`
  - Use for structured site exploration such as standards bodies, product docs, or agency portals.

Fallback to generic browsing only if Tavily is unavailable or clearly cannot cover the needed source class.

### Retrieval Failure Fallback Order

If a retrieval step fails:

1. Retry with a narrower query.
2. Remove brittle or unsupported parameters.
3. Switch to an official-source search.
4. Switch to direct page extraction.
5. Switch to generic browsing only when necessary.

### Tool Quirks to Expect

- Some Tavily parameters are strict and rejected instead of ignored.
- Broad synthesis calls may time out.
- Some pages reject `HEAD` while allowing `GET`.
- Some publisher pages block bots and require alternate records such as PubMed or PMC.

### Parallel Execution Protocol

1. Launch all initial Tavily searches concurrently.
2. In parallel, spawn sub-agents for deep-dive work that benefits from independent context:
   - academic-paper review
   - documentation deep dives
   - codebase or repository inspection
   - market or regulatory analysis
3. Shortlist sources as results arrive.
4. Run `tavily_extract` on the shortlisted URLs.
5. Track gaps and launch targeted follow-up searches only where evidence is still weak.
6. Maintain a source ledger with citation number, source type, URL, access status, verification status, publication date, and intended claims supported.

### Example Search Batch

```text
[Single assistant message with multiple tool calls]
- tavily_search(query="quantum computing state of the art 2025", topic="general", search_depth="advanced", max_results=8, start_date="2024-01-01")
- tavily_search(query="quantum computing limitations and failure modes", topic="general", search_depth="advanced", max_results=8)
- tavily_search(query="quantum computing commercial adoption 2024 2025", topic="general", search_depth="advanced", max_results=8)
- tavily_search(query="quantum error correction", topic="general", search_depth="advanced", max_results=8, include_domains=["arxiv.org", "nature.com", "science.org"])
- Task(subagent_type="general-purpose", description="Academic analysis", prompt="Review 2024-2025 quantum computing papers and extract methods, benchmarks, and limits.")
- Task(subagent_type="general-purpose", description="Industry analysis", prompt="Review commercial adoption, vendor claims, and customer evidence for quantum computing.")
```

### Example Extraction Batch

```text
- tavily_extract(
    urls=["https://example.com/source-1", "https://example.com/source-2"],
    format="markdown",
    extract_depth="advanced",
    query="Extract dates, benchmarks, limitations, and quantitative claims."
  )
```

### First Finish Search Pattern

Proceed once the first acceptable evidence threshold is reached:

- `quick`: 10+ sources with average credibility above 60, or 2 minutes elapsed
- `standard`: 15+ sources with average credibility above 60, or 5 minutes elapsed
- `deep`: 25+ sources with average credibility above 70, or 10 minutes elapsed
- `ultradeep`: 30+ sources with average credibility above 75, or 15 minutes elapsed

If the threshold is reached early, let remaining searches finish in the background and use the extra evidence in synthesis.

### Retrieval Quality Standards

- Maintain source diversity across source types and viewpoints.
- Mix recent sources with foundational background when needed.
- Flag low-credibility sources for extra scrutiny.
- Prioritize primary sources, official docs, and direct data when available.

**Output:** Organized evidence set with metadata, source types, credibility signals, and gaps to resolve.

## Phase 4: Triangulate

**Objective:** Validate important claims across independent sources.

**Activities:**
1. Identify claims that need verification.
2. Cross-reference facts across 3 or more independent sources.
3. Flag contradictions and uncertainty.
4. Assess source credibility and bias.
5. Separate consensus areas from debate areas.

**Output:** Verified fact base with confidence levels and contradiction notes.

## Phase 4.5: Outline Refinement

**Objective:** Adapt the report structure when the evidence points somewhere more important than the initial outline.

**Use when:**

- a major finding contradicts initial assumptions
- a critical subtopic emerges during retrieval
- the original scope was too broad or too narrow
- the evidence consistently emphasizes a different center of gravity

**Rules:**

- Changes must be evidence-driven.
- Do not drift away from the original research question.
- Do not create new sections without supporting evidence already in hand.
- If refinement exposes major gaps, run a short targeted retrieval pass instead of restarting Phase 3.

**Output:** Refined outline plus a short rationale for what changed and why.

## Phase 5: Synthesize

**Objective:** Convert verified evidence into structured understanding.

**Activities:**
1. Identify patterns across sources.
2. Map relationships between concepts.
3. Distinguish facts from synthesis.
4. Build evidence-backed conclusions.
5. Develop decision-relevant insights.

**Output:** Synthesized understanding with clear implications and supporting evidence.

## Phase 6: Critique

**Objective:** Stress-test the work before delivery.

**Questions to ask:**

- What could be wrong?
- What evidence is missing?
- Which claims are weakest?
- What alternative interpretations fit the evidence?
- Where could bias have entered the process?

**Output:** Critique notes with concrete improvements to make.

## Phase 7: Refine

**Objective:** Strengthen the report after critique.

**Activities:**
1. Fill important gaps.
2. Strengthen weak arguments.
3. Add missing perspectives.
4. Resolve contradictions where possible.
5. Tighten the writing and citations.

**Output:** Stronger report with deficiencies addressed or explicitly documented.

## Phase 8: Package

**Objective:** Deliver a complete, usable research artifact set.

At this stage:

1. Use [Report Template](../templates/report_template.md) for the document shape.
2. Follow [Reporting and Delivery](./reporting.md) for file paths, assembly, and HTML/PDF generation.
3. Follow [Quality and Validation](./quality.md) for bibliography rules, writing standards, and final checks.
4. Run citation verification and report validation before delivery.

**Output:** Validated research package ready to hand to the user.

## Advanced Features

### Graph-of-Thoughts Reasoning

Use branching reasoning when a single framing is too narrow. Explore multiple plausible angles, then converge once the evidence makes one structure dominant.

### Parallel Agent Deployment

Use sub-agents for independent deep dives, especially when retrieval or synthesis would benefit from isolated context windows.

### Adaptive Depth Control

Adjust depth based on topic complexity, source availability, uncertainty, and the stakes of the decision.

### Citation Intelligence

Track provenance for every major claim, assess source credibility, and preserve bibliography completeness throughout the report-writing process.
