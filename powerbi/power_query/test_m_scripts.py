"""
Structural and Schema Integrity Tests for Power BI Power Query M Scripts:
powerbi/power_query/test_m_scripts.py

Checks:
1. Balanced delimiters: [], (), {}, and quotes ("") for all M scripts.
2. Complete and exact column typing: every column named in Table.TransformColumnTypes
   exists in the CSV header and every CSV header column is typed (0 missing, 0 extra).
3. Culture specification: explicitly uses 'en-US' locale culture.
4. Clean transformation rule: no calculated columns or extra steps in Power Query.
5. Parameter query integrity: parameters.m correctly specifies a text parameter.

Can be run directly via CLI or via pytest.
"""

import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "powerbi" / "data"
PQ_DIR = REPO_ROOT / "powerbi" / "power_query"

TABLE_QUERIES = [
    "dim_date.m",
    "dim_hotel.m",
    "dim_profile.m",
    "fact_bookings.m",
    "fact_stay_nights.m",
    "fact_capacity.m",
]


def check_balanced_delimiters(code: str) -> tuple[bool, str]:
    """Check that quotes, parentheses, brackets, and curly braces are balanced."""
    # First check quotes balance
    quote_count = code.count('"')
    if quote_count % 2 != 0:
        return False, f"Unbalanced double quotes: found {quote_count} quotes"

    # Track brackets while ignoring characters inside string literals
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
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


def get_csv_headers_for_query(code: str) -> tuple[str, list[str]]:
    """Find the CSV filename in the query and read its headers."""
    match = re.search(r'File\.Contents\(DataFolder\s*&\s*"([^"]+)"\)', code)
    if not match:
        raise ValueError("Could not find CSV filename in Csv.Document call!")
    csv_name = match.group(1)
    csv_path = DATA_DIR / csv_name
    if not csv_path.exists():
        raise FileNotFoundError(f"Referenced CSV not found: {csv_path}")

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
    return csv_name, [h.strip() for h in headers if h.strip()]


def extract_typed_columns(code: str) -> list[str]:
    """Extract columns listed in Table.TransformColumnTypes."""
    match = re.search(
        r'Table\.TransformColumnTypes\((.+?),\s*"en-US"\)', code, re.DOTALL
    )
    if not match:
        raise ValueError(
            "Could not find Table.TransformColumnTypes step with 'en-US' culture!"
        )
    inner = match.group(1)
    typed_cols = re.findall(r'\{\s*"([^"]+)"\s*,', inner)
    return typed_cols


def validate_query_file(file_path: Path) -> dict:
    code = file_path.read_text(encoding="utf-8")

    # Check 1: Balanced delimiters
    bal_ok, bal_msg = check_balanced_delimiters(code)

    # Check 2: CSV headers vs typed columns
    csv_name, csv_headers = get_csv_headers_for_query(code)
    typed_cols = extract_typed_columns(code)
    missing_cols = set(csv_headers) - set(typed_cols)
    extra_cols = set(typed_cols) - set(csv_headers)

    typing_ok = (len(missing_cols) == 0 and len(extra_cols) == 0)
    if typing_ok:
        typing_msg = f"All {len(csv_headers)} CSV headers strictly typed (0 missing, 0 extra)"
    else:
        errs = []
        if missing_cols:
            errs.append(f"untyped columns: {missing_cols}")
        if extra_cols:
            errs.append(f"extra columns not in CSV: {extra_cols}")
        typing_msg = "; ".join(errs)

    # Check 3: Culture en-US
    has_culture = '"en-US"' in code

    # Check 4: No calculated columns or extra steps (let -> Source -> Promoted Headers -> Changed Type -> in)
    has_no_extra_steps = (
        "Table.AddColumn" not in code
        and "Table.SelectRows" not in code
        and "Table.Sort" not in code
    )

    overall_pass = bal_ok and typing_ok and has_culture and has_no_extra_steps

    return {
        "file": file_path.name,
        "csv": csv_name,
        "col_count": len(csv_headers),
        "bal_ok": bal_ok,
        "bal_msg": bal_msg,
        "typing_ok": typing_ok,
        "typing_msg": typing_msg,
        "culture_ok": has_culture,
        "no_calc_cols_ok": has_no_extra_steps,
        "overall_pass": overall_pass,
    }


