#!/usr/bin/env python3
"""
Master Pipeline Runner for Hotel Revenue & Cancellation Analytics.
Executes the complete data and analytics pipeline in exact dependency order.
Stops immediately at the first failure and prints a timing line per step.
Adheres to Rule R1, R3, R4, R10.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

def run_command(cmd, step_name: str, cwd: Path = REPO_ROOT) -> float:
    """Runs a subprocess command, prints live output, and returns elapsed time in seconds."""
    print(f"\n{'='*70}")
    print(f">> STARTING: {step_name}")
    print(f">> COMMAND:  {' '.join(str(c) for c in cmd)}")
    print(f"{'='*70}")

    start_time = time.perf_counter()
    proc = subprocess.run(cmd, cwd=str(cwd))
    elapsed = time.perf_counter() - start_time

    if proc.returncode != 0:
        print(f"\n[FAILED] {step_name} exited with returncode {proc.returncode} after {elapsed:.2f}s", file=sys.stderr)
        sys.exit(proc.returncode)

    print(f"[PASSED] {step_name} completed in {elapsed:.2f}s")
    return elapsed

def main():
    total_start = time.perf_counter()
    python_bin = sys.executable

    print("\n" + "#"*70)
    print("HOTEL REVENUE ANALYTICS - MASTER PIPELINE RUNNER (run_all.py)")
    print(f"Repository Root: {REPO_ROOT}")
    print(f"Python Binary:   {python_bin}")
    print("#"*70)

    # 1. Discover SQL files in sql/ in filename order, excluding 00_ and 01_ (already run/schema)
    sql_dir = REPO_ROOT / "sql"
    sql_files = sorted([
        f for f in sql_dir.glob("*.sql")
        if not f.name.startswith("00_") and not f.name.startswith("01_")
    ], key=lambda x: x.name)

    # Define steps in exact required dependency order
    steps = [
        ("clean_data", [python_bin, str(REPO_ROOT / "src" / "clean_data.py")]),
        ("tests", [python_bin, "-m", "pytest", str(REPO_ROOT / "tests" / "test_clean.py"), "-v"]),
        ("load_to_postgres", [python_bin, str(REPO_ROOT / "src" / "load_to_postgres.py")]),
    ]

    # Add each SQL file
    for sf in sql_files:
        steps.append((f"sql/{sf.name}", [python_bin, str(REPO_ROOT / "src" / "run_sql.py"), str(sf)]))

    # Add downstream pipeline scripts
    steps.extend([
        ("write_assumptions", [python_bin, str(REPO_ROOT / "src" / "write_assumptions.py")]),
        ("export_sql_outputs", [python_bin, str(REPO_ROOT / "src" / "export_sql_outputs.py")]),
        ("crosscheck_sql_vs_pandas", [python_bin, str(REPO_ROOT / "src" / "crosscheck_sql_vs_pandas.py")]),
        ("export_powerbi_model", [python_bin, str(REPO_ROOT / "src" / "export_powerbi_model.py")]),
        ("validate_powerbi_model", [python_bin, str(REPO_ROOT / "src" / "validate_powerbi_model.py")]),
        ("make_pbi_m_scripts", [python_bin, str(REPO_ROOT / "src" / "make_pbi_m_scripts.py")]),
        ("check_dax_refs", [python_bin, str(REPO_ROOT / "src" / "check_dax_refs.py")]),
        ("export_excel_inputs", [python_bin, str(REPO_ROOT / "src" / "export_excel_inputs.py")]),
        ("build_country_lookup", [python_bin, str(REPO_ROOT / "src" / "build_country_lookup.py")]),
        ("make_pivot_expected", [python_bin, str(REPO_ROOT / "src" / "make_pivot_expected.py")]),
        ("make_pq_scripts", [python_bin, str(REPO_ROOT / "src" / "make_pq_scripts.py")]),
        ("build_workbook", [python_bin, str(REPO_ROOT / "src" / "build_workbook.py")]),
        ("build_findings", [python_bin, str(REPO_ROOT / "src" / "make_findings_data.py")]),
        ("make_dashboard_text", [python_bin, str(REPO_ROOT / "src" / "make_dashboard_text.py")]),
        ("audit_report_numbers", [python_bin, str(REPO_ROOT / "src" / "audit_report_numbers.py")]),
    ])

    timing_results = []
    print(f"\nQueued {len(steps)} pipeline steps for execution:")
    for idx, (name, _) in enumerate(steps, 1):
        print(f"  {idx:02d}. {name}")

    for idx, (name, cmd) in enumerate(steps, 1):
        step_label = f"Step {idx:02d}/{len(steps):02d}: {name}"
        elapsed = run_command(cmd, step_label)
        timing_results.append((name, elapsed))

    total_elapsed = time.perf_counter() - total_start

    print("\n" + "="*70)
    print("MASTER PIPELINE EXECUTION SUMMARY")
    print("="*70)
    for idx, (name, elapsed) in enumerate(timing_results, 1):
        print(f"  {idx:02d}. {name:<35} : {elapsed:>7.2f}s  [SUCCESS]")
    print("-"*70)
    print(f"Total Pipeline Execution Time: {total_elapsed:.2f}s ({total_elapsed/60:.2f} min)")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
