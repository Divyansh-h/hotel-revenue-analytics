"""
Hotel Booking Demand Data Cleaning Pipeline
Authoritative cleaning decisions D1 through D12 from PROJECT_CONTEXT.md.

Full Pipeline Implementation:
  - Step A: load_raw() -> D1, D7
  - Step B: build_dates() -> D2, D4
  - Step C: build_measures() -> D3, D4
  - Step D: exclude_outliers() -> D5
  - Step E: build_flags_and_categories() -> D6, D8, D9, D10, D11, D12
  - Step F: finalize_schema() -> Final columns selection and ordering
  - Step G: save_processed() -> Export to data/processed/
"""

import argparse
from pathlib import Path
from typing import Tuple
import numpy as np
import pandas as pd

# Raw columns list before any additions or drops
RAW_COLUMNS = [
    "hotel", "is_canceled", "lead_time", "arrival_date_year", "arrival_date_month",
    "arrival_date_week_number", "arrival_date_day_of_month", "stays_in_weekend_nights",
    "stays_in_week_nights", "adults", "children", "babies", "meal", "country",
    "market_segment", "distribution_channel", "is_repeated_guest", "previous_cancellations",
    "previous_bookings_not_canceled", "reserved_room_type", "assigned_room_type",
    "booking_changes", "deposit_type", "agent", "company", "days_in_waiting_list",
    "customer_type", "adr", "required_car_parking_spaces", "total_of_special_requests",
    "reservation_status", "reservation_status_date"
]

# Authoritative Final Columns in exact names and order from PROJECT_CONTEXT.md
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

# Explicit month name to number mapping (never locale dependent)
MONTH_MAP = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

LEAD_BINS = [-1, 7, 30, 90, 180, 100000]
LEAD_LABELS = ["0-7", "8-30", "31-90", "91-180", "181+"]
LEAD_ORDER_MAP = {"0-7": 1, "8-30": 2, "31-90": 3, "91-180": 4, "181+": 5}


def load_raw(raw_path: Path) -> pd.DataFrame:
    """
    Step A: Read data/raw/hotel_bookings.csv.
    - Add booking_id = 1-based row number (D1) before anything else.
    - Immediately, on the 32 ORIGINAL columns only, compute
      is_duplicate_row = duplicated(subset=<the 32 raw columns>, keep='first')
      as 0/1 integers (D7).
    - Assert booking_id is unique and row count is unchanged.
    """
    print(f"Loading raw data from: {raw_path}")
    df = pd.read_csv(raw_path)
    initial_row_count = len(df)
    assert initial_row_count == 119390, f"Expected 119,390 rows, got {initial_row_count:,}"
    assert list(df.columns) == RAW_COLUMNS, "Raw columns do not match expected RAW_COLUMNS schema."

    # D1: Add booking_id = 1-based row number before anything else
    df.insert(0, "booking_id", range(1, initial_row_count + 1))

    # D7: Immediately compute is_duplicate_row on the 32 ORIGINAL columns only
    df["is_duplicate_row"] = df[RAW_COLUMNS].duplicated(keep="first").astype(int)

    # Post-Step A Assertions
    assert len(df) == initial_row_count, f"Row count changed after Step A: {len(df)} vs {initial_row_count}"
    assert df["booking_id"].nunique() == initial_row_count, "booking_id values are not strictly unique!"
    assert df["booking_id"].min() == 1 and df["booking_id"].max() == initial_row_count, "booking_id is not 1-based sequential integers!"
    assert set(df["is_duplicate_row"].unique()).issubset({0, 1}), "is_duplicate_row has values other than 0 and 1"

    num_dups = df["is_duplicate_row"].sum()
    print(f"Step A Complete: Added booking_id (1 to {initial_row_count:,}) and flagged {num_dups:,} duplicate rows.")
    return df