def validate_parameters_file(file_path: Path) -> dict:
    code = file_path.read_text(encoding="utf-8")
    bal_ok, bal_msg = check_balanced_delimiters(code)
    is_param = (
        "IsParameterQuery=true" in code
        and 'Type="Text"' in code
        and "IsParameterQueryRequired=true" in code
    )
    overall_pass = bal_ok and is_param
    return {
        "file": file_path.name,
        "bal_ok": bal_ok,
        "bal_msg": bal_msg,
        "is_param": is_param,
        "overall_pass": overall_pass,
    }


def test_power_query_scripts() -> None:
    """Pytest entrypoint for validating Power Query M scripts."""
    # Test table queries
    for fname in TABLE_QUERIES:
        fpath = PQ_DIR / fname
        assert fpath.exists(), f"Query file missing: {fpath}"
        res = validate_query_file(fpath)
        assert res["bal_ok"], f"{fname} unbalanced delimiters: {res['bal_msg']}"
        assert res["typing_ok"], f"{fname} typing mismatch: {res['typing_msg']}"
        assert res["culture_ok"], f"{fname} missing en-US culture"
        assert res["no_calc_cols_ok"], f"{fname} contains disallowed extra steps"
        assert res["overall_pass"], f"{fname} failed overall integrity"

    # Test parameters.m
    param_path = PQ_DIR / "parameters.m"
    assert param_path.exists(), f"Parameters file missing: {param_path}"
    param_res = validate_parameters_file(param_path)
    assert param_res["bal_ok"], f"parameters.m unbalanced delimiters: {param_res['bal_msg']}"
    assert param_res["is_param"], "parameters.m missing required parameter metadata"
    assert param_res["overall_pass"], "parameters.m failed validation"


def main() -> None:
    print("=" * 100)
    print("TESTING POWER BI POWER QUERY M SCRIPTS: powerbi/power_query/*.m")
    print("=" * 100)

    all_passed = True

    # Validate table queries
    for fname in TABLE_QUERIES:
        fpath = PQ_DIR / fname
        if not fpath.exists():
            print(f"[FAIL] Missing file: {fname}")
            all_passed = False
            continue

        res = validate_query_file(fpath)
        stat = "PASS" if res["overall_pass"] else "FAIL"
        if not res["overall_pass"]:
            all_passed = False

        print(f"[{stat}] {res['file']:<20} -> Source: {res['csv']:<22} ({res['col_count']} cols)")
        print(f"       - Delimiters:    {'PASS' if res['bal_ok'] else 'FAIL'} ({res['bal_msg']})")
        print(f"       - Column Typing: {'PASS' if res['typing_ok'] else 'FAIL'} ({res['typing_msg']})")
        print(f"       - Culture:       {'PASS' if res['culture_ok'] else 'FAIL'} (en-US explicitly declared)")
        print(f"       - Pure Ingest:   {'PASS' if res['no_calc_cols_ok'] else 'FAIL'} (no calculated columns; DAX pure)")

    # Validate parameters.m
    param_file = PQ_DIR / "parameters.m"
    if not param_file.exists():
        print("[FAIL] Missing parameters.m")
        all_passed = False
    else:
        pres = validate_parameters_file(param_file)
        stat = "PASS" if pres["overall_pass"] else "FAIL"
        if not pres["overall_pass"]:
            all_passed = False
        print(f"[{stat}] {pres['file']:<20} -> Parameter definition for DataFolder")
        print(f"       - Delimiters:    {'PASS' if pres['bal_ok'] else 'FAIL'} ({pres['bal_msg']})")
        print(f"       - Parameter Tag: {'PASS' if pres['is_param'] else 'FAIL'} (IsParameterQuery=true, Type=Text)")

    print("-" * 100)
    if all_passed:
        print("POWER BI POWER QUERY VERIFICATION: ALL 7 M SCRIPTS PASSED [PASS]")
        print("=" * 100)
        sys.exit(0)
    else:
        print("POWER BI POWER QUERY VERIFICATION: ONE OR MORE CHECKS FAILED [FAIL]")
        print("=" * 100)
        sys.exit(1)


if __name__ == "__main__":
    main()
