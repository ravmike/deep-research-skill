# Deep Research Skill for Claude Code

A comprehensive research engine that brings Claude Desktop's Advanced Research capabilities (and more) to Claude Code terminal.

## Features

### Core Research Pipeline
- **8.5-Phase Research Pipeline**: Scope → Plan → Retrieve (Parallel) → Triangulate → **Outline Refinement** → Synthesize → Critique → Refine → Package
- **Multiple Research Modes**: Quick, Standard, Deep, and UltraDeep
- **Graph-of-Thoughts Reasoning**: Non-linear exploration with branching thought paths

### 2025 Enhancements (Latest - v2.2)
- **🔄 Auto-Continuation System (NEW)**: **TRUE UNLIMITED length** (50K, 100K+ words) via recursive agent spawning with context preservation
- **📄 Progressive File Assembly**: Section-by-section generation with quality safeguards
- **⚡ Parallel Search Execution**: 5-10 concurrent searches + parallel agents (3-5x faster Phase 3)
- **🎯 First Finish Search (FFS) Pattern**: Adaptive completion based on quality thresholds
- **🔍 Enhanced Citation Validation (CiteGuard)**: Hallucination detection, URL verification, multi-source cross-checking
- **📋 Dynamic Outline Evolution (WebWeaver)**: Adapt structure after Phase 4 based on evidence
- **🔗 Attribution Gradients UI**: Interactive citation tooltips showing evidence chains in HTML reports
- **🛡️ Anti-Fatigue Enforcement**: Prose-first quality checks prevent bullet-point degradation

### Traditional Strengths
- **Citation Management**: Automatic source tracking and bibliography generation
- **Source Credibility Assessment**: Evaluates source quality and potential biases
- **Structured Reports**: Professional markdown, HTML (McKinsey-style), and PDF outputs
- **Verification & Triangulation**: Cross-references claims across multiple sources

## Installation

Package the runtime skill files, then install the packaged output into Codex:

```bash
# Build the minimal export directory
conda run -n codex python tools/package_skill.py

# Optional: also create dist/deep-research.zip for GUI import
conda run -n codex python tools/package_skill.py --zip
```

The packager intentionally exports only the runtime skill package:

- `SKILL.md`
- `agents/`
- `reference/`
- `scripts/`
- `templates/`
- `requirements.txt`

It does not ship repo-only material such as `README.md`, `QUICK_START.md`, audits, or architecture notes.

To install into Codex from the packaged directory:

```bash
rm -rf ~/.codex/skills/deep-research
cp -R dist/deep-research ~/.codex/skills/deep-research
```

For GUI-style import, use `dist/deep-research.zip`.

No third-party Python packages are required for the skill's own runtime scripts.

## Usage

### In Claude Code

Simply invoke the skill:

```
Use deep research to analyze the state of quantum computing in 2025
```

Or specify a mode:

```
Use deep research in ultradeep mode to compare PostgreSQL vs Supabase
```

### Direct CLI Usage

```bash
# Standard research
python ~/.codex/skills/deep-research/scripts/research_engine.py --query "Your research question" --mode standard

# Deep research (all 8 phases)
python ~/.codex/skills/deep-research/scripts/research_engine.py --query "Your research question" --mode deep

# Quick research (3 phases only)
python ~/.codex/skills/deep-research/scripts/research_engine.py --query "Your research question" --mode quick

# Ultra-deep research (extended iterations)
python ~/.codex/skills/deep-research/scripts/research_engine.py --query "Your research question" --mode ultradeep
```

## Research Modes

| Mode | Phases | Duration | Best For |
|------|--------|----------|----------|
| **Quick** | 3 phases | 2-5 min | Simple topics, initial exploration |
| **Standard** | 6 phases | 5-10 min | Most research questions |
| **Deep** | 8 phases | 10-20 min | Complex topics requiring thorough analysis |
| **UltraDeep** | 8+ phases | 20-45 min | Critical decisions, comprehensive reports |

## Output

Research reports are saved to organized folders in `~/Documents/[Topic]_Research_[Date]/`

Each report includes:
- Executive Summary
- Detailed Analysis with Citations
- Synthesis & Insights
- Limitations & Caveats
- Recommendations
- Full Bibliography
- Methodology Appendix

### Unlimited Report Generation (2025 Auto-Continuation System)

Reports use **progressive file assembly with auto-continuation** - achieving truly unlimited length through recursive agent spawning:

**How It Works:**

1. **Initial Generation (18K words)**
   - Generate sections 1-10 progressively
   - Each section written to file immediately (stays under 32K limit per agent)
   - Save continuation state with research context

2. **Auto-Continuation (if needed)**
   - Automatically spawns continuation agent via Task tool
   - Continuation agent loads state: themes, narrative arc, citations, quality metrics
   - Generates next batch of sections (another 18K words)
   - Updates state and spawns next agent if more sections remain

3. **Recursive Chaining**
   - Each agent stays under 32K output token limit
   - Chain continues until all sections complete
   - Final agent generates bibliography and validates report

