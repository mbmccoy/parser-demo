# parser-demo

ANTLR-based parsers are easy for LLMs to write and far more robust than the regex-based parsers they reach for by default. Here, I've had LLMs make two implementations of the same task — report which columns in a SQLite schema are covered by `CHECK` constraints.

| File | Approach |
|------|----------|
| `check_columns.py` | ANTLR4 — real SQLite parse tree |
| `check_columns_regex.py` | Two regexes — the kind an LLM writes first |

The two regexes themselves are pretty gnarly, but do work for fairly simple settings:

```python
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
```

Running the comparison:

```bash
uv run compare_parsers.py
```

The result: **0/8 schema files match.** The regex version fails on nested parentheses, table-level constraints, quoted identifiers, string literals with SQL inside, and comments.

## Why ANTLR

- Grammars for [300+ languages](https://github.com/antlr/grammars-v4) are already written — vendor the `.g4` files and generate the parser once
- Generated parser files are checked in (`generated/grammar/`); production only needs the small Python runtime
- The parser reads the full SQL file and the visitor ignores non-`CREATE TABLE` statements; the vendored SQLite grammar has a tiny PRAGMA-value patch so common setup like `PRAGMA foreign_keys = ON;` parses cleanly
- An LLM can write the visitor glue code in minutes; the code is robust and easily maintained by both LLMs and humans. 

## Setup

```bash
uv run check_columns.py schema.sql
```

## Regenerating the parser

```bash
curl -L https://www.antlr.org/download/antlr-4.9.3-complete.jar -o /tmp/antlr-4.9.3-complete.jar
rm -rf generated/grammar
java -jar /tmp/antlr-4.9.3-complete.jar -Dlanguage=Python3 -visitor -o generated grammar/SQLiteLexer.g4
java -jar /tmp/antlr-4.9.3-complete.jar -Dlanguage=Python3 -visitor -lib generated/grammar -o generated grammar/SQLiteParser.g4
touch generated/__init__.py generated/grammar/__init__.py
```

## Tests

```bash
uv run pytest -q
```

## Blog post

This is a demo for my blog post [Dear Claude: Please don't use regex to parse code](https://mbmccoy.dev/posts/no-regex-claude/).
