"""
Phase 4 Power BI Star Schema Exporter: src/export_powerbi_model.py
Exports hotel.dim_date, hotel.dim_hotel, hotel.dim_profile, hotel.fact_bookings,
hotel.fact_stay_nights, and hotel.fact_capacity to powerbi/data/<name>.csv.
Requirements: UTF-8, header, ISO dates, '.' decimal, flags as 0/1, no index.
Validates row counts and asserts 0 NULL keys.
"""

import sys
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.db import get_engine

EXPORT_TABLES = [
    {
        "table": "dim_date",
        "expected_rows": 1096,
        "order_by": "date_key",
        "key_checks": ["date_key"]
    },
    {
        "table": "dim_hotel",
        "expected_rows": 2,
        "order_by": "hotel_key",
        "key_checks": ["hotel_key"]
    },
    {
        "table": "dim_profile",
        "expected_rows": 101,
        "order_by": "profile_key",
        "key_checks": ["profile_key"]
    },
    {
        "table": "fact_bookings",
        "expected_rows": 119388,
        "order_by": "booking_id",
        "key_checks": ["booking_id", "hotel_key", "profile_key", "arrival_date"]
    },
    {
        "table": "fact_stay_nights",
        "expected_rows": 248261,
        "order_by": "booking_id, stay_date",
        "key_checks": ["booking_id", "hotel_key", "profile_key", "stay_date"]
    },
    {
        "table": "fact_capacity",
        "expected_rows": 1524,
        "order_by": "hotel_key, date_key",
        "key_checks": ["hotel_key", "date_key"]
    }
]


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def export_powerbi_model() -> bool:
    output_dir = REPO_ROOT / "powerbi" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    engine = get_engine()
    all_passed = True
    summary_results = []

    print("=" * 95)
    print("EXPORTING POWER BI STAR SCHEMA DATA MODEL TO powerbi/data/")
    print("=" * 95)

    for item in EXPORT_TABLES:
        t_name = item["table"]
        exp_rows = item["expected_rows"]
        order_by = item["order_by"]
        key_checks = item["key_checks"]

        query = f"SELECT * FROM hotel.{t_name} ORDER BY {order_by};"
        df = pd.read_sql_query(query, engine)
        act_rows = len(df)

        # 1. Row count validation
        row_count_ok = (act_rows == exp_rows)
        if not row_count_ok:
            print(f"[FAIL] Row count mismatch on {t_name}: expected {exp_rows}, got {act_rows}")
            all_passed = False

        # 2. Key null checks
        null_keys_found = False
        for k in key_checks:
            null_count = df[k].isna().sum()
            if null_count > 0:
                print(f"[FAIL] Found {null_count} NULL keys in column '{k}' of table '{t_name}'!")
                null_keys_found = True
                all_passed = False

        # 3. Format date columns to strict ISO format YYYY-MM-DD
        for col in df.columns:
            if "date" in col.lower() or pd.api.types.is_datetime64_any_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
                except Exception:
                    pass

        # 4. Format boolean/flag columns to integer 0/1
        flag_cols = [
            "is_canceled", "is_no_show", "is_repeated_guest",
            "room_type_mismatch", "is_duplicate_row"
        ]
        for col in flag_cols:
            if col in df.columns:
                df[col] = df[col].astype(int)

        # 5. Format nullable integer columns to Int64 (avoid 56.0 / 5.0)
        nullable_int_cols = ["days_cancelled_before_arrival", "cancel_timing_order"]
        for col in nullable_int_cols:
            if col in df.columns:
                df[col] = df[col].astype("Int64")

        # 5. Export to CSV (UTF-8, header, ISO dates, '.' decimal, no index)
        csv_file = output_dir / f"{t_name}.csv"
        df.to_csv(
            csv_file,
            index=False,
            encoding="utf-8",
            date_format="%Y-%m-%d",
            decimal="."
        )

        file_size = csv_file.stat().st_size
        size_str = format_file_size(file_size)
        status = "PASS" if (row_count_ok and not null_keys_found) else "FAIL"

        summary_results.append({
            "table": t_name,
            "file": f"powerbi/data/{t_name}.csv",
            "rows": act_rows,
            "cols": len(df.columns),
            "size": size_str,
            "status": status
        })

    # Print summary table
    print(f"{'Status':<6} | {'Table Name':<18} | {'Rows':<9} | {'Cols':<5} | {'File Size':<11} | {'Output File'}")
    print("-" * 95)
    for res in summary_results:
        print(f"{res['status']:<6} | {res['table']:<18} | {res['rows']:<9} | {res['cols']:<5} | {res['size']:<11} | {res['file']}")
    print("-" * 95)

    if all_passed:
        print("ALL 6 POWER BI STAR SCHEMA CSVS EXPORTED AND VALIDATED SUCCESSFULLY [PASS]")
    else:
        print("VALIDATION FAILURES DETECTED IN POWER BI EXPORT [FAIL]")

    print("=" * 95)
    return all_passed


def main():
    ok = export_powerbi_model()
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
