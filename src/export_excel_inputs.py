"""
Export Excel Inputs from PostgreSQL
Exports 4 input CSV files to excel/inputs/ for Phase 3 workbook construction:
1. bookings_for_excel.csv (hotel.bookings: 22 source columns of tblBookings, ordered by booking_id)
2. monthly_kpis_for_excel.csv (hotel.v_monthly_kpis: spec columns, ordered by Hotel, Month_Start)
3. capacity_for_excel.csv (hotel.capacity_derivation: spec columns, ordered by Hotel)
4. expected_checks.csv (SQL-computed verification benchmarks per hotel and total)

Performs strict validations:
- bookings_for_excel.csv row count equals cleaned row count (119,388)
- No cell in any output file contains 'nan' or 'None'
- Row count is well below Excel's maximum limit of 1,048,575
- Prints row counts and file sizes in MB
"""

import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.db import get_engine

OUTPUT_DIR = REPO_ROOT / "excel" / "inputs"
EXCEL_ROW_LIMIT = 1048575
EXPECTED_CLEANED_ROWS = 119388


def export_bookings(engine) -> Path:
    query = """
    SELECT
        booking_id,
        hotel,
        is_canceled,
        reservation_status,
        lead_time,
        lead_bucket,
        lead_bucket_order,
        arrival_date,
        arrival_month_start,
        total_nights,
        adults,
        children,
        babies,
        country,
        market_segment,
        distribution_channel,
        customer_type,
        deposit_type,
        adr,
        room_revenue,
        room_type_mismatch,
        is_duplicate_row
    FROM hotel.bookings
    ORDER BY booking_id;
    """
    df = pd.read_sql_query(query, engine)

    # Ensure ISO string formatting for dates
    df["arrival_date"] = pd.to_datetime(df["arrival_date"]).dt.strftime("%Y-%m-%d")
    df["arrival_month_start"] = pd.to_datetime(df["arrival_month_start"]).dt.strftime("%Y-%m-%d")

    file_path = OUTPUT_DIR / "bookings_for_excel.csv"
    df.to_csv(file_path, index=False, encoding="utf-8", date_format="%Y-%m-%d", decimal=".")
    return file_path


def export_monthly_kpis(engine) -> Path:
    query = """
    SELECT
        hotel AS "Hotel",
        month_start AS "Month_Start",
        room_nights_sold AS "Room_Nights_Sold",
        room_revenue AS "Room_Revenue",
        occupancy_pct AS "SQL_Occupancy_Pct",
        adr AS "SQL_ADR",
        revpar AS "SQL_RevPAR"
    FROM hotel.v_monthly_kpis
    ORDER BY "Hotel", "Month_Start";
    """
    df = pd.read_sql_query(query, engine)
    df["Month_Start"] = pd.to_datetime(df["Month_Start"]).dt.strftime("%Y-%m-%d")

    file_path = OUTPUT_DIR / "monthly_kpis_for_excel.csv"
    df.to_csv(file_path, index=False, encoding="utf-8", date_format="%Y-%m-%d", decimal=".")
    return file_path


def export_capacity(engine) -> Path:
    query = """
    SELECT
        hotel AS "Hotel",
        peak_rooms_sold AS "Peak_Rooms_Sold",
        capacity_buffer AS "Buffer",
        capacity AS "Rooms"
    FROM hotel.capacity_derivation
    ORDER BY "Hotel";
    """
    df = pd.read_sql_query(query, engine)

    file_path = OUTPUT_DIR / "capacity_for_excel.csv"
    df.to_csv(file_path, index=False, encoding="utf-8", decimal=".")
    return file_path


def export_expected_checks(engine) -> Path:
    query = """
    WITH booking_metrics AS (
        SELECT
            COALESCE(hotel, 'Total') AS hotel,
            COUNT(*)::numeric AS bookings,
            COUNT(*) FILTER (WHERE is_canceled = 1)::numeric AS cancellations,
            ROUND(COUNT(*) FILTER (WHERE is_canceled = 1)::numeric / COUNT(*)::numeric, 4) AS cancel_rate,
            ROUND(SUM(room_revenue) FILTER (WHERE is_canceled = 0)::numeric, 2) AS sum_room_revenue_realised,
            SUM(total_nights) FILTER (WHERE is_canceled = 0)::numeric AS sum_total_nights_realised
        FROM hotel.bookings
        GROUP BY ROLLUP(hotel)
    ),
    window_metrics AS (
        SELECT
            COALESCE(hotel, 'Total') AS hotel,
            SUM(room_nights_sold)::numeric AS room_nights_sold,
            ROUND(SUM(room_revenue)::numeric, 2) AS room_revenue,
            ROUND(SUM(room_nights_sold)::numeric / SUM(room_nights_available)::numeric, 4) AS occupancy,
            ROUND(SUM(room_revenue)::numeric / SUM(room_nights_available)::numeric, 2) AS revpar
        FROM hotel.v_monthly_kpis
        GROUP BY ROLLUP(hotel)
    ),
    unpivoted AS (
        SELECT 'bookings' AS check_name, hotel, bookings AS expected_value, 0.0000 AS tolerance, 1 AS ord FROM booking_metrics
        UNION ALL
        SELECT 'cancellations', hotel, cancellations, 0.0000, 2 FROM booking_metrics
        UNION ALL
        SELECT 'cancel_rate', hotel, cancel_rate, 0.0001, 3 FROM booking_metrics
        UNION ALL
        SELECT 'sum_room_revenue_realised', hotel, sum_room_revenue_realised, 0.0100, 4 FROM booking_metrics
        UNION ALL
        SELECT 'sum_total_nights_realised', hotel, sum_total_nights_realised, 0.0000, 5 FROM booking_metrics
        UNION ALL
        SELECT 'room_nights_sold', hotel, room_nights_sold, 0.0000, 6 FROM window_metrics
        UNION ALL
        SELECT 'room_revenue', hotel, room_revenue, 0.0100, 7 FROM window_metrics
        UNION ALL
        SELECT 'occupancy', hotel, occupancy, 0.0001, 8 FROM window_metrics
        UNION ALL
        SELECT 'revpar', hotel, revpar, 0.0500, 9 FROM window_metrics
    )
    SELECT
        check_name,
        hotel,
        expected_value,
        tolerance
    FROM unpivoted
    ORDER BY ord, CASE WHEN hotel = 'City Hotel' THEN 1 WHEN hotel = 'Resort Hotel' THEN 2 ELSE 3 END;
    """
    df = pd.read_sql_query(query, engine)

    # Format numbers cleanly
    def format_val(row):
        val = row["expected_value"]
        name = row["check_name"]
        if name in ["bookings", "cancellations", "sum_total_nights_realised", "room_nights_sold"]:
            return f"{int(round(val))}"
        elif name in ["cancel_rate", "occupancy"]:
            return f"{val:.4f}"
        elif name in ["sum_room_revenue_realised", "room_revenue", "revpar"]:
            return f"{val:.2f}"
        return str(val)

    def format_tol(row):
        tol = row["tolerance"]
        name = row["check_name"]
        if name in ["bookings", "cancellations", "sum_total_nights_realised", "room_nights_sold"]:
            return "0"
        elif name in ["cancel_rate", "occupancy"]:
            return "0.0001"
        elif name in ["sum_room_revenue_realised", "room_revenue"]:
            return "0.01"
        elif name in ["revpar"]:
            return "0.05"
        return str(tol)

    df["expected_value"] = df.apply(format_val, axis=1)
    df["tolerance"] = df.apply(format_tol, axis=1)

    file_path = OUTPUT_DIR / "expected_checks.csv"
    df.to_csv(file_path, index=False, encoding="utf-8")
    return file_path


