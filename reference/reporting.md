# Reporting and Delivery

## Contents

- Output locations
- Required artifacts
- Report structure
- Assembly workflow
- Continuation protocol
- HTML and PDF packaging
- Delivery checklist

## Output Locations

Prefer a workspace-relative output folder when running inside a repo or workspace:

- Pattern: `./research_output/[topic_slug]_[YYYYMMDD]/`
- Use a clean topic slug derived from the question.
- Reuse the folder if it already exists.

Only fall back to a home-directory location if no writable workspace context exists.

Use one base filename across all artifacts:

- `research_report_[YYYYMMDD]_[topic_slug].md`
- `research_report_[YYYYMMDD]_[topic_slug].html`
- `research_report_[YYYYMMDD]_[topic_slug].pdf`

## Required Artifacts

The delivery target is a matched artifact set:

1. Markdown as the source of truth.
2. HTML generated from the markdown report.
3. PDF when the environment has a working PDF path.

If PDF generation is unavailable, deliver markdown and HTML and state the limitation clearly instead of failing silently.

## Report Structure

Use [Report Template](../templates/report_template.md) exactly.

Required sections:

- Executive Summary
- Introduction
- Main Analysis
- Synthesis and Insights
- Limitations and Caveats
- Recommendations
- Bibliography
- Appendix: Methodology

Expected depth by mode:

- `quick`: about 2,000-4,000 words
- `standard`: about 4,000-8,000 words
- `deep`: about 8,000-15,000 words
- `ultradeep`: as long as needed, but manage output in sections

Do not replace analysis with placeholders, ellipses, or "content continues" markers.

## Assembly Workflow

Generate the report section by section so the file can grow without forcing one oversized response.

Recommended flow:

1. Create the markdown file and write the title plus executive summary.
2. Append each major section individually.
3. Maintain a running list of citations used.
4. Generate the bibliography only after all body citations are known.
5. Append the methodology appendix last.

While assembling:

- keep each generation chunk focused on one section
- preserve numbering and citation continuity
- prefer prose paragraphs over bullet-heavy dumping
- keep findings evidence-rich and specific

## Continuation Protocol

If the report is likely to exceed a comfortable single-run output budget, continue in batches instead of compressing content.

Continuation state should preserve:

- report id
- file path
- mode
- completed sections
- citations already used
- next citation number
- summaries of completed findings
- current narrative arc
- next sections to generate
- quality metrics such as average section length and citation density

When resuming:

1. Read the continuation state.
2. Read the existing report, especially the last few sections.
3. Continue with the next section batch.
4. Update the state after each batch.
5. On the final batch, generate the full bibliography, run validation, and clean up the continuation state.

## HTML and PDF Packaging

### HTML

Use `scripts/build_report.py` as the canonical packaging step.

`scripts/md_to_html.py` is an internal fragment converter used by the builder. Do not hand-assemble HTML around it unless you are debugging the builder itself.

Always:

- preserve citation markers
- include 3-4 dashboard metrics derived from the report or passed in intentionally
- verify the final HTML with `scripts/verify_html.py`

Suggested flow:

```bash
python scripts/build_report.py [markdown_report_path]
python scripts/verify_html.py --html [html_path] --md [md_path]
```

Open the HTML file after generation if the environment supports it.

### PDF

Generate a PDF from the markdown or HTML artifact only if the current environment has a tested export path.

If a dedicated PDF skill or export path exists and has been tested in the current environment, use it. If not, report that PDF generation could not be completed and still deliver the validated markdown and HTML artifacts.

## Delivery Checklist

Before handing off:

- markdown exists at the final path
- HTML exists and passes `verify_html.py`
- PDF exists, or its absence is explicitly reported
- citation verification passes directly or unresolved failures are classified and documented
- report validation passes
- artifact folder path is included in the user-facing response
- source count and any important limitations are summarized in the response
