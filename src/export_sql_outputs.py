"""
Export Phase 2 PostgreSQL analytical views and tables to data/outputs/<name>.csv
Requirements: UTF-8, header, ISO dates, no index, '.' decimal.
Prints rows written per file.
"""

import sys
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.db import get_engine

EXPORT_OBJECTS = [
    "v_monthly_kpis",
    "v_hotel_totals",
    "v_yearly_kpis",
    "v_booking_trends",
    "v_cancellation_drivers",
    "v_cancel_timing",
    "v_lead_deposit_matrix",
    "v_late_cancel_revenue_at_risk",
    "v_segment_performance",
    "v_channel_performance",
    "v_segment_channel_matrix",
    "v_seasonality",
    "v_overbooking_buffer",
    "v_room_mismatch",
    "capacity",
    "capacity_derivation",
    "daily_performance"
]


def export_sql_outputs() -> dict:
    output_dir = REPO_ROOT / "data" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    engine = get_engine()
    results = {}

    print(f"Exporting {len(EXPORT_OBJECTS)} database objects to {output_dir}...")
    print("=" * 70)
    print(f"{'Object Name':<35} | {'Rows Written':<15} | {'File Path'}")
    print("-" * 70)

    for obj in EXPORT_OBJECTS:
        query = f"SELECT * FROM hotel.{obj};"
        df = pd.read_sql_query(query, engine)

        # Ensure all date columns are formatted as ISO strings
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]) or "date" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
                except Exception:
                    pass

        file_path = output_dir / f"{obj}.csv"
        df.to_csv(file_path, index=False, encoding="utf-8", date_format="%Y-%m-%d", decimal=".")
        results[obj] = len(df)
        print(f"{obj:<35} | {len(df):<15} | data/outputs/{obj}.csv")

    print("=" * 70)
    print("All objects successfully exported.")
    return results


def main():
    export_sql_outputs()


if __name__ == "__main__":
    main()