def build_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step B: Build date fields.
    - Build arrival_date with explicit month mapping dictionary.
    - Add arrival_year, arrival_month_num, arrival_month_start (first day of arrival month),
      checkout_date and booking_date.
    - Convert reservation_status_date to a real date (D2, D4).
    - Assert there are no NaT values and validate date ranges.
    """
    initial_row_count = len(df)

    month_num_series = df["arrival_date_month"].map(MONTH_MAP)
    assert not month_num_series.isna().any(), "Unmapped month names encountered in arrival_date_month!"

    arrival_dt = pd.to_datetime(pd.DataFrame({
        "year": df["arrival_date_year"],
        "month": month_num_series,
        "day": df["arrival_date_day_of_month"]
    }))
    df["arrival_date"] = arrival_dt

    df["arrival_year"] = arrival_dt.dt.year.astype(int)
    df["arrival_month_num"] = arrival_dt.dt.month.astype(int)

    df["arrival_month_start"] = pd.to_datetime(pd.DataFrame({
        "year": df["arrival_year"],
        "month": df["arrival_month_num"],
        "day": 1
    }))

    tot_nights = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    df["checkout_date"] = arrival_dt + pd.to_timedelta(tot_nights, unit="D")
    df["booking_date"] = arrival_dt - pd.to_timedelta(df["lead_time"], unit="D")
    df["reservation_status_date"] = pd.to_datetime(df["reservation_status_date"])

    # Post-Step B Assertions
    date_cols = [
        "arrival_date", "checkout_date", "booking_date",
        "arrival_month_start", "reservation_status_date"
    ]
    for col in date_cols:
        assert not df[col].isna().any(), f"NaT detected in date column: {col}"

    assert len(df) == initial_row_count, f"Row count changed after Step B: {len(df)} vs {initial_row_count}"
    assert df["arrival_date"].min() == pd.Timestamp("2015-07-01"), f"Unexpected min arrival_date: {df['arrival_date'].min()}"
    assert df["arrival_date"].max() == pd.Timestamp("2017-08-31"), f"Unexpected max arrival_date: {df['arrival_date'].max()}"
    assert (df["checkout_date"] >= df["arrival_date"]).all(), "Detected checkout_date earlier than arrival_date!"
    assert (df["booking_date"] <= df["arrival_date"]).all(), "Detected booking_date later than arrival_date!"
    assert (df["arrival_month_start"] <= df["arrival_date"]).all(), "Detected arrival_month_start after arrival_date!"

    print("Step B Complete: Built arrival_date, arrival_year, arrival_month_num, arrival_month_start, checkout_date, booking_date, and converted reservation_status_date.")
    return df


def build_measures(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step C: Impute missing values and build core numeric measures.
    - children NaN -> 0 (integer) (D3)
    - country NaN -> 'Unknown' (D3)
    - add total_nights = stays_in_weekend_nights + stays_in_week_nights (D4)
    - add total_guests = adults + children + babies (D4)
    - add room_revenue = adr * total_nights (D4)
    - keep agent as nullable integer (Int64) (D3)
    - drop company and arrival_date_week_number (D3)
    """
    initial_row_count = len(df)

    df["children"] = df["children"].fillna(0).astype(int)
    df["country"] = df["country"].fillna("Unknown")
    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    df["total_guests"] = df["adults"] + df["children"] + df["babies"]
    df["room_revenue"] = (df["adr"] * df["total_nights"]).round(2)
    df["agent"] = df["agent"].astype("Int64")
    df = df.drop(columns=["company", "arrival_date_week_number"])

    # Post-Step C Assertions
    assert len(df) == initial_row_count, f"Row count changed after Step C: {len(df)} vs {initial_row_count}"
    assert (df["total_nights"] == (df["stays_in_weekend_nights"] + df["stays_in_week_nights"])).all(), "total_nights check failed!"
    assert (df["total_guests"] == (df["adults"] + df["children"] + df["babies"])).all(), "total_guests check failed!"
    assert np.isclose(df["room_revenue"], df["adr"] * df["total_nights"]).all(), "room_revenue calculation mismatch!"
    assert "company" not in df.columns, "'company' column still present in dataframe!"
    assert "arrival_date_week_number" not in df.columns, "'arrival_date_week_number' column still present!"
    assert not df["children"].isna().any(), "children column contains NaNs after imputation!"
    assert df["children"].dtype in [int, np.int64, np.int32], f"children is not integer dtype: {df['children'].dtype}"
    assert not df["country"].isna().any(), "country column contains NaNs after imputation!"
    assert str(df["agent"].dtype) == "Int64", f"agent column is not Int64: {df['agent'].dtype}"

    print("Step C Complete: Imputed children & country, computed total_nights, total_guests, room_revenue; dropped company & arrival_date_week_number.")
    return df


