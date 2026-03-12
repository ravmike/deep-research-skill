#!/usr/bin/env python3
"""
Citation verification for deep-research reports.

Checks citations by combining:
1. DOI metadata resolution
2. URL accessibility checks with HEAD -> GET fallback
3. Basic metadata matching
4. Hallucination-pattern detection

This verifier is intentionally conservative about failed access:
- it distinguishes network problems from publisher blocking
- it treats GET success after HEAD failure as verified
- it reports failure categories so the caller can decide whether to
  swap in an alternate URL such as PubMed or PMC
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib import error, request
from urllib.parse import quote, urlparse


USER_AGENT = "Mozilla/5.0 (Deep Research Citation Verifier)"
RECOVERABLE_HEAD_CODES = {403, 405}
SUCCESS_CODES = set(range(200, 400))


@dataclass
class VerificationResult:
    num: str
    status: str = "unknown"
    category: str = "unknown"
    issues: List[str] = field(default_factory=list)
    verification_methods: List[str] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)


class CitationVerifier:
    """Verify bibliography entries in a markdown research report."""

    def __init__(self, report_path: Path, strict_mode: bool = False):
        self.report_path = report_path
        self.strict_mode = strict_mode
        self.content = self._read_report()
        self.current_year = datetime.now().year
        self.suspicious_patterns = [
            (
                r"^(A |An |The )?(Study|Analysis|Review|Survey|Investigation) (of|on|into)",
                "Generic academic title pattern",
            ),
            (
                r"^(Recent|Current|Modern|Contemporary) (Advances|Developments|Trends) in",
                "Generic 'advances' title pattern",
            ),
            (
                r"^[A-Z][a-z]+ [A-Z][a-z]+: A (Comprehensive|Complete|Systematic) (Review|Analysis|Guide)$",
                "Too perfect, templated structure",
            ),
        ]

    def _read_report(self) -> str:
        try:
            return self.report_path.read_text(encoding="utf-8")
        except Exception as exc:
            print(f"ERROR: cannot read report: {exc}")
            sys.exit(1)

    def extract_bibliography(self) -> List[Dict[str, Optional[str]]]:
        pattern = r"## Bibliography(.*?)(?=##|\Z)"
        match = re.search(pattern, self.content, re.DOTALL | re.IGNORECASE)
        if not match:
            return []

        entries: List[Dict[str, Optional[str]]] = []
        current_entry: Optional[Dict[str, Optional[str]]] = None

        for raw_line in match.group(1).strip().splitlines():
            line = raw_line.strip()
            if not line:
                continue

            match_num = re.match(r"^\[(\d+)\]\s+(.+)$", line)
            if match_num:
                if current_entry:
                    entries.append(current_entry)

                num = match_num.group(1)
                rest = match_num.group(2)
                year_match = re.search(r"\((\d{4})\)", rest)
                title_match = re.search(r'"([^"]+)"', rest)
                doi_match = re.search(r"(?:doi\.org/|doi:\s*)(10\.\S+?)(?:\s|$)", rest, re.IGNORECASE)
                url_match = re.search(r"https?://[^\s\)]+", rest)
                current_entry = {
                    "num": num,
                    "raw": rest,
                    "year": year_match.group(1) if year_match else None,
                    "title": title_match.group(1) if title_match else None,
                    "doi": doi_match.group(1).rstrip(").,") if doi_match else None,
                    "url": url_match.group(0).rstrip(").,") if url_match else None,
                }
            elif current_entry:
                current_entry["raw"] = f"{current_entry['raw']} {line}"

        if current_entry:
            entries.append(current_entry)

        return entries

    def verify_doi(self, doi: str) -> Tuple[bool, Dict[str, object]]:
        if not doi:
            return False, {}

        try:
            req = request.Request(f"https://doi.org/{quote(doi)}")
            req.add_header("Accept", "application/vnd.citationstyles.csl+json")
            req.add_header("User-Agent", USER_AGENT)
            with request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
            return True, {
                "title": data.get("title", ""),
                "year": data.get("issued", {}).get("date-parts", [[None]])[0][0],
                "authors": [
                    f"{author.get('family', '')} {author.get('given', '')}".strip()
                    for author in data.get("author", [])
                ],
                "venue": data.get("container-title", ""),
            }
        except error.HTTPError as exc:
            category = "doi_not_found" if exc.code == 404 else "doi_http_error"
            return False, {"error": f"HTTP {exc.code}", "category": category}
        except error.URLError as exc:
            return False, {"error": str(exc.reason), "category": "network_error"}
        except Exception as exc:
            return False, {"error": str(exc), "category": "unknown_error"}

    def _open_url(self, url: str, method: str) -> Tuple[bool, Dict[str, object]]:
        req = request.Request(url, method=method)
        req.add_header("User-Agent", USER_AGENT)

        try:
            with request.urlopen(req, timeout=15) as response:
                return True, {
                    "status_code": response.status,
                    "final_url": response.geturl(),
                    "method": method,
                    "category": "ok",
                }
        except error.HTTPError as exc:
            return False, {
                "status_code": exc.code,
                "final_url": url,
                "method": method,
                "category": self._categorize_http_failure(exc.code),
                "error": f"HTTP {exc.code}",
            }
        except error.URLError as exc:
            return False, {
                "status_code": None,
                "final_url": url,
                "method": method,
                "category": "network_error",
                "error": f"URL error: {exc.reason}",
            }
        except Exception as exc:
            return False, {
                "status_code": None,
                "final_url": url,
                "method": method,
                "category": "unknown_error",
                "error": f"Connection error: {str(exc)[:80]}",
            }

    def _categorize_http_failure(self, status_code: int) -> str:
        if status_code == 401:
            return "auth_required"
        if status_code == 403:
            return "publisher_blocked"
        if status_code == 404:
            return "not_found"
        if status_code == 405:
            return "method_not_allowed"
        if 500 <= status_code <= 599:
            return "server_error"
        return "http_error"

    def verify_url(self, url: str) -> Tuple[bool, Dict[str, object]]:
        if not url:
            return False, {"category": "no_url", "error": "No URL"}

        head_ok, head_result = self._open_url(url, "HEAD")
        if head_ok and head_result["status_code"] in SUCCESS_CODES:
            head_result["verification_method"] = "HEAD"
            return True, head_result

        if head_result.get("status_code") in RECOVERABLE_HEAD_CODES:
            get_ok, get_result = self._open_url(url, "GET")
            if get_ok and get_result["status_code"] in SUCCESS_CODES:
                get_result["verification_method"] = "GET"
                get_result["category"] = "ok_after_head_failure"
                get_result["head_error"] = head_result.get("error")
                return True, get_result
            return False, get_result

        return False, head_result

    def detect_hallucination_patterns(self, entry: Dict[str, Optional[str]]) -> List[str]:
        issues: List[str] = []
        title = entry.get("title") or ""
        if not title:
            return issues

        for pattern, description in self.suspicious_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                issues.append(f"Suspicious title pattern: {description}")

        generic_words = ["overview", "introduction", "guide", "handbook", "manual"]
        if any(word in title.lower() for word in generic_words) and len(title.split()) < 5:
            issues.append("Very generic short title")

        if any(word in title.lower() for word in ["tbd", "todo", "placeholder", "example"]):
            issues.append("Placeholder text in title")

        year = entry.get("year")
        if year:
            year_int = int(year)
            if year_int >= self.current_year - 1 and not entry.get("doi") and not entry.get("url"):
                issues.append("Recent year with no DOI or URL")
            if year_int > self.current_year:
                issues.append(f"Future year: {year_int}")
            if year_int < 2000 and any(term in title.lower() for term in ["ai", "llm", "gpt", "transformer"]):
                issues.append(f"Anachronistic title for year {year_int}")

        return issues

    def check_title_similarity(self, title1: str, title2: str) -> float:
        def normalize(value: str) -> set[str]:
            lowered = re.sub(r"[^\w\s]", " ", value.lower())
            return set(lowered.split())

        words1 = normalize(title1)
        words2 = normalize(title2)
        if not words1 or not words2:
            return 0.0
        return len(words1 & words2) / len(words1 | words2)

    def verify_entry(self, entry: Dict[str, Optional[str]]) -> VerificationResult:
        result = VerificationResult(num=entry["num"] or "?", category="unverified", status="unverified")

        hallucination_issues = self.detect_hallucination_patterns(entry)
        if hallucination_issues:
            result.issues.extend(hallucination_issues)
            result.status = "suspicious"
            result.category = "metadata_warning"

        doi = entry.get("doi")
        if doi:
            print(f"  [{result.num}] Checking DOI {doi}...", end=" ")
            doi_ok, metadata = self.verify_doi(doi)
            if doi_ok:
                result.metadata = metadata
                result.status = "verified"
                result.category = "doi_verified"
                result.verification_methods.append("DOI")
                print("OK")

                if entry.get("title") and metadata.get("title"):
                    similarity = self.check_title_similarity(entry["title"] or "", str(metadata["title"]))
                    if similarity < 0.5:
                        result.issues.append(f"Title mismatch (similarity {similarity:.1%})")
                        result.status = "suspicious"
                        result.category = "metadata_mismatch"

                if entry.get("year") and metadata.get("year"):
                    if int(entry["year"]) != int(metadata["year"]):
                        result.issues.append(
                            f"Year mismatch: report says {entry['year']}, DOI says {metadata['year']}"
                        )
                        result.status = "suspicious"
                        result.category = "metadata_mismatch"
            else:
                print(f"FAILED ({metadata.get('error', 'unknown error')})")
                result.issues.append(f"DOI resolution failed: {metadata.get('error', 'unknown error')}")
                result.category = str(metadata.get("category", "doi_error"))

        url = entry.get("url")
        if url and result.status != "verified":
            url_ok, url_result = self.verify_url(url)
            if url_ok:
                method = str(url_result.get("verification_method", url_result.get("method", "URL")))
                result.verification_methods.append(method)
                result.status = "url_verified"
                result.category = str(url_result.get("category", "url_verified"))
                final_url = str(url_result.get("final_url", url))
                print(f"  [{result.num}] URL accessible via {method} ({final_url})")
            else:
                category = str(url_result.get("category", "url_error"))
                detail = str(url_result.get("error", "unknown error"))
                result.issues.append(f"URL check failed [{category}]: {detail}")
                result.category = category

        if not doi and not url:
            result.status = "suspicious"
            result.category = "no_verification_path"
            result.issues.append("No DOI or URL provided")

        return result

    def verify_all(self) -> bool:
        print(f"\n{'=' * 60}")
        print(f"CITATION VERIFICATION: {self.report_path.name}")
        print(f"{'=' * 60}\n")

        entries = self.extract_bibliography()
        if not entries:
            print("ERROR: no bibliography entries found")
            return False

        print(f"Found {len(entries)} citations\n")

        results: List[VerificationResult] = []
        for entry in entries:
            results.append(self.verify_entry(entry))
            time.sleep(0.1)

        doi_verified = [result for result in results if result.category == "doi_verified"]
        url_verified = [result for result in results if result.status == "url_verified"]
        suspicious = [result for result in results if result.status == "suspicious"]
        unverified = [result for result in results if result.status == "unverified"]

        print(f"\n{'=' * 60}")
        print("VERIFICATION SUMMARY")
        print(f"{'=' * 60}\n")
        print(f"DOI Verified: {len(doi_verified)}/{len(results)}")
        print(f"URL Verified: {len(url_verified)}/{len(results)}")
        print(f"Suspicious: {len(suspicious)}/{len(results)}")
        print(f"Unverified: {len(unverified)}/{len(results)}")
        print()

        if suspicious:
            print("SUSPICIOUS CITATIONS (manual review recommended):")
            for result in suspicious:
                print(f"  [{result.num}] {result.category}")
                for issue in result.issues:
                    print(f"    - {issue}")
            print()

        if unverified:
            print("UNVERIFIED CITATIONS (structured failure categories):")
            for result in unverified:
                issue = result.issues[0] if result.issues else "No details"
                print(f"  [{result.num}] {result.category}: {issue}")
            print()

        total_verified = len(doi_verified) + len(url_verified)
        verified_fraction = total_verified / len(results)

        if self.strict_mode and (suspicious or unverified):
            print("STRICT MODE: failing due to suspicious or unverified citations")
            return False

        if verified_fraction < 0.5:
            print("WARNING: less than 50% of citations verified directly")
        else:
            print("CITATION VERIFICATION PASSED")

        return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify citations in a markdown report")
    parser.add_argument("--report", "-r", required=True, help="Path to markdown report")
    parser.add_argument("--strict", action="store_true", help="Fail on any suspicious or unverified citation")
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"ERROR: report file not found: {report_path}")
        return 1

    verifier = CitationVerifier(report_path, strict_mode=args.strict)
    return 0 if verifier.verify_all() else 1


if __name__ == "__main__":
    sys.exit(main())
