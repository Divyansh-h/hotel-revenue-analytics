"""
PostgreSQL Ingestion and Reconciliation Script
Loads data/processed/bookings_clean.csv into hotel.bookings using psycopg2 copy_expert.
Requirements:
  1. Idempotent: TRUNCATE hotel.bookings inside the same transaction as COPY.
  2. copy_expert with explicit column list and (FORMAT csv, HEADER true, NULL '').
  3. Run ANALYZE hotel.bookings after loading.
  4. Full reconciliation against pandas dataframe.
  5. Non-zero exit code on failure.
"""

import sys
from decimal import Decimal
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.db import get_connection

FINAL_COLUMNS = [
    "booking_id", "hotel", "is_canceled", "is_no_show", "reservation_status",
    "reservation_status_date", "lead_time", "lead_bucket", "lead_bucket_order",
    "booking_date", "arrival_date", "arrival_year", "arrival_month_num",
    "arrival_month_start", "checkout_date", "stays_in_weekend_nights",
    "stays_in_week_nights", "total_nights", "adults", "children", "babies",
    "total_guests", "meal", "country", "market_segment", "distribution_channel",
    "is_repeated_guest", "previous_cancellations", "previous_bookings_not_canceled",
    "reserved_room_type", "assigned_room_type", "room_type_mismatch",
    "booking_changes", "deposit_type", "agent", "days_in_waiting_list",
    "customer_type", "adr", "required_car_parking_spaces",
    "total_of_special_requests", "room_revenue", "days_cancelled_before_arrival",
    "flag_zero_nights", "flag_zero_guests", "is_duplicate_row"
]


