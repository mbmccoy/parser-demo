#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["antlr4-python3-runtime==4.9.3"]
# ///
"""Compare ANTLR and regex CHECK-column parser output for schema files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from check_columns import parse_sql as parse_antlr
from check_columns_regex import parse_sql as parse_regex


def as_json(value) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def compare_file(path: Path) -> bool:
    sql = path.read_text(encoding="utf-8")
    antlr = parse_antlr(sql)
    regex = parse_regex(sql)
    matches = antlr == regex

    print(f"{path}: {'MATCH' if matches else 'DIFF'}")
    if not matches:
        print("  ANTLR:")
        print("\n".join(f"    {line}" for line in as_json(antlr).splitlines()))
        print("  REGEX:")
        print("\n".join(f"    {line}" for line in as_json(regex).splitlines()))
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare check_columns.py and check_columns_regex.py output."
    )
    parser.add_argument(
        "schemas",
        nargs="*",
        type=Path,
        default=sorted(Path("comparison_schemas").glob("*.sql")),
        help="Schema files to compare. Defaults to comparison_schemas/*.sql.",
    )
    args = parser.parse_args()

    results = [compare_file(path) for path in args.schemas]
    matched = sum(results)
    total = len(results)
    print(f"\nSummary: {matched}/{total} files matched.")
    return 0 if matched == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
