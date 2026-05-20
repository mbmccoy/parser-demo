#!/usr/bin/env python3
"""Two-regex toy baseline. Intentionally not a real SQL parser."""

import argparse, json, re
from collections import OrderedDict
from pathlib import Path

CREATE_TABLE = re.compile(
    r"\bcreate\s+(?:temp(?:orary)?\s+)?table\s+(?:if\s+not\s+exists\s+)?"
    r'(?P<table>"[^"]+"|`[^`]+`|\[[^\]]+\]|\w+)\s*\((?P<body>.*?)\)\s*;',
    re.I | re.S,
)
CHECK = re.compile(
    r'(?:(?P<col>"[^"]+"|`[^`]+`|\[[^\]]+\]|\w+)[^,]*?)?'
    r'(?P<check>(?:constraint\s+(?:"[^"]+"|`[^`]+`|\[[^\]]+\]|\w+)\s+)?'
    r"check\s*\((?:'[^']*'|[^)])*\))",
    re.I | re.S,
)

def parse_sql(sql):
    out = OrderedDict()
    for table in CREATE_TABLE.finditer(sql):
        checks = OrderedDict()
        for match in CHECK.finditer(table.group("body")):
            col = match.group("col")
            if col:
                col = col[1:-1] if col[:1] in '"`[' else col
                checks.setdefault(col, []).append(" ".join(match.group("check").split()))
        name = table.group("table")
        out[name[1:-1] if name[:1] in '"`[' else name] = checks
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("schema", nargs="+", type=Path)
    print(json.dumps(parse_sql("\n".join(p.read_text() for p in parser.parse_args().schema)), indent=2))