def load_and_reconcile() -> bool:
    csv_path = REPO_ROOT / "data" / "processed" / "bookings_clean.csv"
    if not csv_path.exists():
        print(f"Error: Processed file not found: {csv_path}", file=sys.stderr)
        return False

    print(f"Loading reference CSV into pandas: {csv_path}")
    df_csv = pd.read_csv(csv_path, low_memory=False)
    csv_rows = len(df_csv)
    print(f"Read {csv_rows:,} rows from CSV.\n")

    conn = get_connection()
    cols_str = ", ".join(FINAL_COLUMNS)
    copy_query = (
        f"COPY hotel.bookings ({cols_str}) "
        "FROM STDIN WITH (FORMAT csv, HEADER true, NULL '');"
    )

    # 1. Idempotent Load in a single transaction
    print("Initiating transactional load (TRUNCATE + COPY)...")
    try:
        with conn:
            with conn.cursor() as cur:
                print("  Executing: TRUNCATE TABLE hotel.bookings;")
                cur.execute("TRUNCATE TABLE hotel.bookings;")
                print(f"  Executing copy_expert into hotel.bookings ({len(FINAL_COLUMNS)} columns)...")
                with open(csv_path, "r", encoding="utf-8") as f:
                    cur.copy_expert(copy_query, f)
        print("Load transaction committed successfully.\n")
    except Exception as e:
        print(f"Transaction failed during COPY: {e}", file=sys.stderr)
        conn.close()
        return False

    # 3. Run ANALYZE hotel.bookings
    print("Executing: ANALYZE hotel.bookings;")
    try:
        with conn.cursor() as cur:
            cur.execute("ANALYZE hotel.bookings;")
        conn.commit()
        print("ANALYZE completed successfully.\n")
    except Exception as e:
        print(f"Warning: ANALYZE encountered error: {e}", file=sys.stderr)

    # 4. Reconciliation
    print("=" * 80)
    print("DATA RECONCILIATION: PostgreSQL (hotel.bookings) vs CSV (pandas)")
    print("=" * 80)

    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*)::bigint,
                SUM(total_nights)::bigint,
                SUM(adr)::numeric,
                SUM(room_revenue)::numeric,
                SUM(is_canceled)::bigint,
                SUM(is_duplicate_row)::bigint,
                SUM(flag_zero_nights)::bigint,
                MIN(arrival_date)::text,
                MAX(arrival_date)::text,
                COUNT(*) FILTER (WHERE agent IS NULL)::bigint,
                COUNT(*) FILTER (WHERE days_cancelled_before_arrival IS NULL)::bigint
            FROM hotel.bookings;
        """)
        db_res = cur.fetchone()

        cur.execute("""
            SELECT hotel, ROUND(AVG(is_canceled)::numeric, 4)
            FROM hotel.bookings
            GROUP BY hotel
            ORDER BY hotel;
        """)
        db_cr_rows = cur.fetchall()

    conn.close()

    db_counts = {
        "row_count": int(db_res[0]),
        "sum_total_nights": int(db_res[1]),
        "sum_adr": float(db_res[2]),
        "sum_room_revenue": float(db_res[3]),
        "sum_is_canceled": int(db_res[4]),
        "sum_is_duplicate_row": int(db_res[5]),
        "sum_flag_zero_nights": int(db_res[6]),
        "min_arrival_date": str(db_res[7]),
        "max_arrival_date": str(db_res[8]),
        "null_agent": int(db_res[9]),
        "null_days_cancelled": int(db_res[10]),
    }
    db_cr = {r[0]: float(r[1]) for r in db_cr_rows}

    # CSV metrics
    csv_counts = {
        "row_count": int(len(df_csv)),
        "sum_total_nights": int(df_csv["total_nights"].sum()),
        "sum_adr": float(df_csv["adr"].sum()),
        "sum_room_revenue": float(df_csv["room_revenue"].sum()),
        "sum_is_canceled": int(df_csv["is_canceled"].sum()),
        "sum_is_duplicate_row": int(df_csv["is_duplicate_row"].sum()),
        "sum_flag_zero_nights": int(df_csv["flag_zero_nights"].sum()),
        "min_arrival_date": str(df_csv["arrival_date"].min()),
        "max_arrival_date": str(df_csv["arrival_date"].max()),
        "null_agent": int(df_csv["agent"].isna().sum()),
        "null_days_cancelled": int(df_csv["days_cancelled_before_arrival"].isna().sum()),
    }
    csv_cr = {
        h: round(float(g["is_canceled"].mean()), 4)
        for h, g in df_csv.groupby("hotel")
    }

    all_pass = True
    results = []

    def check(metric: str, csv_val, db_val, is_float: bool = False, tolerance: float = 0.01):
        nonlocal all_pass
        if is_float:
            diff = abs(float(csv_val) - float(db_val))
            passed = diff <= tolerance
            note = f"diff: {diff:.4f}" if diff > 0 else "exact match"
            if 0 < diff <= tolerance:
                note += " (within rounding tolerance < 0.01)"
        else:
            passed = (csv_val == db_val)
            note = "exact match" if passed else f"diff: {csv_val} != {db_val}"

        if not passed:
            all_pass = False

        status = "PASS" if passed else "FAIL"
        results.append({
            "Metric": metric,
            "CSV (Pandas)": f"{csv_val:,.2f}" if is_float else str(csv_val),
            "PostgreSQL": f"{db_val:,.2f}" if is_float else str(db_val),
            "Status": status,
            "Notes": note
        })

    # Execute all checks
    check("Row Count", csv_counts["row_count"], db_counts["row_count"])
    check("SUM(total_nights)", csv_counts["sum_total_nights"], db_counts["sum_total_nights"])
    check("SUM(adr)", csv_counts["sum_adr"], db_counts["sum_adr"], is_float=True, tolerance=0.01)
    check("SUM(room_revenue)", csv_counts["sum_room_revenue"], db_counts["sum_room_revenue"], is_float=True, tolerance=0.01)
    check("SUM(is_canceled)", csv_counts["sum_is_canceled"], db_counts["sum_is_canceled"])
    check("SUM(is_duplicate_row)", csv_counts["sum_is_duplicate_row"], db_counts["sum_is_duplicate_row"])
    check("SUM(flag_zero_nights)", csv_counts["sum_flag_zero_nights"], db_counts["sum_flag_zero_nights"])
    check("MIN(arrival_date)", csv_counts["min_arrival_date"], db_counts["min_arrival_date"])
    check("MAX(arrival_date)", csv_counts["max_arrival_date"], db_counts["max_arrival_date"])

    for h in sorted(csv_cr.keys()):
        check(f"Cancellation Rate ({h})", f"{csv_cr[h]:.4f}", f"{db_cr.get(h, 0.0):.4f}")

    check("COUNT(agent IS NULL)", csv_counts["null_agent"], db_counts["null_agent"])
    check("COUNT(days_cancelled IS NULL)", csv_counts["null_days_cancelled"], db_counts["null_days_cancelled"])

    # Format table output
    df_results = pd.DataFrame(results)
    print(df_results.to_string(index=False))

    print("\n" + "=" * 80)
    if all_pass:
        print("ALL RECONCILIATION CHECKS PASSED.")
    else:
        print("ONE OR MORE RECONCILIATION CHECKS FAILED.", file=sys.stderr)
    print("=" * 80 + "\n")

    return all_pass


def main():
    success = load_and_reconcile()
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
