#!/usr/bin/env python3
"""
Markdown fragment conversion for deep-research reports.

This module is intentionally a converter, not a report packager.
Use build_report.py to assemble a full HTML artifact with the shared template.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Tuple


def split_markdown_sections(markdown_text: str) -> Tuple[str, str, str]:
    """
    Split a report into:
    - content before bibliography
    - bibliography section body
    - content after bibliography
    """
    lines = markdown_text.splitlines()
    bib_start = None
    bib_end = None

    for index, line in enumerate(lines):
        if line.strip().lower() == "## bibliography":
            bib_start = index
            continue
        if bib_start is not None and line.startswith("## "):
            bib_end = index
            break

    if bib_start is None:
        return markdown_text, "", ""

    if bib_end is None:
        bib_end = len(lines)

    pre = "\n".join(lines[:bib_start]).strip()
    bibliography = "\n".join(lines[bib_start + 1 : bib_end]).strip()
    post = "\n".join(lines[bib_end:]).strip()
    return pre, bibliography, post


def convert_markdown_to_html(markdown_text: str) -> Tuple[str, str]:
    """
    Backward-compatible helper:
    returns body HTML (content before + after bibliography) and bibliography HTML.
    """
    pre, bibliography, post = split_markdown_sections(markdown_text)
    body_parts = [part for part in [pre, post] if part]
    body_html = "\n".join(convert_markdown_fragment_to_html(part) for part in body_parts if part)
    bibliography_html = convert_bibliography_section(bibliography)
    return body_html, bibliography_html


def convert_markdown_fragment_to_html(markdown: str) -> str:
    html = markdown
    html = _strip_preamble_before_first_section(html)

    html = re.sub(
        r"^## (.+)$",
        r'<div class="section"><h2 class="section-title">\1</h2>',
        html,
        flags=re.MULTILINE,
    )
    html = re.sub(
        r"^### (.+)$",
        r'<h3 class="subsection-title">\1</h3>',
        html,
        flags=re.MULTILINE,
    )
    html = re.sub(
        r"^#### (.+)$",
        r'<h4 class="subsubsection-title">\1</h4>',
        html,
        flags=re.MULTILINE,
    )

    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)

    html = _convert_lists(html)
    html = _convert_tables(html)
    html = _convert_paragraphs(html)
    html = _close_sections(html)

    html = html.replace(
        '<h2 class="section-title">Executive Summary</h2>',
        '<div class="executive-summary"><h2 class="section-title">Executive Summary</h2>',
    )
    if '<div class="executive-summary">' in html:
        html = html.replace('</h2>\n<div class="section">', '</h2></div>\n<div class="section">', 1)

    return html


def convert_bibliography_section(markdown: str) -> str:
    if not markdown.strip():
        return ""

    entries = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^\[(\d+)\]\s+(.+)$", line)
        if not match:
            continue
        num, rest = match.groups()
        url_match = re.search(r"(https?://[^\s\)]+)", rest)
        if url_match:
            url = url_match.group(1).rstrip(").,")
            rest_html = rest.replace(url_match.group(1), f'<a href="{url}" target="_blank">{url}</a>')
        else:
            rest_html = rest
        entries.append(f'<div class="bib-entry"><span class="bib-number">[{num}]</span> {rest_html}</div>')

    return "\n".join(entries)


def _strip_preamble_before_first_section(markdown: str) -> str:
    lines = markdown.splitlines()
    processed_lines = []
    skip_until_first_section = True

    for line in lines:
        if skip_until_first_section:
            if line.startswith("## ") and not line.startswith("### "):
                skip_until_first_section = False
                processed_lines.append(line)
            continue
        processed_lines.append(line)

    return "\n".join(processed_lines)


def _convert_lists(html: str) -> str:
    lines = html.split("\n")
    result = []
    in_list = False
    list_tag = "ul"
    list_level = 0

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                list_tag = "ul"
                result.append(f"<{list_tag}>")
                in_list = True
                list_level = len(line) - len(line.lstrip())
            result.append(f"<li>{stripped[2:]}</li>")
            continue

        if re.match(r"^\d+\.\s", stripped):
            if not in_list:
                list_tag = "ol"
                result.append(f"<{list_tag}>")
                in_list = True
                list_level = len(line) - len(line.lstrip())
            result.append(f"<li>{re.sub(r'^\d+\.\s', '', stripped)}</li>")
            continue

        if in_list:
            current_level = len(line) - len(line.lstrip())
            if current_level > list_level and stripped:
                if result[-1].endswith("</li>"):
                    result[-1] = result[-1][:-5] + f" {stripped}</li>"
                continue
            result.append(f"</{list_tag}>")
            in_list = False
            list_level = 0

        result.append(line)

    if in_list:
        result.append(f"</{list_tag}>")

    return "\n".join(result)


def _convert_tables(html: str) -> str:
    lines = html.split("\n")
    result = []
    in_table = False

    for line in lines:
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                in_table = True
                result.append("<table>")
                cells = [cell.strip() for cell in line.split("|")[1:-1]]
                result.append("<thead><tr>")
                for cell in cells:
                    result.append(f"<th>{cell}</th>")
                result.append("</tr></thead>")
                result.append("<tbody>")
            elif "---" in line:
                continue
            else:
                cells = [cell.strip() for cell in line.split("|")[1:-1]]
                result.append("<tr>")
                for cell in cells:
                    result.append(f"<td>{cell}</td>")
                result.append("</tr>")
            continue

        if in_table:
            result.append("</tbody></table>")
            in_table = False

        result.append(line)

    if in_table:
        result.append("</tbody></table>")

    return "\n".join(result)


def _convert_paragraphs(html: str) -> str:
    lines = html.split("\n")
    result = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_paragraph:
                result.append("</p>")
                in_paragraph = False
            result.append(line)
            continue

        if (
            (stripped.startswith("<") and stripped.endswith(">"))
            or stripped.startswith("</")
            or "<h" in stripped
            or "<div" in stripped
            or "<ul" in stripped
            or "<ol" in stripped
            or "<li" in stripped
            or "<table" in stripped
            or "</div>" in stripped
            or "</ul>" in stripped
            or "</ol>" in stripped
        ):
            if in_paragraph:
                result.append("</p>")
                in_paragraph = False
            result.append(line)
            continue

        if not in_paragraph:
            result.append(f"<p>{line}")
            in_paragraph = True
        else:
            result.append(line)

    if in_paragraph:
        result.append("</p>")

    return "\n".join(result)


def _close_sections(html: str) -> str:
    lines = html.split("\n")
    result = []
    section_open = False

    for line in lines:
        if '<div class="section">' in line:
            if section_open:
                result.append("</div>")
            section_open = True
        result.append(line)

    if section_open:
        result.append("</div>")

    return "\n".join(result)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert markdown fragments for deep-research reports. Use build_report.py for full HTML output."
    )
    parser.add_argument("markdown_file", type=Path, help="Path to markdown report")
    args = parser.parse_args()

    if not args.markdown_file.exists():
        print(f"ERROR: file not found: {args.markdown_file}")
        return 1

    markdown_text = args.markdown_file.read_text(encoding="utf-8")
    body_html, bibliography_html = convert_markdown_to_html(markdown_text)
    print(f"Body fragment length: {len(body_html)}")
    print(f"Bibliography fragment length: {len(bibliography_html)}")
    print("Use build_report.py to generate the full HTML artifact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
