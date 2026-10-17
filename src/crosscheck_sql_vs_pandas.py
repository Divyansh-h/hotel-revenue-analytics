"""
Independent Cross-Check: PostgreSQL SQL Views vs Pandas Direct Recomputation
Recomputes stay-night and booking metrics from data/processed/bookings_clean.csv with NO SQL.
Compares with data/outputs/v_monthly_kpis.csv and data/outputs/v_booking_trends.csv.
Requirements:
  - Counts must match exactly
  - Percentages and money within 0.01
  - Prints PASS or FAIL per metric with number of rows compared and worst difference.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_crosscheck() -> bool:
    print("=" * 85)
    print("PHASE 2 INDEPENDENT CROSS-CHECK: PANDAS vs SQL EXPORTS")
    print("=" * 85)

    # 1. Load Assumptions
    assumptions_path = REPO_ROOT / "config" / "assumptions.yml"
    if not assumptions_path.exists():
        print(f"Error: Assumptions file not found at {assumptions_path}", file=sys.stderr)
        return False

    with open(assumptions_path, "r", encoding="utf-8") as f:
        assump = yaml.safe_load(f)

    w_start = pd.to_datetime(assump["window"]["start"])
    w_end = pd.to_datetime(assump["window"]["end"])
    capacities = {h: assump["hotels"][h]["capacity"] for h in assump["hotels"]}

    print(f"Loaded Reliable Window: {w_start.strftime('%Y-%m-%d')} to {w_end.strftime('%Y-%m-%d')}")
    print(f"Loaded Derived Capacities: {capacities}")

    # 2. Load Processed Clean Bookings
    clean_csv_path = REPO_ROOT / "data" / "processed" / "bookings_clean.csv"
    if not clean_csv_path.exists():
        print(f"Error: Processed bookings not found at {clean_csv_path}", file=sys.stderr)
        return False

    df_clean = pd.read_csv(clean_csv_path, low_memory=False)
    print(f"Loaded {len(df_clean):,} clean rows from {clean_csv_path}")

    # -------------------------------------------------------------------------
    # PART A: STAY NIGHTS RECOMPUTATION (v_monthly_kpis.csv)
    # -------------------------------------------------------------------------
    print("\nRecomputing stay-night metrics via day-offset explosion in NumPy/Pandas...")
    non_canc = df_clean[(df_clean["is_canceled"] == 0) & (df_clean["total_nights"] > 0)].copy()
    non_canc["arr_dt"] = pd.to_datetime(non_canc["arrival_date"])

    repeats = non_canc["total_nights"].values
    offsets = np.concatenate([np.arange(n) for n in repeats])

    df_stay_nights = pd.DataFrame({
        "hotel": np.repeat(non_canc["hotel"].values, repeats),
        "adr": np.repeat(non_canc["adr"].values, repeats),
        "stay_date": np.repeat(non_canc["arr_dt"].values, repeats) + pd.to_timedelta(offsets, unit="D")
    })

    # Restrict to reliable window
    df_stay_window = df_stay_nights[
        (df_stay_nights["stay_date"] >= w_start) & (df_stay_nights["stay_date"] <= w_end)
    ].copy()
    df_stay_window["month_start"] = (
        df_stay_window["stay_date"].dt.to_period("M").dt.to_timestamp().dt.strftime("%Y-%m-%d")
    )

    print(f"Total stay-nights in window: {len(df_stay_window):,} (across both hotels)")

    # Aggregate monthly room nights and revenue
    pd_monthly_kpis = df_stay_window.groupby(["hotel", "month_start"]).agg(
        room_nights_sold=("adr", "count"),
        room_revenue=("adr", "sum")
    ).reset_index()

    # Calculate days in month within window
    calendar_dates = pd.date_range(w_start, w_end, freq="D")
    cal_df = pd.DataFrame({"date": calendar_dates})
    cal_df["month_start"] = cal_df["date"].dt.to_period("M").dt.to_timestamp().dt.strftime("%Y-%m-%d")
    days_per_month = cal_df.groupby("month_start").size().to_dict()

    pd_monthly_kpis["days_in_month"] = pd_monthly_kpis["month_start"].map(days_per_month)
    pd_monthly_kpis["capacity"] = pd_monthly_kpis["hotel"].map(capacities)
    pd_monthly_kpis["room_nights_available"] = pd_monthly_kpis["days_in_month"] * pd_monthly_kpis["capacity"]

    pd_monthly_kpis["occupancy_pct"] = (
        100.0 * pd_monthly_kpis["room_nights_sold"] / pd_monthly_kpis["room_nights_available"]
    ).round(2)
    pd_monthly_kpis["adr"] = (pd_monthly_kpis["room_revenue"] / pd_monthly_kpis["room_nights_sold"]).round(2)
    pd_monthly_kpis["revpar"] = (pd_monthly_kpis["room_revenue"] / pd_monthly_kpis["room_nights_available"]).round(2)
    pd_monthly_kpis["room_revenue"] = pd_monthly_kpis["room_revenue"].round(2)

    # Load SQL Export: v_monthly_kpis.csv
    sql_monthly_path = REPO_ROOT / "data" / "outputs" / "v_monthly_kpis.csv"
    if not sql_monthly_path.exists():
        print(f"Error: SQL output {sql_monthly_path} does not exist.", file=sys.stderr)
        return False

    sql_monthly = pd.read_csv(sql_monthly_path)
    merged_kpis = pd.merge(
        pd_monthly_kpis, sql_monthly,
        on=["hotel", "month_start"],
        suffixes=("_pandas", "_sql")
    )

    all_pass = True
    results = []

    kpi_checks = [
        ("v_monthly_kpis: room_nights_sold", "room_nights_sold", True),
        ("v_monthly_kpis: room_nights_available", "room_nights_available", True),
        ("v_monthly_kpis: room_revenue ($)", "room_revenue", False),
        ("v_monthly_kpis: occupancy_pct (%)", "occupancy_pct", False),
        ("v_monthly_kpis: adr ($)", "adr", False),
        ("v_monthly_kpis: revpar ($)", "revpar", False),
    ]

    for label, col, is_int in kpi_checks:
        diff_series = (merged_kpis[f"{col}_pandas"] - merged_kpis[f"{col}_sql"]).abs()
        worst_diff = diff_series.max()
        if is_int:
            passed = (worst_diff == 0)
        else:
            passed = (worst_diff <= 0.01)

        if not passed:
            all_pass = False

        results.append({
            "Metric": label,
            "Rows Compared": len(merged_kpis),
            "Worst Difference": f"{worst_diff:.4f}" if not is_int else f"{int(worst_diff)}",
            "Threshold": "Exact (0)" if is_int else "<= 0.01",
            "Status": "PASS" if passed else "FAIL"
        })

    # -------------------------------------------------------------------------
    # PART B: BOOKING TRENDS RECOMPUTATION (v_booking_trends.csv)
    # -------------------------------------------------------------------------
    print("\nRecomputing monthly booking trends directly from bookings_clean.csv...")
    df_clean["arr_month"] = pd.to_datetime(df_clean["arrival_month_start"]).dt.strftime("%Y-%m-%d")

    pd_trends = df_clean.groupby(["hotel", "arr_month"]).agg(
        bookings=("is_canceled", "count"),
        cancellations=("is_canceled", "sum")
    ).reset_index()

    pd_trends["cancel_rate_pct"] = (
        100.0 * pd_trends["cancellations"] / pd_trends["bookings"]
    ).round(1)

    sql_trends_path = REPO_ROOT / "data" / "outputs" / "v_booking_trends.csv"
    if not sql_trends_path.exists():
        print(f"Error: SQL output {sql_trends_path} does not exist.", file=sys.stderr)
        return False

    sql_trends = pd.read_csv(sql_trends_path)
    merged_trends = pd.merge(
        pd_trends, sql_trends,
        left_on=["hotel", "arr_month"],
        right_on=["hotel", "arrival_month_start"],
        suffixes=("_pandas", "_sql")
    )

    trend_checks = [
        ("v_booking_trends: bookings", "bookings", True),
        ("v_booking_trends: cancellations", "cancellations", True),
        ("v_booking_trends: cancel_rate_pct (%)", "cancel_rate_pct", False),
    ]

    for label, col, is_int in trend_checks:
        diff_series = (merged_trends[f"{col}_pandas"] - merged_trends[f"{col}_sql"]).abs()
        worst_diff = diff_series.max()
        if is_int:
            passed = (worst_diff == 0)
        else:
            passed = (worst_diff <= 0.01)

        if not passed:
            all_pass = False

        results.append({
            "Metric": label,
            "Rows Compared": len(merged_trends),
            "Worst Difference": f"{worst_diff:.4f}" if not is_int else f"{int(worst_diff)}",
            "Threshold": "Exact (0)" if is_int else "<= 0.01",
            "Status": "PASS" if passed else "FAIL"
        })

    # -------------------------------------------------------------------------
    # DISPLAY SUMMARY TABLE
    # -------------------------------------------------------------------------
    res_df = pd.DataFrame(results)
    print("\n" + "=" * 85)
    print("CROSS-CHECK RESULTS SUMMARY")
    print("=" * 85)
    print(res_df.to_string(index=False))

    print("\n" + "=" * 85)
    if all_pass:
        print("ALL INDEPENDENT PANDAS vs SQL CROSS-CHECKS PASSED.")
    else:
        print("ONE OR MORE CHECKS FAILED.", file=sys.stderr)
    print("=" * 85 + "\n")

    return all_pass


def main():
    success = run_crosscheck()
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
