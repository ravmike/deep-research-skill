#!/usr/bin/env python3
"""
Build a full HTML artifact for a deep-research markdown report.

This is the canonical packaging path for HTML delivery.
"""

from __future__ import annotations

import argparse
import html
import re
from datetime import date
from pathlib import Path
from typing import Tuple

from md_to_html import (
    convert_bibliography_section,
    convert_markdown_fragment_to_html,
    split_markdown_sections,
)


def extract_title(markdown_text: str, fallback: str) -> str:
    match = re.search(r"^# (.+)$", markdown_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return fallback.replace("_", " ").replace("-", " ").title()


def count_sources(markdown_text: str) -> int:
    return len(set(re.findall(r"^\[(\d+)\]", markdown_text, re.MULTILINE)))


def count_citations(markdown_text: str) -> int:
    return len(re.findall(r"\[(\d+)\]", markdown_text))


def count_sections(markdown_text: str) -> int:
    return len(re.findall(r"^## ", markdown_text, re.MULTILINE))


def replace_citation_markers(html_fragment: str) -> str:
    return re.sub(r"\[(\d+)\]", r'<span class="citation">[\1]</span>', html_fragment)


def build_metrics_html(markdown_text: str) -> str:
    source_count = count_sources(markdown_text)
    citation_count = count_citations(markdown_text)
    section_count = count_sections(markdown_text)
    word_count = len(markdown_text.split())

    metrics = [
        (str(source_count), "Sources"),
        (str(citation_count), "Inline Citations"),
        (str(section_count), "Major Sections"),
        (str(word_count), "Words"),
    ]

    cards = []
    for number, label in metrics:
        cards.append(
            f'<div class="metric"><span class="metric-number">{html.escape(number)}</span>'
            f'<span class="metric-label">{html.escape(label)}</span></div>'
        )
    return '<div class="metrics-dashboard">\n' + "\n".join(cards) + "\n</div>"


def build_html(markdown_text: str, template_text: str, report_title: str, report_date: str) -> str:
    pre_bib, bibliography_md, post_bib = split_markdown_sections(markdown_text)
    pre_html = replace_citation_markers(convert_markdown_fragment_to_html(pre_bib)) if pre_bib else ""
    post_html = replace_citation_markers(convert_markdown_fragment_to_html(post_bib)) if post_bib else ""
    bibliography_html = convert_bibliography_section(bibliography_md)

    return (
        template_text.replace("{{TITLE}}", html.escape(report_title))
        .replace("{{DATE}}", html.escape(report_date))
        .replace("{{SOURCE_COUNT}}", str(count_sources(markdown_text)))
        .replace("{{METRICS_DASHBOARD}}", build_metrics_html(markdown_text))
        .replace("{{CONTENT}}", pre_html)
        .replace("{{BIBLIOGRAPHY}}", bibliography_html)
        .replace("{{POST_BIB_CONTENT}}", post_html)
    )


def resolve_output_path(markdown_path: Path, html_path_arg: str | None) -> Path:
    if html_path_arg:
        return Path(html_path_arg)
    return markdown_path.with_suffix(".html")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a full HTML report from markdown")
    parser.add_argument("markdown_report", type=Path, help="Path to markdown report")
    parser.add_argument("--html", help="Optional output HTML path")
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "templates" / "mckinsey_report_template.html",
        help="HTML template path",
    )
    args = parser.parse_args()

    if not args.markdown_report.exists():
        print(f"ERROR: markdown report not found: {args.markdown_report}")
        return 1

    if not args.template.exists():
        print(f"ERROR: template not found: {args.template}")
        return 1

    markdown_text = args.markdown_report.read_text(encoding="utf-8")
    template_text = args.template.read_text(encoding="utf-8")
    report_title = extract_title(markdown_text, args.markdown_report.stem)
    report_date = date.today().isoformat()
    html_output_path = resolve_output_path(args.markdown_report, args.html)

    html_output_path.write_text(
        build_html(markdown_text, template_text, report_title, report_date),
        encoding="utf-8",
    )
    print(html_output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
