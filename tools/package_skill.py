#!/usr/bin/env python3
"""
Build a minimal distributable deep-research skill package.

Default:
    Create dist/deep-research/

Optional:
    Add --zip to also create dist/deep-research.zip
"""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


PACKAGE_NAME = "deep-research"
EXPORT_ITEMS = (
    "SKILL.md",
    "agents",
    "reference",
    "scripts",
    "templates",
    "requirements.txt",
)
IGNORE_PATTERNS = shutil.ignore_patterns(
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def validate_inputs(root: Path) -> None:
    missing = [item for item in EXPORT_ITEMS if not (root / item).exists()]
    if missing:
        missing_str = ", ".join(missing)
        raise SystemExit(f"Missing required package items: {missing_str}")


def build_export(root: Path, export_root: Path) -> Path:
    export_dir = export_root / PACKAGE_NAME

    if export_dir.exists():
        shutil.rmtree(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    for item in EXPORT_ITEMS:
        src = root / item
        dst = export_dir / item
        if src.is_dir():
            shutil.copytree(src, dst, ignore=IGNORE_PATTERNS)
        else:
            shutil.copy2(src, dst)

    return export_dir


def build_zip(export_root: Path, export_dir: Path) -> Path:
    zip_path = export_root / f"{PACKAGE_NAME}.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(export_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(export_root))

    return zip_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a minimal deep-research skill package.",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Also create dist/deep-research.zip for GUI import.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    export_root = root / "dist"

    validate_inputs(root)
    export_dir = build_export(root, export_root)
    print(f"Created export directory: {export_dir}")

    if args.zip:
        zip_path = build_zip(export_root, export_dir)
        print(f"Created archive: {zip_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
