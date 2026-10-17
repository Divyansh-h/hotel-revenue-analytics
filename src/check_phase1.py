"""
Phase 1 Reconciliation Script
Recomputes Checks a, b, c, d, and f in pandas from data/processed/bookings_clean.csv
and compares them directly against live PostgreSQL query results.
Exits 0 if all checks PASS, 1 if any check FAILS.
"""

import sys
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.db import get_connection


def check_phase1() -> bool:
    csv_path = REPO_ROOT / "data" / "processed" / "bookings_clean.csv"
    if not csv_path.exists():
        print(f"Error: Processed CSV not found at {csv_path}", file=sys.stderr)
        return False

    print(f"Reading {csv_path} for Phase 1 reconciliation...")
    df = pd.read_csv(csv_path, low_memory=False)

    conn = get_connection()
    all_pass = True
    check_rows = []

    def record_check(label: str, csv_val, sql_val):
        nonlocal all_pass
        passed = (csv_val == sql_val)
        if not passed:
            all_pass = False
        status = "PASS" if passed else "FAIL"
        check_rows.append({
            "Check Item": label,
            "Pandas (CSV)": str(csv_val),
            "PostgreSQL": str(sql_val),
            "Status": status
        })

    # =========================================================================
    # Check a: Total Bookings and Bookings by Hotel
    # =========================================================================
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COALESCE(hotel, 'Total Portfolio'), COUNT(*)::bigint
            FROM hotel.bookings
            GROUP BY GROUPING SETS ((hotel), ())
            ORDER BY (hotel IS NULL), hotel;
        """)
        sql_a = dict(cur.fetchall())

    csv_total = len(df)
    csv_city = int((df["hotel"] == "City Hotel").sum())
    csv_resort = int((df["hotel"] == "Resort Hotel").sum())

    record_check("Check a: Total Portfolio Bookings", csv_total, sql_a.get("Total Portfolio"))
    record_check("Check a: City Hotel Bookings", csv_city, sql_a.get("City Hotel"))
    record_check("Check a: Resort Hotel Bookings", csv_resort, sql_a.get("Resort Hotel"))

    # =========================================================================
    # Check b: Cancellations, No-Shows, and Cancellation Rate by Hotel
    # =========================================================================
    with conn.cursor() as cur:
        cur.execute("""
            SELECT hotel, COUNT(*)::bigint, SUM(is_canceled)::bigint,
                   SUM(is_no_show)::bigint, ROUND(AVG(is_canceled)::numeric, 4)
            FROM hotel.bookings
            GROUP BY hotel
            ORDER BY hotel;
        """)
        sql_b = {r[0]: {"total": r[1], "cancels": r[2], "noshows": r[3], "rate": float(r[4])} for r in cur.fetchall()}

    for h in ["City Hotel", "Resort Hotel"]:
        df_h = df[df["hotel"] == h]
        csv_tot_h = len(df_h)
        csv_canc_h = int(df_h["is_canceled"].sum())
        csv_ns_h = int(df_h["is_no_show"].sum())
        csv_rate_h = round(float(df_h["is_canceled"].mean()), 4)

        b_data = sql_b.get(h, {})
        record_check(f"Check b: {h} Total Cancellations", csv_canc_h, b_data.get("cancels"))
        record_check(f"Check b: {h} Total No-Shows", csv_ns_h, b_data.get("noshows"))
        record_check(f"Check b: {h} Cancellation Rate", f"{csv_rate_h:.4f}", f"{b_data.get('rate', 0.0):.4f}")

    # =========================================================================
    # Check c: Bookings per arrival_month_start (26 months)
    # =========================================================================
    with conn.cursor() as cur:
        cur.execute("""
            SELECT arrival_month_start::text, COUNT(*)::bigint
            FROM hotel.bookings
            GROUP BY arrival_month_start
            ORDER BY arrival_month_start;
        """)
        sql_c = dict(cur.fetchall())

    csv_c = df.groupby("arrival_month_start").size().to_dict()
    record_check("Check c: Total Distinct Arrival Months", len(csv_c), len(sql_c))
    months_match = (csv_c == sql_c)
    record_check("Check c: All 26 Monthly Counts Match Exactly", True, months_match)

    # =========================================================================
    # Check d: Rows per lead_bucket (5 buckets, no NULL)
    # =========================================================================
    with conn.cursor() as cur:
        cur.execute("""
            SELECT lead_bucket, COUNT(*)::bigint
            FROM hotel.bookings
            GROUP BY lead_bucket, lead_bucket_order
            ORDER BY lead_bucket_order;
        """)
        sql_d = dict(cur.fetchall())

    csv_d = df["lead_bucket"].value_counts().to_dict()
    for b in ["0-7", "8-30", "31-90", "91-180", "181+"]:
        record_check(f"Check d: Lead Bucket '{b}' Count", csv_d.get(b), sql_d.get(b))

    # =========================================================================
    # Check f: Non-Cancelled Stays (total_nights > 0) Count and Nights Sum
    # =========================================================================
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)::bigint, SUM(total_nights)::bigint
            FROM hotel.bookings
            WHERE is_canceled = 0 AND total_nights > 0;
        """)
        sql_f = cur.fetchone()

    df_f = df[(df["is_canceled"] == 0) & (df["total_nights"] > 0)]
    csv_f_count = len(df_f)
    csv_f_nights = int(df_f["total_nights"].sum())

    record_check("Check f: Non-Cancelled Stays (total_nights > 0) Count", csv_f_count, sql_f[0])
    record_check("Check f: Non-Cancelled Stays Sum(total_nights)", csv_f_nights, sql_f[1])

    conn.close()

    # Display Results Table
    df_results = pd.DataFrame(check_rows)
    print("\n" + "=" * 80)
    print("PHASE 1 INTEGRITY RECONCILIATION: PANDAS vs SQL")
    print("=" * 80)
    print(df_results.to_string(index=False))

    print("\n" + "=" * 80)
    if all_pass:
        print("ALL PHASE 1 CHECKS PASSED.")
    else:
        print("ONE OR MORE CHECKS FAILED.", file=sys.stderr)
    print("=" * 80 + "\n")

    return all_pass


def main():
    success = check_phase1()
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