**Realistic Report Sizes:**
- **Quick mode**: 2,000-4,000 words (single run) ✅
- **Standard mode**: 4,000-8,000 words (single run) ✅
- **Deep mode**: 8,000-15,000 words (single run) ✅
- **UltraDeep mode**: 20,000-100,000+ words (auto-continuation) ✅

**Example: 50,000 word report:**
- Agent 1: Sections 1-10 (18K words) → Spawns Agent 2
- Agent 2: Sections 11-20 (18K words) → Spawns Agent 3
- Agent 3: Sections 21-25 + Bibliography (14K words) → Complete!
- Total: 50K words across 3 agents, each under 32K limit

**Context Preservation (Quality Safeguards):**

Continuation state includes:
- ✅ Research question and key themes
- ✅ Main findings summaries (100 words each)
- ✅ Narrative arc position (beginning/middle/end)
- ✅ Quality metrics (avg words, citation density, prose ratio)
- ✅ All citations used + bibliography entries
- ✅ Writing style characteristics

Each continuation agent:
- Reads last 3 sections to understand flow
- Maintains established themes and style
- Continues citation numbering correctly
- Matches quality metrics (±20% tolerance)
- Verifies coherence before each section

**Quality Gates (Per Section):**
- [ ] Word count: Within ±20% of average
- [ ] Citation density: Matches established rate
- [ ] Prose ratio: ≥80% prose (not bullets)
- [ ] Theme alignment: Ties to key themes
- [ ] Style consistency: Matches established patterns

**Benefits:**
- ✅ TRUE unlimited length (50K, 100K+ words achievable)
- ✅ Fully automatic (no manual intervention)
- ✅ Context preserved across continuations
- ✅ Quality maintained throughout
- ✅ Each agent stays under 32K token limit
- ✅ Progressive assembly prevents truncation

## Examples

### Technology Analysis
```
Use deep research to evaluate whether we should adopt Next.js 15 for our project
```

### Market Research
```
Use deep research to analyze longevity biotech funding trends 2023-2025
```

### Technical Decision
```
Use deep research to compare authentication solutions: Auth0 vs Clerk vs Supabase Auth
```

### Scientific Review
```
Use deep research in ultradeep mode to summarize recent advances in senolytic therapies
```

## Quality Standards

Every research output:
- ✅ Minimum 10+ distinct sources
- ✅ Citations for all major claims
- ✅ Cross-verified facts (3+ sources)
- ✅ Executive summary under 250 words
- ✅ Limitations section
- ✅ Full bibliography
- ✅ Methodology documentation

## Architecture

```
deep-research/
├── SKILL.md                    # Main skill definition
├── research_engine.py          # Core orchestration engine
├── utils/
│   ├── citation_manager.py    # Citation tracking & bibliography
│   └── source_evaluator.py    # Source credibility assessment
├── requirements.txt
└── README.md
```

## Tips for Best Results

1. **Be Specific**: Frame questions clearly with context
2. **Set Expectations**: Specify if you need comparisons, recommendations, or pure analysis
3. **Choose Appropriate Mode**: Use Quick for exploration, Deep for decisions
4. **Review Scope**: Check Phase 1 output to ensure research is on track
5. **Leverage Citations**: Use citation numbers to drill deeper into specific sources

## Comparison with Claude Desktop Research

| Feature | Claude Desktop | Deep Research Skill |
|---------|---------------|---------------------|
| Multi-source synthesis | ✅ | ✅ |
| Citation tracking | ✅ | ✅ |
| Iterative refinement | ✅ | ✅ |
| Source verification | ✅ | ✅ Enhanced |
| Credibility scoring | ❌ | ✅ |
| 8-phase methodology | ❌ | ✅ |
| Graph-of-Thoughts | ❌ | ✅ |
| Multiple modes | ❌ | ✅ |
| Local file integration | ❌ | ✅ |
| Code execution | ❌ | ✅ |

## 2025 Research Papers Implemented

This skill now incorporates cutting-edge techniques from 2025 academic research:

1. **Parallel Execution** (GAP, Flash-Searcher, TPS-Bench)
   - DAG-based parallel tool use for independent subtasks
   - 3-5x faster retrieval phase
   - Concurrent search strategies

2. **First Finish Search** (arXiv 2505.18149)
   - Quality threshold gates by mode
   - Continue background searches for depth
   - Optimal latency-accuracy tradeoff

3. **Citation Validation** (CiteGuard, arXiv 2510.17853)
   - Hallucination pattern detection
   - Multi-source verification (DOI + URL)
   - Strict mode for critical reports

4. **Dynamic Outlines** (WebWeaver, arXiv 2509.13312)
   - Evidence-driven structure adaptation
   - Phase 4.5 refinement step
   - Prevents locked-in research paths

5. **Attribution Gradients** (arXiv 2510.00361)
   - Interactive evidence chains
   - Hover tooltips in HTML reports
   - Improved auditability

## Version

2.0 (2025-11-05) - Major update with 2025 research enhancements
1.0 (2025-11-04) - Initial release

## License

User skill - modify as needed for your workflow
