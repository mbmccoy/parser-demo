import json
import subprocess
import sys

from check_columns import parse_sql


def test_inline_column_check():
    result = parse_sql("CREATE TABLE t (x INTEGER CHECK (x > 0));")

    assert result == {"t": {"x": ["CHECK (x > 0)"]}}


def test_table_level_check():
    result = parse_sql("CREATE TABLE t (x INTEGER, CHECK (x > 0));")

    assert result == {"t": {"x": ["CHECK (x > 0)"]}}


def test_named_table_level_check():
    result = parse_sql(
        "CREATE TABLE t (discount NUMERIC, "
        "CONSTRAINT valid_discount CHECK (discount BETWEEN 0 AND 1));"
    )

    assert result == {
        "t": {
            "discount": [
                "CONSTRAINT valid_discount CHECK (discount BETWEEN 0 AND 1)"
            ]
        }
    }


def test_multiline_check():
    result = parse_sql(
        """
        CREATE TABLE t (
            status TEXT,
            CHECK (
                status IN (
                    'pending',
                    'paid'
                )
            )
        );
        """
    )

    assert result == {
        "t": {"status": ["CHECK (status IN ('pending', 'paid'))"]}
    }


def test_string_literals_with_check_text_and_parentheses_are_not_structure():
    result = parse_sql(
        """
        CREATE TABLE t (
            note TEXT CHECK (note <> 'CHECK (fake)'),
            kind TEXT CHECK (kind IN ('a', 'b) still string')),
            x INTEGER,
            CHECK (x > 0 AND note NOT LIKE 'unbalanced ) paren')
        );
        """
    )

    assert result == {
        "t": {
            "note": [
                "CHECK (note <> 'CHECK (fake)')",
                "CHECK (x > 0 AND note NOT LIKE 'unbalanced ) paren')",
            ],
            "kind": ["CHECK (kind IN ('a', 'b) still string'))"],
            "x": ["CHECK (x > 0 AND note NOT LIKE 'unbalanced ) paren')"],
        }
    }


def test_multiple_create_table_statements_and_unrelated_statements():
    result = parse_sql(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE a (x INTEGER CHECK (x > 0));
        CREATE INDEX idx_a_x ON a (x);
        CREATE TABLE b (y INTEGER, CHECK (y < 10));
        """
    )

    assert result == {
        "a": {"x": ["CHECK (x > 0)"]},
        "b": {"y": ["CHECK (y < 10)"]},
    }


def test_comments_inside_or_around_constraints():
    result = parse_sql(
        """
        CREATE TABLE t (
            x INTEGER
                -- column comment
                CHECK (x > 0),
            y INTEGER,
            /* table constraint */
            CHECK (
                y > 0 /* keep me */
            )
        );
        """
    )

    assert result == {
        "t": {
            "x": ["CHECK (x > 0)"],
            "y": ["CHECK (y > 0 /* keep me */)"],
        }
    }


def test_quoted_identifier_column():
    result = parse_sql(
        'CREATE TABLE users ("user-status" TEXT CHECK ("user-status" IN (\'active\', \'locked\')));'
    )

    assert result == {
        "users": {
            "user-status": [
                'CHECK ("user-status" IN (\'active\', \'locked\'))'
            ]
        }
    }


def test_table_level_check_referring_to_two_columns():
    result = parse_sql(
        "CREATE TABLE orders (quantity INTEGER, unit_price NUMERIC, "
        "CHECK (quantity * unit_price >= 0));"
    )

    assert result == {
        "orders": {
            "quantity": ["CHECK (quantity * unit_price >= 0)"],
            "unit_price": ["CHECK (quantity * unit_price >= 0)"],
        }
    }


def test_cli_outputs_json(tmp_path):
    schema = tmp_path / "schema.sql"
    schema.write_text("CREATE TABLE t (x INTEGER CHECK (x > 0));", encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "check_columns.py", str(schema)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(completed.stdout) == {"t": {"x": ["CHECK (x > 0)"]}}
