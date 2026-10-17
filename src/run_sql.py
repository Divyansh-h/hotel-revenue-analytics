"""
Transactional SQL Script Runner
Reads a .sql file, splits statements using sqlparse, executes them in a single transaction,
prints progress and results, and rolls back on error.
Adheres to Rule R10.
"""

import sys
from pathlib import Path
import sqlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.db import get_connection


def run_sql_file(sql_file_path: Path):
    if not sql_file_path.exists():
        print(f"Error: SQL file does not exist: {sql_file_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading SQL script: {sql_file_path}")
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    statements = [stmt.strip() for stmt in sqlparse.split(sql_content) if stmt.strip()]
    print(f"Found {len(statements)} SQL statement(s) to execute.\n")

    conn = get_connection()
    try:
        with conn:  # Transaction block
            with conn.cursor() as cur:
                for idx, stmt in enumerate(statements, 1):
                    # Clean first line for header
                    first_line = stmt.splitlines()[0].strip()
                    if len(first_line) > 80:
                        first_line = first_line[:77] + "..."
                    print(f"[{idx}/{len(statements)}] Executing: {first_line}")

                    cur.execute(stmt)

                    if cur.description:
                        # Statement returned rows
                        col_names = [desc[0] for desc in cur.description]
                        rows = cur.fetchall()
                        total_rows = len(rows)
                        display_rows = rows[:50]

                        # Format output
                        print(f"  Result ({total_rows} row{'s' if total_rows != 1 else ''}):")
                        header_str = " | ".join(col_names)
                        print(f"  {header_str}")
                        print(f"  {'-' * len(header_str)}")
                        for row in display_rows:
                            row_str = " | ".join(str(val) for val in row)
                            print(f"  {row_str}")
                        if total_rows > 50:
                            print(f"  ... [truncated {total_rows - 50} additional rows]")
                    else:
                        print(f"  Status: {cur.statusmessage or 'OK'}")

        print(f"\nTransaction committed successfully for {sql_file_path.name}.")
    except Exception as e:
        conn.rollback()
        print(f"\nERROR executing SQL statement: {e}", file=sys.stderr)
        print("Transaction rolled back.", file=sys.stderr)
        conn.close()
        sys.exit(1)
    finally:
        conn.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/run_sql.py <path_to_sql_file>")
        sys.exit(1)

    sql_path = Path(sys.argv[1]).resolve()
    run_sql_file(sql_path)


if __name__ == "__main__":
    main()
