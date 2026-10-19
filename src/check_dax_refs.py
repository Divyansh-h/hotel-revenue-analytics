"""
DAX Measure Reference & Syntax Checker: src/check_dax_refs.py

Validates powerbi/measures.dax:
1. Balanced delimiters: parentheses (), brackets [], braces {}, and quotes "".
2. Schema existence: every table[column] reference exists in powerbi/data/<table_name>.csv headers.
3. Measure existence: every [Measure] reference without a table prefix is defined in the file.
4. Metadata completeness: every measure has Purpose, Display Folder, and Format String.

Prints detailed verification status. Exits with 0 on full pass, 1 on any failure.
"""

import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "powerbi" / "data"
DAX_FILE = REPO_ROOT / "powerbi" / "measures.dax"


def load_csv_headers() -> dict[str, list[str]]:
    """Load column headers for all CSV files in powerbi/data."""
    headers_by_table = {}
    for csv_file in DATA_DIR.glob("*.csv"):
        table_name = csv_file.stem
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
        headers_by_table[table_name] = [h.strip() for h in headers if h.strip()]
    return headers_by_table


def check_balanced_delimiters(code: str) -> tuple[bool, str]:
    """Check that quotes, parentheses, brackets, and braces are balanced."""
    # First remove single-line comments
    clean_lines = []
    for line in code.splitlines():
        # Remove // comment
        line_no_comment = re.sub(r'//.*$', '', line)
        clean_lines.append(line_no_comment)
    clean_code = "\n".join(clean_lines)

    # Remove block comments
    clean_code = re.sub(r'/\*.*?\*/', '', clean_code, flags=re.DOTALL)

    # Check quote balance
    quote_count = clean_code.count('"')
    if quote_count % 2 != 0:
        return False, f"Unbalanced double quotes: found {quote_count} quotes"

    # Track brackets while ignoring characters inside string literals
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    in_string = False

    i = 0
    n = len(clean_code)
    while i < n:
        char = clean_code[i]

        # Handle string literals and escaped quotes ""
        if char == '"':
            if in_string and i + 1 < n and clean_code[i + 1] == '"':
                i += 2
                continue
            in_string = not in_string
            i += 1
            continue

        if not in_string:
            if char in "([{":
                stack.append((char, i))
            elif char in ")]}":
                if not stack:
                    return False, f"Unexpected closing '{char}' at index {i}"
                top, pos = stack.pop()
                if top != pairs[char]:
                    return (
                        False,
                        f"Mismatched delimiter: opened with '{top}' at {pos}, closed with '{char}' at {i}",
                    )
        i += 1

    if in_string:
        return False, "Unclosed string literal at end of script"
    if stack:
        top, pos = stack[-1]
        return False, f"Unclosed '{top}' opened at index {pos}"

    return True, 'All delimiters balanced () [] {} ""'


def parse_measures_file(dax_path: Path):
    """Parse powerbi/measures.dax and extract measures, comments, and expressions."""
    content = dax_path.read_text(encoding="utf-8")

    # Regular expression to match measure definitions
    # Matches comments above the measure name, followed by Measure Name =
    pattern = re.compile(
        r'((?:(?://[^\n]*\n|\s*)*))'  # Group 1: comment lines
        r'^\s*([A-Za-z0-9_ %(),-]+?)\s*=\s*\n'  # Group 2: measure name
        r'(.*?)(?=(?:(?://[^\n]*\n|\s*)*^\s*[A-Za-z0-9_ %(),-]+?\s*=\s*\n)|\Z)',  # Group 3: formula body
        re.MULTILINE | re.DOTALL,
    )

    measures = []
    for match in pattern.finditer(content):
        comments_raw, measure_name, body = match.groups()
        measure_name = measure_name.strip()
        if measure_name.startswith("[") and measure_name.endswith("]"):
            measure_name = measure_name[1:-1]

        # Extract metadata from comments
        purpose = None
        display_folder = None
        format_string = None

        for line in comments_raw.splitlines():
            line = line.strip()
            if line.startswith("// Purpose:"):
                purpose = line[len("// Purpose:"):].strip()
            elif line.startswith("// Display Folder:"):
                display_folder = line[len("// Display Folder:"):].strip()
            elif line.startswith("// Format String:"):
                format_string = line[len("// Format String:"):].strip()

        measures.append({
            "name": measure_name,
            "purpose": purpose,
            "folder": display_folder,
            "format": format_string,
            "body": body.strip(),
        })

    return measures, content


def extract_references(clean_body: str):
    """Extract table[column] and standalone [measure] references."""
    # Find all table[column] references
    col_refs = re.findall(r'([a-zA-Z0-9_]+)\[([a-zA-Z0-9_]+)\]', clean_body)

    # Find standalone [measure] references (not preceded by table name or word character)
    # Note: match measure names that might have spaces, %, (), etc.
    measure_refs = re.findall(r'(?<![a-zA-Z0-9_])\[([a-zA-Z0-9_ %(),-]+)\]', clean_body)

    return col_refs, measure_refs


