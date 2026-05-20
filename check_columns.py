#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["antlr4-python3-runtime==4.9.3"]
# ///
"""Report SQLite columns associated with CHECK constraints."""

from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Iterable

from antlr4 import CommonTokenStream, InputStream, ParseTreeVisitor, Token
from antlr4.error.ErrorListener import ErrorListener

from generated.grammar.SQLiteLexer import SQLiteLexer
from generated.grammar.SQLiteParser import SQLiteParser
from generated.grammar.SQLiteParserVisitor import SQLiteParserVisitor


class UpperCaseInputStream(InputStream):
    """Case-insensitive lexing while preserving original token text."""

    def LA(self, offset: int):
        value = super().LA(offset)
        if value <= 0:
            return value
        return ord(chr(value).upper())


class CollectingErrorListener(ErrorListener):
    def __init__(self) -> None:
        super().__init__()
        self.errors: list[str] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"line {line}:{column} {msg}")


def normalize_identifier(text: str) -> str:
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1].replace('""', '"')
    if len(text) >= 2 and text[0] == "`" and text[-1] == "`":
        return text[1:-1].replace("``", "`")
    if len(text) >= 2 and text[0] == "[" and text[-1] == "]":
        return text[1:-1]
    return text


def canonical_name(ctx) -> str:
    return normalize_identifier(ctx.getText())


def constraint_sql(tokens: CommonTokenStream, start: Token, stop: Token) -> str:
    """Render a constraint from ANTLR tokens with normalized whitespace."""
    pieces: list[str] = []
    needs_space = False
    tight_before = {SQLiteParser.CLOSE_PAR, SQLiteParser.COMMA, SQLiteParser.DOT}

    for token in tokens.tokens[start.tokenIndex : stop.tokenIndex + 1]:
        if token.type == SQLiteLexer.SPACES:
            needs_space = True
            continue
        if token.type == Token.EOF:
            continue

        if token.type == SQLiteParser.COMMA:
            pieces.append(token.text)
            needs_space = True
            continue

        if pieces and token.type not in tight_before:
            if needs_space and pieces[-1] not in ("(", "."):
                pieces.append(" ")
        pieces.append(token.text.strip() if token.channel == Token.HIDDEN_CHANNEL else token.text)
        needs_space = token.channel == Token.HIDDEN_CHANNEL

    return "".join(pieces).strip()


class ReferencedColumnVisitor(ParseTreeVisitor):
    def __init__(self, known_columns: Iterable[str]) -> None:
        super().__init__()
        self.known_columns = set(known_columns)
        self.references: set[str] = set()

    def visitColumn_name(self, ctx: SQLiteParser.Column_nameContext):
        name = canonical_name(ctx)
        if name in self.known_columns:
            self.references.add(name)
        return None

    def visitColumn_name_excluding_string(
        self, ctx: SQLiteParser.Column_name_excluding_stringContext
    ):
        name = canonical_name(ctx)
        if name in self.known_columns:
            self.references.add(name)
        return None


class CheckConstraintVisitor(SQLiteParserVisitor):
    def __init__(self, tokens: CommonTokenStream) -> None:
        super().__init__()
        self.tokens = tokens
        self.tables: OrderedDict[str, OrderedDict[str, list[str]]] = OrderedDict()

    def visitCreate_table_stmt(self, ctx: SQLiteParser.Create_table_stmtContext):
        if ctx.select_stmt():
            return None

        table_name = canonical_name(ctx.table_name())
        columns = [canonical_name(column.column_name()) for column in ctx.column_def()]
        checks_by_column: OrderedDict[str, list[str]] = OrderedDict()

        for column in ctx.column_def():
            column_name = canonical_name(column.column_name())
            for constraint in column.column_constraint():
                if constraint.check_constraint():
                    checks_by_column.setdefault(column_name, []).append(
                        constraint_sql(self.tokens, constraint.start, constraint.stop)
                    )

        for constraint in ctx.table_constraint():
            check = constraint.check_constraint()
            if not check:
                continue
            sql = constraint_sql(self.tokens, constraint.start, constraint.stop)
            refs = ReferencedColumnVisitor(columns)
            refs.visit(check.expr())
            for column_name in columns:
                if column_name in refs.references:
                    checks_by_column.setdefault(column_name, []).append(sql)

        self.tables[table_name] = checks_by_column
        return None


def parse_sql(sql: str) -> OrderedDict[str, OrderedDict[str, list[str]]]:
    stream = UpperCaseInputStream(sql)
    lexer = SQLiteLexer(stream)
    lexer_errors = CollectingErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexer_errors)

    tokens = CommonTokenStream(lexer)
    parser = SQLiteParser(tokens)
    parser_errors = CollectingErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(parser_errors)

    tree = parser.parse()
    errors = lexer_errors.errors + parser_errors.errors
    if errors:
        raise ValueError("SQL parse failed:\n" + "\n".join(errors))

    visitor = CheckConstraintVisitor(tokens)
    visitor.visit(tree)
    return visitor.tables


def main(argv: list[str] | None = None) -> int:
    arg_parser = argparse.ArgumentParser(
        description="Report SQLite columns associated with CHECK constraints."
    )
    arg_parser.add_argument(
        "schema",
        nargs="+",
        type=Path,
        help="One or more .sql schema files; shell globs are supported.",
    )
    args = arg_parser.parse_args(argv)

    try:
        result: OrderedDict[str, OrderedDict[str, list[str]]] = OrderedDict()
        for schema in args.schema:
            result.update(parse_sql(schema.read_text(encoding="utf-8")))
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