def exclude_outliers(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Step D: Exclude ADR outliers (D5).
    - Rows with adr < 0 or adr > 1000 are EXCLUDED from analytical table.
    - Expected: exactly 2 rows (one negative and one around 5400).
    - If count != 2, STOP immediately.
    - Add excluded_reason column and return (clean_df, excluded_df).
    """
    outlier_mask = (df["adr"] < 0) | (df["adr"] > 1000)
    outlier_count = int(outlier_mask.sum())

    if outlier_count != 2:
        raise ValueError(f"D5 check failed: Expected exactly 2 outliers (adr < 0 or > 1000), found {outlier_count}!")

    df_excluded = df[outlier_mask].copy()
    df_excluded["excluded_reason"] = np.where(
        df_excluded["adr"] < 0,
        f"adr < 0 (value: {df_excluded['adr'].min()})",
        f"adr > 1000 (value: {df_excluded['adr'].max()})"
    )

    df_clean = df[~outlier_mask].copy()

    assert len(df_clean) + len(df_excluded) == len(df), "Row count mismatch after exclusion!"
    assert len(df_excluded) == 2, f"Expected 2 excluded rows, got {len(df_excluded)}"
    assert (df_clean["adr"] >= 0).all() and (df_clean["adr"] <= 1000).all(), "Clean dataframe still contains ADR outliers!"

    print(f"Step D Complete: Identified exactly {outlier_count} ADR outliers; partitioned into clean ({len(df_clean):,}) and excluded ({len(df_excluded):,}) sets.")
    return df_clean, df_excluded


def build_flags_and_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step E: Build categorical flags and business logic fields.
    - is_canceled: 1 covers Canceled & No-Show (D8)
    - is_no_show: 1 only for No-Show (D8)
    - lead_bucket and lead_bucket_order (D9)
    - room_type_mismatch (D10)
    - days_cancelled_before_arrival (D11)
    - flag_zero_nights, flag_zero_guests (D6)
    - D12: all flag/boolean columns stored as 0/1 integers
    """
    # D8: is_canceled and is_no_show
    df["is_no_show"] = (df["reservation_status"] == "No-Show").astype(int)
    df["is_canceled"] = df["reservation_status"].isin(["Canceled", "No-Show"]).astype(int)

    # D9: lead_bucket and lead_bucket_order
    df["lead_bucket"] = pd.cut(df["lead_time"], bins=LEAD_BINS, labels=LEAD_LABELS).astype(str)
    df["lead_bucket_order"] = df["lead_bucket"].map(LEAD_ORDER_MAP).astype(int)

    # D10: room_type_mismatch = 1 when assigned <> reserved, else 0
    df["room_type_mismatch"] = (df["assigned_room_type"] != df["reserved_room_type"]).astype(int)

    # D11: days_cancelled_before_arrival = arrival_date - reservation_status_date, only for 'Canceled', else NULL
    days_cancel = (df["arrival_date"] - df["reservation_status_date"]).dt.days
    df["days_cancelled_before_arrival"] = np.where(
        df["reservation_status"] == "Canceled",
        days_cancel,
        pd.NA
    )
    df["days_cancelled_before_arrival"] = df["days_cancelled_before_arrival"].astype("Int64")

    # D6: flag_zero_nights and flag_zero_guests
    df["flag_zero_nights"] = (df["total_nights"] == 0).astype(int)
    df["flag_zero_guests"] = (df["total_guests"] == 0).astype(int)

    # D12 Assertions: ensure all flag columns are stored as 0/1 integers
    flag_cols = [
        "is_canceled", "is_no_show", "is_repeated_guest",
        "room_type_mismatch", "flag_zero_nights", "flag_zero_guests", "is_duplicate_row"
    ]
    for col in flag_cols:
        assert set(df[col].unique()).issubset({0, 1}), f"Column {col} contains values other than 0 or 1!"
        assert df[col].dtype in [int, np.int64, np.int32], f"Column {col} is not integer dtype!"

    assert df[df["reservation_status"] != "Canceled"]["days_cancelled_before_arrival"].isna().all(), (
        "Non-canceled bookings must have NULL days_cancelled_before_arrival!"
    )
    assert not df[df["reservation_status"] == "Canceled"]["days_cancelled_before_arrival"].isna().any(), (
        "Canceled bookings must have valid integer days_cancelled_before_arrival!"
    )

    print("Step E Complete: Built status flags, lead buckets, room mismatch, cancellation lead, and zero night/guest flags.")
    return df


def finalize_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step F: Reorder and project final columns as mandated by PROJECT_CONTEXT.md.
    Formats dates to ISO string format (YYYY-MM-DD).
    """
    date_cols = [
        "reservation_status_date", "booking_date", "arrival_date",
        "arrival_month_start", "checkout_date"
    ]
    for col in date_cols:
        df[col] = df[col].dt.strftime("%Y-%m-%d")

    df_final = df[FINAL_COLUMNS].copy()
    assert list(df_final.columns) == FINAL_COLUMNS, "Final column list or order does not match PROJECT_CONTEXT.md!"
    print(f"Step F Complete: Finalized schema with exact {len(FINAL_COLUMNS)} columns.")
    return df_final


def save_processed(df_clean: pd.DataFrame, df_excluded: pd.DataFrame, processed_dir: Path):
    """
    Step G: Export clean analytical dataset and excluded rows.
    """
    processed_dir.mkdir(parents=True, exist_ok=True)
    clean_csv = processed_dir / "bookings_clean.csv"
    excluded_csv = processed_dir / "excluded_rows.csv"

    print(f"Saving cleaned dataset to: {clean_csv} ({len(df_clean):,} rows)")
    df_clean.to_csv(clean_csv, index=False)

    # Format date columns in excluded set as well for consistency
    date_cols = [
        "reservation_status_date", "booking_date", "arrival_date",
        "arrival_month_start", "checkout_date"
    ]
    for col in date_cols:
        if col in df_excluded.columns:
            df_excluded[col] = df_excluded[col].dt.strftime("%Y-%m-%d")

    print(f"Saving excluded dataset to: {excluded_csv} ({len(df_excluded):,} rows)")
    df_excluded.to_csv(excluded_csv, index=False)
    print("Step G Complete: Datasets saved successfully.")


def main():
    parser = argparse.ArgumentParser(description="Hotel Booking Demand Data Cleaning Pipeline")
    parser.add_argument(
        "--stage1",
        action="store_true",
        help="Execute Stage 1 (Steps A-C) only and print diagnostics"
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    raw_path = repo_root / "data" / "raw" / "hotel_bookings.csv"
    processed_dir = repo_root / "data" / "processed"

    # Step A: Load and flag duplicates
    df = load_raw(raw_path)

    # Step B: Build dates
    df = build_dates(df)

    # Step C: Build measures and imputations
    df = build_measures(df)

    if args.stage1:
        current_cols = set(df.columns)
        raw_cols_set = set(RAW_COLUMNS)
        added_cols = [c for c in df.columns if c not in raw_cols_set]
        dropped_cols = [c for c in RAW_COLUMNS if c not in current_cols]
        num_dups = int(df["is_duplicate_row"].sum())

        print("\n" + "=" * 60)
        print("STAGE 1 EXECUTION SUMMARY (Steps A to C)")
        print("=" * 60)
        print(f"Final Stage 1 Shape: {df.shape}")
        print(f"Total Rows: {len(df):,}")
        print(f"Duplicate Rows Flagged (is_duplicate_row == 1): {num_dups:,}")
        print(f"\nAdded Columns ({len(added_cols)}):")
        print("  " + ", ".join(added_cols))
        print(f"\nDropped Columns ({len(dropped_cols)}):")
        print("  " + ", ".join(dropped_cols))
        print("\n" + "=" * 60)
        print("STAGE 1 DIAGNOSTICS")
        print("=" * 60)
        print(df.dtypes.to_string())
        print("\nTransposed Head (first 3 rows):")
        print(df.head(3).T)
        return

    # Step D: Partition outliers
    df_clean, df_excluded = exclude_outliers(df)

    # Step E: Build flags and categories on clean dataset
    df_clean = build_flags_and_categories(df_clean)

    # Step F: Finalize columns and ordering
    df_clean_final = finalize_schema(df_clean)

    # Step G: Save processed datasets
    save_processed(df_clean_final, df_excluded, processed_dir)

    print("\n" + "=" * 60)
    print("CLEANING PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Clean Bookings:    {len(df_clean_final):,} rows, {len(df_clean_final.columns)} columns")
    print(f"Excluded Bookings: {len(df_excluded):,} rows")
    print(f"Total Preserved:   {len(df_clean_final) + len(df_excluded):,} rows")


if __name__ == "__main__":
    main()
