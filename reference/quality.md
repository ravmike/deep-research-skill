# Quality and Validation

## Contents

- Anti-hallucination rules
- Source attribution rules
- Writing standards
- Bibliography requirements
- Stop rules
- Acceptance thresholds
- Inputs and defaults

## Anti-hallucination Rules

Every factual claim must be source-grounded.

Apply these rules throughout the report:

- cite major factual claims inline in the same sentence
- distinguish sourced facts from your synthesis
- label inferences as inferences
- do not imply certainty when the evidence is partial
- say that no source was found when that is the truth

Preferred patterns:

- "According to [1] ..."
- "[1] reports ..."
- "This suggests ..." for analysis built on cited evidence

Avoid vague attributions:

- "Research suggests ..."
- "Studies show ..."
- "Experts believe ..."

## Source Attribution Rules

For important claims:

- use 3 or more independent sources when feasible
- prefer official docs, primary research, direct datasets, and primary reporting
- flag single-source claims as weak or unverified
- note recency when it matters
- note bias or commercial incentives when they may distort the evidence

If sources conflict:

1. state the contradiction plainly
2. identify which sources support each side
3. explain the likely reason for the disagreement if evidence allows
4. do not force a false consensus

## Writing Standards

The default style is dense, direct, and evidence-first prose.

Priorities:

- precision over flourish
- clarity over cleverness
- signal over volume
- narrative flow over bullet fatigue

Use bullets only for genuinely list-shaped content such as product lists, steps, or option sets. The report body should be primarily paragraphs.

Good phrasing:

- "The market reached $2.4 billion in 2023, driven by consumer demand [1]."
- "Five randomized trials covering 1,847 participants found ..."
- "This suggests the main operational bottleneck is deployment complexity."

Weak phrasing:

- "The market is huge."
- "Several studies suggest improvement."
- "Experts generally believe ..."

## Bibliography Requirements

The bibliography is mandatory and must be complete.

Rules:

- every citation used in the report body must appear in the bibliography
- write entries individually; do not collapse them into ranges
- include enough metadata to identify and revisit the source
- do not use placeholders such as "additional citations omitted"

Expected entry pattern:

`[N] Author or Organization (Year). "Title". Publication or Site. URL (Retrieved: Date)`

Run this before delivery:

```bash
python scripts/verify_citations.py --report [path]
```

## Stop Rules

Stop and report the issue when:

- the same validation failure persists after two fixes
- fewer than 5 usable sources remain after exhaustive retrieval
- the user changes scope midstream in a way that invalidates the current report
- a key claim cannot be verified and materially affects the conclusion

When stopping, report:

- the issue
- what was attempted
- what remains blocked
- the best next options

## Acceptance Thresholds

Every report should meet these thresholds unless the limitation is explicitly documented:

- 10 or more sources for standard research
- 3 or more sources behind major claims
- executive summary under 250 words
- limitations section present
- methodology appendix present
- no placeholders
- citations and bibliography are consistent

Run this before delivery:

```bash
python scripts/validate_report.py --report [path]
```

## Inputs and Defaults

Required input:

- research question

Optional inputs:

- mode
- time constraint
- required perspectives
- source preferences
- output format constraints

Default assumptions:

- `standard` mode unless the task clearly warrants more or less depth
- recent developments matter for trend or market questions
- technical audiences prefer direct terminology and evidence density
- verification quality takes priority over speed
