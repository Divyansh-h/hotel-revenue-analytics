"""
Test Power Query M scripts for structural validity and column consistency.

Checks:
1. Balanced delimiters: [], (), {}, and quotes ("").
2. Explicit typing: every column in the CSV header is typed in Table.TransformColumnTypes.
3. Column reference integrity: every column referenced exists in the CSV header
   or is a valid derived column created earlier in the query.

Outputs PASS / FAIL per check.
Can be run via pytest or directly as a CLI script.
"""

import sys
from pathlib import Path
import csv
import re

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = REPO_ROOT / "data" / "outputs"
PQ_DIR = REPO_ROOT / "excel" / "power_query"

QUERY_FILES = [
    "q_monthly_kpis.m",
    "q_segments.m",
    "q_cancel_drivers.m",
]


def check_balanced_delimiters(code: str) -> tuple[bool, str]:
    """Check that quotes, parentheses, brackets, and curly braces are balanced."""
    # First check quotes balance
    quote_count = code.count('"')
    if quote_count % 2 != 0:
        return False, f"Unbalanced double quotes: found {quote_count} quotes"
    
    # Track brackets while ignoring characters inside string literals
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    in_string = False
    
    i = 0
    n = len(code)
    while i < n:
        char = code[i]
        
        # Handle string literals
        if char == '"':
            # Check for M string escaping: "" inside a string represents a literal quote
            if in_string and i + 1 < n and code[i + 1] == '"':
                i += 2
                continue
            in_string = not in_string
            i += 1
            continue
            
        if not in_string:
            if char in '([{':
                stack.append((char, i))
            elif char in ')]}':
                if not stack:
                    return False, f"Unexpected closing '{char}' at index {i}"
                top, pos = stack.pop()
                if top != pairs[char]:
                    return False, f"Mismatched delimiter: opened with '{top}' at {pos}, closed with '{char}' at {i}"
        i += 1
        
    if in_string:
        return False, "Unclosed string literal at end of script"
    if stack:
        top, pos = stack[-1]
        return False, f"Unclosed '{top}' opened at index {pos}"
        
    return True, "All delimiters balanced () [] {} \"\""


def get_csv_headers_for_query(code: str) -> tuple[str, list[str]]:
    """Find the CSV filename in the query and read its headers."""
    match = re.search(r'File\.Contents\(DataFolder\s*&\s*"([^"]+)"\)', code)
    if not match:
        raise ValueError("Could not find CSV filename in Csv.Document call!")
    csv_name = match.group(1)
    csv_path = OUTPUTS_DIR / csv_name
    if not csv_path.exists():
        raise FileNotFoundError(f"Referenced CSV not found: {csv_path}")
    
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
    return csv_name, [h.strip() for h in headers if h.strip()]


def extract_typed_columns(code: str) -> list[str]:
    """Extract columns listed in Table.TransformColumnTypes."""
    match = re.search(r'Table\.TransformColumnTypes\((.+?),\s*"en-US"\)', code, re.DOTALL)
    if not match:
        raise ValueError("Could not find Table.TransformColumnTypes step with 'en-US' culture!")
    inner = match.group(1)
    typed_cols = re.findall(r'\{\s*"([^"]+)"\s*,', inner)
    return typed_cols


def extract_all_column_references(code: str) -> set[str]:
    """
    Extract all column references in expressions [col_name]
    and column names used in SelectColumns, Sort, etc.
    """
    # 1. Bracketed column references: [col_name]
    bracket_refs = set(re.findall(r'\[([A-Za-z0-9_]+)\]', code))
    
    # 2. String literal column references in SelectColumns
    select_match = re.search(r'Table\.SelectColumns\([^,]+,\s*\{([^}]+)\}\)', code)
    if select_match:
        for col in re.findall(r'"([^"]+)"', select_match.group(1)):
            bracket_refs.add(col)
            
    # 3. String literal column references in Table.Sort
    sort_matches = re.findall(r'\{\s*"([^"]+)"\s*,\s*Order\.(?:Ascending|Descending)\s*\}', code)
    for col in sort_matches:
        bracket_refs.add(col)
        
    return bracket_refs


