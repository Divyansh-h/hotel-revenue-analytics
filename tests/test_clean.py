"""
Pytest suite for cleaned hotel booking demand dataset.
Validates data/processed/bookings_clean.csv and data/processed/excluded_rows.csv
against authoritative rules and decisions D1 through D12 in PROJECT_CONTEXT.md.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
CLEAN_PATH = PROCESSED_DIR / "bookings_clean.csv"
EXCLUDED_PATH = PROCESSED_DIR / "excluded_rows.csv"

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


@pytest.fixture(scope="session")
def clean_data() -> pd.DataFrame:
    assert CLEAN_PATH.exists(), f"Cleaned data file missing at: {CLEAN_PATH}"
    df = pd.read_csv(CLEAN_PATH, low_memory=False)
    return df


@pytest.fixture(scope="session")
def excluded_data() -> pd.DataFrame:
    assert EXCLUDED_PATH.exists(), f"Excluded rows file missing at: {EXCLUDED_PATH}"
    df = pd.read_csv(EXCLUDED_PATH, low_memory=False)
    return df


def test_01_row_count(clean_data: pd.DataFrame, excluded_data: pd.DataFrame):
    """Rule 1: Cleaned rows + excluded rows must equal exactly 119,390."""
    total = len(clean_data) + len(excluded_data)
    assert total == 119390, (
        f"Row count mismatch: cleaned ({len(clean_data):,}) + excluded ({len(excluded_data):,}) "
        f"= {total:,}, expected exactly 119,390."
    )


def test_02_booking_id_integrity(clean_data: pd.DataFrame, excluded_data: pd.DataFrame):
    """Rule 2: booking_id is unique and together covers 1..119390 exactly once."""
    clean_ids = set(clean_data["booking_id"])
    excl_ids = set(excluded_data["booking_id"])

    assert len(clean_ids) == len(clean_data), (
        f"Duplicate booking_id found in bookings_clean: {len(clean_data) - len(clean_ids)} duplicates."
    )
    assert len(excl_ids) == len(excluded_data), (
        f"Duplicate booking_id found in excluded_rows: {len(excluded_data) - len(excl_ids)} duplicates."
    )

    overlap = clean_ids.intersection(excl_ids)
    assert not overlap, f"booking_id overlap between cleaned and excluded datasets: {overlap}"

    combined_ids = clean_ids.union(excl_ids)
    expected_ids = set(range(1, 119391))
    assert combined_ids == expected_ids, (
        f"Combined booking_ids do not cover 1..119390 exactly once! "
        f"Missing: {len(expected_ids - combined_ids)}, Unexpected: {len(combined_ids - expected_ids)}"
    )


def test_03_column_list_and_order(clean_data: pd.DataFrame):
    """Rule 3: Columns equal final column list in PROJECT_CONTEXT.md in exact order."""
    actual_cols = list(clean_data.columns)
    assert actual_cols == FINAL_COLUMNS, (
        f"Column list or ordering mismatch:\n"
        f"Expected ({len(FINAL_COLUMNS)}): {FINAL_COLUMNS}\n"
        f"Actual   ({len(actual_cols)}): {actual_cols}"
    )


def test_04_no_nulls_in_key_columns(clean_data: pd.DataFrame):
    """Rule 4: No nulls in key analytical columns."""
    key_cols = [
        "booking_id", "hotel", "is_canceled", "arrival_date", "lead_time",
        "total_nights", "adr", "market_segment", "deposit_type", "country"
    ]
    null_counts = clean_data[key_cols].isna().sum().to_dict()
    violating = {col: cnt for col, cnt in null_counts.items() if cnt > 0}
    assert not violating, f"Found unexpected null values in key columns: {violating}"


def test_05_categorical_domain_validity(clean_data: pd.DataFrame):
    """Rule 5: hotel and reservation_status domain values are valid."""
    hotels = set(clean_data["hotel"].unique())
    assert hotels == {"City Hotel", "Resort Hotel"}, f"Unexpected hotel categories: {hotels}"

    statuses = set(clean_data["reservation_status"].unique())
    assert statuses == {"Check-Out", "Canceled", "No-Show"}, f"Unexpected reservation_status categories: {statuses}"


def test_06_cancellation_flags_consistency(clean_data: pd.DataFrame):
    """Rule 6: is_canceled is 1 iff Canceled/No-Show; is_no_show is 1 iff No-Show."""
    canceled_expected = clean_data["reservation_status"].isin(["Canceled", "No-Show"]).astype(int)
    canceled_diff = (clean_data["is_canceled"] != canceled_expected).sum()
    assert canceled_diff == 0, f"is_canceled inconsistent with reservation_status in {canceled_diff} rows"

    no_show_expected = (clean_data["reservation_status"] == "No-Show").astype(int)
    no_show_diff = (clean_data["is_no_show"] != no_show_expected).sum()
    assert no_show_diff == 0, f"is_no_show inconsistent with reservation_status in {no_show_diff} rows"


def test_07_adr_range_and_room_revenue(clean_data: pd.DataFrame):
    """Rule 7: adr is between 0 and 1000; room_revenue equals adr * total_nights within 0.01."""
    out_of_bounds = ((clean_data["adr"] < 0) | (clean_data["adr"] > 1000)).sum()
    assert out_of_bounds == 0, f"Found {out_of_bounds} rows with adr < 0 or > 1000 in cleaned data"

    expected_revenue = clean_data["adr"] * clean_data["total_nights"]
    diff = (clean_data["room_revenue"] - expected_revenue).abs()
    revenue_mismatches = (diff > 0.01).sum()
    assert revenue_mismatches == 0, f"Found {revenue_mismatches} rows where room_revenue != adr * total_nights within 0.01"


def test_08_total_nights_and_checkout_date(clean_data: pd.DataFrame):
    """Rule 8: total_nights equals weekend + week nights; checkout_date - arrival_date equals total_nights."""
    expected_nights = clean_data["stays_in_weekend_nights"] + clean_data["stays_in_week_nights"]
    night_diffs = (clean_data["total_nights"] != expected_nights).sum()
    assert night_diffs == 0, f"total_nights calculation mismatch in {night_diffs} rows"

    arr_dt = pd.to_datetime(clean_data["arrival_date"])
    chk_dt = pd.to_datetime(clean_data["checkout_date"])
    date_diff_days = (chk_dt - arr_dt).dt.days
    date_diff_mismatches = (date_diff_days != clean_data["total_nights"]).sum()
    assert date_diff_mismatches == 0, f"checkout_date - arrival_date != total_nights in {date_diff_mismatches} rows"


def test_09_booking_date_lead_time_consistency(clean_data: pd.DataFrame):
    """Rule 9: booking_date equals arrival_date minus lead_time days."""
    arr_dt = pd.to_datetime(clean_data["arrival_date"])
    bkg_dt = pd.to_datetime(clean_data["booking_date"])
    lead_days = (arr_dt - bkg_dt).dt.days
    mismatches = (lead_days != clean_data["lead_time"]).sum()
    assert mismatches == 0, f"arrival_date - booking_date != lead_time in {mismatches} rows"


def test_10_lead_bucket_boundaries_and_mapping(clean_data: pd.DataFrame):
    """Rule 10: lead_bucket matches D9; test boundary values 0, 7, 8, 30, 31, 90, 91, 180, 181."""
    boundary_cases = {
        0: ("0-7", 1),
        7: ("0-7", 1),
        8: ("8-30", 2),
        30: ("8-30", 2),
        31: ("31-90", 3),
        90: ("31-90", 3),
        91: ("91-180", 4),
        180: ("91-180", 4),
        181: ("181+", 5),
    }
    bins = [-1, 7, 30, 90, 180, 100000]
    labels = ["0-7", "8-30", "31-90", "91-180", "181+"]
    order_map = {"0-7": 1, "8-30": 2, "31-90": 3, "91-180": 4, "181+": 5}

    for lead_val, (exp_bucket, exp_order) in boundary_cases.items():
        actual_bucket = str(pd.cut([lead_val], bins=bins, labels=labels)[0])
        actual_order = order_map[actual_bucket]
        assert actual_bucket == exp_bucket, f"Boundary lead_time {lead_val} mapped to {actual_bucket}, expected {exp_bucket}"
        assert actual_order == exp_order, f"Boundary lead_time {lead_val} mapped to order {actual_order}, expected {exp_order}"

    expected_buckets = pd.cut(clean_data["lead_time"], bins=bins, labels=labels).astype(str)
    bucket_diff = (clean_data["lead_bucket"] != expected_buckets).sum()
    assert bucket_diff == 0, f"lead_bucket mapping mismatch in {bucket_diff} rows"

    expected_orders = expected_buckets.map(order_map).astype(int)
    order_diff = (clean_data["lead_bucket_order"] != expected_orders).sum()
    assert order_diff == 0, f"lead_bucket_order mapping mismatch in {order_diff} rows"


def test_11_flag_columns_and_zero_conditions(clean_data: pd.DataFrame):
    """Rule 11: flag_zero_nights is 1 iff total_nights = 0; flag_zero_guests is 1 iff total_guests = 0; flags are 0/1."""
    zero_nights_expected = (clean_data["total_nights"] == 0).astype(int)
    assert (clean_data["flag_zero_nights"] == zero_nights_expected).all(), "flag_zero_nights != 1 iff total_nights == 0"

    zero_guests_expected = (clean_data["total_guests"] == 0).astype(int)
    assert (clean_data["flag_zero_guests"] == zero_guests_expected).all(), "flag_zero_guests != 1 iff total_guests == 0"

    flag_cols = [
        "is_canceled", "is_no_show", "is_repeated_guest",
        "room_type_mismatch", "flag_zero_nights", "flag_zero_guests", "is_duplicate_row"
    ]
    for col in flag_cols:
        vals = set(clean_data[col].unique())
        assert vals.issubset({0, 1}), f"Flag column '{col}' contains values other than 0 or 1: {vals}"


def test_12_cancellation_days_lead_null_rule(clean_data: pd.DataFrame):
    """Rule 12: days_cancelled_before_arrival is null unless reservation_status is Canceled."""
    non_canceled = clean_data[clean_data["reservation_status"] != "Canceled"]
    non_canceled_not_null = non_canceled["days_cancelled_before_arrival"].notna().sum()
    assert non_canceled_not_null == 0, (
        f"days_cancelled_before_arrival is not NULL for {non_canceled_not_null} non-canceled rows"
    )

    canceled = clean_data[clean_data["reservation_status"] == "Canceled"]
    canceled_null = canceled["days_cancelled_before_arrival"].isna().sum()
    assert canceled_null == 0, (
        f"days_cancelled_before_arrival is NULL for {canceled_null} canceled rows"
    )


def test_13_arrival_date_range(clean_data: pd.DataFrame):
    """Rule 13: arrival_date is between 2015-07-01 and 2017-08-31 inclusive."""
    arr_dt = pd.to_datetime(clean_data["arrival_date"])
    min_date = arr_dt.min().strftime("%Y-%m-%d")
    max_date = arr_dt.max().strftime("%Y-%m-%d")

    assert min_date == "2015-07-01", f"Earliest arrival_date is {min_date}, expected 2015-07-01"
    assert max_date == "2017-08-31", f"Latest arrival_date is {max_date}, expected 2017-08-31"


def test_14_excluded_rows_schema_and_count(excluded_data: pd.DataFrame):
    """Rule 14: excluded_rows.csv has exactly 2 rows and an excluded_reason column."""
    assert len(excluded_data) == 2, f"excluded_rows.csv has {len(excluded_data)} rows, expected exactly 2"
    assert "excluded_reason" in excluded_data.columns, "excluded_rows.csv is missing 'excluded_reason' column"
    assert excluded_data["excluded_reason"].notna().all(), "excluded_rows.csv contains NULL in 'excluded_reason'"
