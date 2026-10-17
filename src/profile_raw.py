"""
Raw Dataset Profiling Script
Reads data/raw/hotel_bookings.csv (read-only, no modifications).
Produces 6 profile tables in reports/tables/ with prefix profile_:
  1. profile_missing_values.csv
  2. profile_categorical_distributions.csv & profile_top_20_countries.csv
  3. profile_numeric_summary.csv
  4. profile_issues.csv & profile_adr_zero_by_segment.csv
  5. profile_adr_extremes.csv
"""

from pathlib import Path
import pandas as pd
import numpy as np


def profile_raw_dataset():
    repo_root = Path(__file__).resolve().parent.parent
    raw_path = repo_root / "data" / "raw" / "hotel_bookings.csv"
    tables_dir = repo_root / "reports" / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading raw dataset from {raw_path}...")
    df = pd.read_csv(raw_path)
    n_rows = len(df)
    n_cols = len(df.columns)
    print(f"Loaded {n_rows:,} rows and {n_cols} columns.\n")

    # =========================================================================
    # 1. Missing Values (count and percent for every column)
    # =========================================================================
    missing_list = []
    for col in df.columns:
        m_count = int(df[col].isna().sum())
        m_pct = (m_count / n_rows) * 100
        missing_list.append({
            "column_name": col,
            "missing_count": m_count,
            "total_rows": n_rows,
            "percent_missing": round(m_pct, 4)
        })
    df_missing = pd.DataFrame(missing_list)
    missing_csv = tables_dir / "profile_missing_values.csv"
    df_missing.to_csv(missing_csv, index=False)
    print(f"Saved: {missing_csv.name}")

    # =========================================================================
    # 2. Categorical Value Counts with Percent
    # =========================================================================
    cat_cols = [
        "hotel", "meal", "market_segment", "distribution_channel",
        "deposit_type", "customer_type", "reserved_room_type",
        "assigned_room_type", "reservation_status", "is_repeated_guest"
    ]

    cat_list = []
    for col in cat_cols:
        vc = df[col].value_counts(dropna=False)
        for val, count in vc.items():
            cat_list.append({
                "column_name": col,
                "value": str(val),
                "count": int(count),
                "percent": round((count / n_rows) * 100, 4)
            })
    df_cat = pd.DataFrame(cat_list)
    cat_csv = tables_dir / "profile_categorical_distributions.csv"
    df_cat.to_csv(cat_csv, index=False)
    print(f"Saved: {cat_csv.name}")

    # Top 20 countries
    top_20_vc = df["country"].value_counts(dropna=False).head(20)
    country_list = []
    for rank, (country, count) in enumerate(top_20_vc.items(), 1):
        country_list.append({
            "rank": rank,
            "country": str(country),
            "count": int(count),
            "percent": round((count / n_rows) * 100, 4)
        })
    df_top_countries = pd.DataFrame(country_list)
    top_countries_csv = tables_dir / "profile_top_20_countries.csv"
    df_top_countries.to_csv(top_countries_csv, index=False)
    print(f"Saved: {top_countries_csv.name}")

    # =========================================================================
    # 3. Numeric Summary (count, mean, std, min, 1%, 25%, 50%, 75%, 99%, max)
    # =========================================================================
    num_cols = [
        "lead_time", "adr", "adults", "children", "babies",
        "stays_in_weekend_nights", "stays_in_week_nights",
        "previous_cancellations", "booking_changes", "days_in_waiting_list"
    ]

    num_summary = []
    for col in num_cols:
        s = df[col].dropna()
        num_summary.append({
            "column_name": col,
            "count": int(s.count()),
            "mean": round(float(s.mean()), 4),
            "std": round(float(s.std()), 4),
            "min": round(float(s.min()), 4),
            "p01": round(float(s.quantile(0.01)), 4),
            "p25": round(float(s.quantile(0.25)), 4),
            "p50": round(float(s.quantile(0.50)), 4),
            "p75": round(float(s.quantile(0.75)), 4),
            "p99": round(float(s.quantile(0.99)), 4),
            "max": round(float(s.max()), 4)
        })
    df_num = pd.DataFrame(num_summary)
    num_csv = tables_dir / "profile_numeric_summary.csv"
    df_num.to_csv(num_csv, index=False)
    print(f"Saved: {num_csv.name}")

    # =========================================================================
    # 4. Issue Counts
    # =========================================================================
    # adr issues
    adr_neg = int((df["adr"] < 0).sum())
    adr_gt1000 = int((df["adr"] > 1000).sum())
    adr_zero = int((df["adr"] == 0).sum())

    # total nights = 0
    total_nights = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    zero_nights = int((total_nights == 0).sum())

    # total guests = 0 (children NaN treated as 0)
    children_filled = df["children"].fillna(0)
    total_guests = df["adults"] + children_filled + df["babies"]
    zero_guests = int((total_guests == 0).sum())

    # exact duplicate rows across all 32 columns
    exact_dups = int(df.duplicated().sum())

    # reservation_status is Canceled and reservation_status_date > arrival_date
    month_map = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }
    arrival_dates = pd.to_datetime(pd.DataFrame({
        "year": df["arrival_date_year"],
        "month": df["arrival_date_month"].map(month_map),
        "day": df["arrival_date_day_of_month"]
    }))
    res_status_dates = pd.to_datetime(df["reservation_status_date"])
    canceled_mask = (df["reservation_status"] == "Canceled")
    cancel_after_arrival = int((canceled_mask & (res_status_dates > arrival_dates)).sum())

    # assigned_room_type != reserved_room_type
    room_mismatch = int((df["assigned_room_type"] != df["reserved_room_type"]).sum())

    # missing values issues
    company_null = int(df["company"].isna().sum())
    agent_null = int(df["agent"].isna().sum())
    country_null = int(df["country"].isna().sum())
    children_null = int(df["children"].isna().sum())

    # undefined category issues
    market_segment_undefined = int((df["market_segment"] == "Undefined").sum())
    distribution_channel_undefined = int((df["distribution_channel"] == "Undefined").sum())

    issues = [
        {
            "issue": "Negative ADR (adr < 0)",
            "columns": "adr",
            "rows_affected": adr_neg,
            "percent_of_data": round((adr_neg / n_rows) * 100, 4),
            "details": "Single row with adr = -6.38"
        },
        {
            "issue": "Extreme High ADR (adr > 1000)",
            "columns": "adr",
            "rows_affected": adr_gt1000,
            "percent_of_data": round((adr_gt1000 / n_rows) * 100, 4),
            "details": "Single row with adr = 5400.0"
        },
        {
            "issue": "Zero ADR (adr = 0)",
            "columns": "adr, market_segment",
            "rows_affected": adr_zero,
            "percent_of_data": round((adr_zero / n_rows) * 100, 4),
            "details": "Non-revenue stays (Complementary, promotions, house guests)"
        },
        {
            "issue": "Zero Stay Nights (weekend + week nights = 0)",
            "columns": "stays_in_weekend_nights, stays_in_week_nights",
            "rows_affected": zero_nights,
            "percent_of_data": round((zero_nights / n_rows) * 100, 4),
            "details": "Bookings with 0 duration (cancelled or day-use)"
        },
        {
            "issue": "Zero Total Guests (adults + children + babies = 0)",
            "columns": "adults, children, babies",
            "rows_affected": zero_guests,
            "percent_of_data": round((zero_guests / n_rows) * 100, 4),
            "details": "Bookings registered with zero guest occupants"
        },
        {
            "issue": "Exact Duplicate Rows (all 32 raw columns)",
            "columns": "all 32 columns",
            "rows_affected": exact_dups,
            "percent_of_data": round((exact_dups / n_rows) * 100, 4),
            "details": "Repeated rows without unique booking identifier"
        },
        {
            "issue": "Canceled Date Later Than Arrival Date",
            "columns": "reservation_status, reservation_status_date, arrival_date_*",
            "rows_affected": cancel_after_arrival,
            "percent_of_data": round((cancel_after_arrival / n_rows) * 100, 4),
            "details": "Cancellations recorded with status date > arrival date"
        },
        {
            "issue": "Room Type Mismatch (assigned <> reserved)",
            "columns": "reserved_room_type, assigned_room_type",
            "rows_affected": room_mismatch,
            "percent_of_data": round((room_mismatch / n_rows) * 100, 4),
            "details": "Operational reassignments / room upgrades"
        },
        {
            "issue": "Missing Company ID",
            "columns": "company",
            "rows_affected": company_null,
            "percent_of_data": round((company_null / n_rows) * 100, 4),
            "details": "94.31% missing corporate identifier"
        },
        {
            "issue": "Missing Agent ID",
            "columns": "agent",
            "rows_affected": agent_null,
            "percent_of_data": round((agent_null / n_rows) * 100, 4),
            "details": "13.69% direct or non-agent bookings"
        },
        {
            "issue": "Missing Country of Origin",
            "columns": "country",
            "rows_affected": country_null,
            "percent_of_data": round((country_null / n_rows) * 100, 4),
            "details": "488 bookings without customer country code"
        },
        {
            "issue": "Missing Children Count",
            "columns": "children",
            "rows_affected": children_null,
            "percent_of_data": round((children_null / n_rows) * 100, 4),
            "details": "4 bookings with NaN children"
        },
        {
            "issue": "Undefined Market Segment",
            "columns": "market_segment",
            "rows_affected": market_segment_undefined,
            "percent_of_data": round((market_segment_undefined / n_rows) * 100, 4),
            "details": "Categorical 'Undefined' value in market segment"
        },
        {
            "issue": "Undefined Distribution Channel",
            "columns": "distribution_channel",
            "rows_affected": distribution_channel_undefined,
            "percent_of_data": round((distribution_channel_undefined / n_rows) * 100, 4),
            "details": "Categorical 'Undefined' value in distribution channel"
        }
    ]
    df_issues = pd.DataFrame(issues)
    issues_csv = tables_dir / "profile_issues.csv"
    df_issues.to_csv(issues_csv, index=False)
    print(f"Saved: {issues_csv.name}")

    # adr = 0 breakdown by market segment
    df_zero_adr = df[df["adr"] == 0]
    seg_counts = df_zero_adr["market_segment"].value_counts()
    seg_breakdown = []
    for seg, cnt in seg_counts.items():
        total_in_seg = int((df["market_segment"] == seg).sum())
        seg_breakdown.append({
            "market_segment": seg,
            "adr_zero_count": int(cnt),
            "total_segment_bookings": total_in_seg,
            "percent_within_segment": round((cnt / total_in_seg) * 100, 4),
            "percent_of_all_zero_adr": round((cnt / adr_zero) * 100, 4)
        })
    df_seg_breakdown = pd.DataFrame(seg_breakdown)
    adr_zero_csv = tables_dir / "profile_adr_zero_by_segment.csv"
    df_seg_breakdown.to_csv(adr_zero_csv, index=False)
    print(f"Saved: {adr_zero_csv.name}")

    # =========================================================================
    # 5. ADR Extremes (5 lowest and 5 highest)
    # =========================================================================
    lowest_5 = df.nsmallest(5, "adr")[["hotel", "market_segment", "customer_type", "adr"]].copy()
    lowest_5["rank_type"] = "Lowest"
    lowest_5["rank"] = range(1, 6)
    lowest_5["raw_row_index"] = lowest_5.index

    highest_5 = df.nlargest(5, "adr")[["hotel", "market_segment", "customer_type", "adr"]].copy()
    highest_5["rank_type"] = "Highest"
    highest_5["rank"] = range(1, 6)
    highest_5["raw_row_index"] = highest_5.index

    df_extremes = pd.concat([lowest_5, highest_5], ignore_index=True)[[
        "rank_type", "rank", "raw_row_index", "hotel", "market_segment", "customer_type", "adr"
    ]]
    extremes_csv = tables_dir / "profile_adr_extremes.csv"
    df_extremes.to_csv(extremes_csv, index=False)
    print(f"Saved: {extremes_csv.name}")

    print("\nPROFILING COMPLETE. All tables successfully written.\n")


if __name__ == "__main__":
    profile_raw_dataset()