def verify_file(file_path: Path, expected_rows: int = None) -> dict:
    size_mb = file_path.stat().st_size / (1024 * 1024)

    # Read raw text to check for forbidden strings 'nan' or 'None'
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into lines
    lines = [line for line in content.splitlines() if line.strip()]
    header = lines[0].split(",")
    data_rows = len(lines) - 1

    # Check for 'nan' or 'None' (case-insensitive) in cells
    # Parse tokens
    forbidden_found = False
    forbidden_tokens = []
    for line_idx, line in enumerate(lines):
        tokens = line.split(",")
        for tok in tokens:
            cleaned_tok = tok.strip().lower()
            if cleaned_tok in ["nan", "none"]:
                forbidden_found = True
                forbidden_tokens.append((line_idx, tok))
                if len(forbidden_tokens) >= 5:
                    break
        if len(forbidden_tokens) >= 5:
            break

    # Excel limit check
    excel_limit_pass = data_rows <= EXCEL_ROW_LIMIT

    # Row count check if specified
    row_count_pass = True
    if expected_rows is not None:
        row_count_pass = (data_rows == expected_rows)

    return {
        "file": file_path.name,
        "size_mb": size_mb,
        "rows": data_rows,
        "cols": len(header),
        "forbidden_found": forbidden_found,
        "forbidden_sample": forbidden_tokens,
        "excel_limit_pass": excel_limit_pass,
        "row_count_pass": row_count_pass
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = get_engine()

    print("=" * 80)
    print("PHASE 3: EXPORTING EXCEL INPUT MARTS FROM POSTGRESQL")
    print("=" * 80)

    # 1. Export files
    print("\n1. Querying database and exporting CSV files...")
    bookings_file = export_bookings(engine)
    monthly_file = export_monthly_kpis(engine)
    capacity_file = export_capacity(engine)
    checks_file = export_expected_checks(engine)

    files_to_check = [
        (bookings_file, EXPECTED_CLEANED_ROWS),
        (monthly_file, 50),
        (capacity_file, 2),
        (checks_file, 27)
    ]

    print("\n2. Verification & Validation Results:")
    print("-" * 80)
    print(f"{'File Name':<30} | {'Rows':<8} | {'Cols':<5} | {'Size (MB)':<10} | {'No NaN/None':<12} | {'Excel Limit'}")
    print("-" * 80)

    all_passed = True
    for fpath, expected_r in files_to_check:
        res = verify_file(fpath, expected_r)
        nan_status = "PASS" if not res["forbidden_found"] else "FAIL"
        excel_status = "PASS" if res["excel_limit_pass"] else "FAIL"
        row_status = "PASS" if res["row_count_pass"] else "FAIL"

        print(f"{res['file']:<30} | {res['rows']:<8} | {res['cols']:<5} | {res['size_mb']:<10.4f} | {nan_status:<12} | {excel_status}")

        if not res["row_count_pass"]:
            print(f"  [ERROR] Row count mismatch in {res['file']}: expected {expected_r}, got {res['rows']}")
            all_passed = False

        if res["forbidden_found"]:
            print(f"  [ERROR] Forbidden 'nan' or 'None' found in {res['file']}: {res['forbidden_sample']}")
            all_passed = False

        if not res["excel_limit_pass"]:
            print(f"  [ERROR] File {res['file']} exceeds Excel limit ({res['rows']} > {EXCEL_ROW_LIMIT})")
            all_passed = False

    print("-" * 80)

    if not all_passed:
        print("\n[CRITICAL ERROR] Validation failed! Halting pipeline per Rule R5.")
        sys.exit(1)

    print("\n[SUCCESS] All 4 Excel input files exported and verified successfully.")
    print("=" * 80)


if __name__ == "__main__":
    main()