def extract_added_columns(code: str) -> set[str]:
    """Extract names of new columns created with Table.AddColumn."""
    added = set(re.findall(r'Table\.AddColumn\([^,]+,\s*"([^"]+)"', code))
    return added


def validate_query_file(file_path: Path) -> dict:
    code = file_path.read_text(encoding="utf-8")
    
    # Check 1: Balanced delimiters
    bal_ok, bal_msg = check_balanced_delimiters(code)
    
    # Check 2: All CSV headers typed
    csv_name, csv_headers = get_csv_headers_for_query(code)
    typed_cols = extract_typed_columns(code)
    missing_types = set(csv_headers) - set(typed_cols)
    extra_types = set(typed_cols) - set(csv_headers)
    
    typing_ok = (len(missing_types) == 0 and len(extra_types) == 0)
    if typing_ok:
        typing_msg = f"All {len(csv_headers)} CSV headers explicitly typed"
    else:
        errs = []
        if missing_types:
            errs.append(f"untyped: {missing_types}")
        if extra_types:
            errs.append(f"extra types not in CSV: {extra_types}")
        typing_msg = ", ".join(errs)
        
    # Check 3: All referenced columns exist in header or added columns
    referenced_cols = extract_all_column_references(code)
    added_cols = extract_added_columns(code)
    allowed_cols = set(csv_headers).union(added_cols)
    unresolved_refs = referenced_cols - allowed_cols
    
    ref_ok = (len(unresolved_refs) == 0)
    if ref_ok:
        ref_msg = f"All {len(referenced_cols)} referenced columns valid ({len(referenced_cols - added_cols)} from CSV, {len(referenced_cols.intersection(added_cols))} derived)"
    else:
        ref_msg = f"Unresolved column references: {unresolved_refs}"
        
    overall_pass = bal_ok and typing_ok and ref_ok
    
    return {
        "file": file_path.name,
        "csv": csv_name,
        "bal_ok": bal_ok,
        "bal_msg": bal_msg,
        "typing_ok": typing_ok,
        "typing_msg": typing_msg,
        "ref_ok": ref_ok,
        "ref_msg": ref_msg,
        "overall_pass": overall_pass,
    }


def test_pq_scripts() -> None:
    """Pytest entrypoint to validate all Power Query scripts."""
    for fname in QUERY_FILES:
        fpath = PQ_DIR / fname
        assert fpath.exists(), f"Power Query script missing: {fpath}"
        res = validate_query_file(fpath)
        assert res["bal_ok"], f"{fname} failed balanced delimiters: {res['bal_msg']}"
        assert res["typing_ok"], f"{fname} failed column typing: {res['typing_msg']}"
        assert res["ref_ok"], f"{fname} failed column reference check: {res['ref_msg']}"
        assert res["overall_pass"], f"{fname} failed overall integrity"


def main() -> None:
    print("=" * 80)
    print("TESTING POWER QUERY M SCRIPTS FOR STRUCTURAL AND SCHEMA INTEGRITY")
    print("=" * 80)
    
    all_passed = True
    for fname in QUERY_FILES:
        fpath = PQ_DIR / fname
        if not fpath.exists():
            print(f"[FAIL] Script not found: {fpath}")
            all_passed = False
            continue
            
        res = validate_query_file(fpath)
        status_str = "[PASS]" if res["overall_pass"] else "[FAIL]"
        print(f"\n{status_str} Query: {res['file']} (Source: {res['csv']})")
        print(f"   - Delimiters:   {'PASS' if res['bal_ok'] else 'FAIL'} -> {res['bal_msg']}")
        print(f"   - Column Types: {'PASS' if res['typing_ok'] else 'FAIL'} -> {res['typing_msg']}")
        print(f"   - Column Refs:  {'PASS' if res['ref_ok'] else 'FAIL'} -> {res['ref_msg']}")
        
        if not res["overall_pass"]:
            all_passed = False
            
    print("\n" + "=" * 80)
    if all_passed:
        print("[SUCCESS] ALL POWER QUERY SCRIPTS PASSED ALL INTEGRITY CHECKS.")
        print("=" * 80)
        sys.exit(0)
    else:
        print("[FAILURE] ONE OR MORE INTEGRITY CHECKS FAILED.")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