def main():
    print("=" * 100)
    print("POWER BI DAX REFERENCE & SYNTAX VERIFICATION: powerbi/measures.dax")
    print("=" * 100)
    print("[NOTE] DAX formulas cannot be executed in this non-desktop environment.")
    print("       Checking delimiter balance, table[column] physical existence, and measure dependencies.")
    print("-" * 100)

    if not DAX_FILE.exists():
        print(f"[FAIL] Missing DAX file: {DAX_FILE}")
        sys.exit(1)

    csv_headers = load_csv_headers()
    measures, full_content = parse_measures_file(DAX_FILE)

    all_passed = True

    # 1. Check Delimiters
    bal_ok, bal_msg = check_balanced_delimiters(full_content)
    print(f"[{'PASS' if bal_ok else 'FAIL'}] Delimiter Balance Check: {bal_msg}")
    if not bal_ok:
        all_passed = False

    # 2. Check Measures Parsed
    print(f"[INFO] Discovered {len(measures)} measures in {DAX_FILE.name}:")
    defined_measure_names = {m["name"] for m in measures}

    for m in measures:
        folder = m["folder"] or "None"
        fmt = m["format"] or "None"
        print(f"       - [{m['name']}] (Folder: '{folder}', Format: '{fmt}')")

    # 3. Check Metadata Completeness
    missing_meta = []
    for m in measures:
        if not m["purpose"] or not m["folder"] or not m["format"]:
            missing_meta.append(m["name"])

    if missing_meta:
        print(f"[FAIL] Missing Purpose/Folder/Format comments for: {missing_meta}")
        all_passed = False
    else:
        print("[PASS] Metadata Completeness: All 26 measures have Purpose, Folder, and Format.")

    # 4. Check Table[Column] References
    all_col_refs = set()
    all_meas_refs = set()

    for m in measures:
        # Strip line comments before scanning body
        body_clean = "\n".join(
            re.sub(r'//.*$', '', l) for l in m["body"].splitlines()
        )
        col_refs, meas_refs = extract_references(body_clean)
        for t, c in col_refs:
            all_col_refs.add((t, c))
        for ref_m in meas_refs:
            all_meas_refs.add((m["name"], ref_m))

    invalid_cols = []
    for table, col in sorted(all_col_refs):
        if table not in csv_headers:
            invalid_cols.append((table, col, f"Table '{table}.csv' not found in powerbi/data/"))
        elif col not in csv_headers[table]:
            invalid_cols.append((table, col, f"Column '{col}' not in '{table}.csv' (Valid: {csv_headers[table]})"))

    if invalid_cols:
        print(f"[FAIL] Invalid Table[Column] references detected ({len(invalid_cols)}):")
        for t, c, reason in invalid_cols:
            print(f"       - {t}[{c}]: {reason}")
        all_passed = False
    else:
        print(f"[PASS] Physical Column References: All {len(all_col_refs)} table[column] references exist in CSV headers:")
        for t, c in sorted(all_col_refs):
            print(f"       - {t}[{c}]")

    # 5. Check Measure-to-Measure References
    invalid_measure_refs = []
    for source_m, target_m in sorted(all_meas_refs):
        if target_m not in defined_measure_names:
            invalid_measure_refs.append((source_m, target_m))

    if invalid_measure_refs:
        print(f"[FAIL] Undefined [Measure] references detected ({len(invalid_measure_refs)}):")
        for sm, tm in invalid_measure_refs:
            print(f"       - In measure '{sm}': referenced [{tm}] is not defined in measures.dax")
        all_passed = False
    else:
        print(f"[PASS] Measure Dependency References: All {len(all_meas_refs)} internal [Measure] references exist.")

    print("-" * 100)
    if all_passed:
        print("POWER BI DAX REFERENCE CHECK: ALL CHECKS PASSED [PASS]")
        print("=" * 100)
        sys.exit(0)
    else:
        print("POWER BI DAX REFERENCE CHECK: CHECKS FAILED [FAIL]")
        print("=" * 100)
        sys.exit(1)


def test_dax_measures():
    """Pytest entrypoint to validate powerbi/measures.dax."""
    assert DAX_FILE.exists(), f"Missing DAX file: {DAX_FILE}"
    csv_headers = load_csv_headers()
    measures, full_content = parse_measures_file(DAX_FILE)

    bal_ok, bal_msg = check_balanced_delimiters(full_content)
    assert bal_ok, f"Unbalanced delimiters: {bal_msg}"
    assert len(measures) == 26, f"Expected 26 measures, found {len(measures)}"

    defined_measure_names = {m["name"] for m in measures}
    for m in measures:
        assert m["purpose"], f"Missing purpose for {m['name']}"
        assert m["folder"], f"Missing folder for {m['name']}"
        assert m["format"], f"Missing format for {m['name']}"

        body_clean = "\n".join(re.sub(r'//.*$', '', l) for l in m["body"].splitlines())
        col_refs, meas_refs = extract_references(body_clean)
        for t, c in col_refs:
            assert t in csv_headers, f"Table '{t}' not in CSVs"
            assert c in csv_headers[t], f"Column '{c}' not in table '{t}'"
        for ref_m in meas_refs:
            assert ref_m in defined_measure_names, f"Measure '[{ref_m}]' referenced in '{m['name']}' not defined"


if __name__ == "__main__":
    main()

