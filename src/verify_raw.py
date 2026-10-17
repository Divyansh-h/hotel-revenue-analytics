"""
Verification script for raw dataset: data/raw/hotel_bookings.csv
Validates schema, dimensions, categorical values, cancellation logic,
date ranges, and missing value counts.
Outputs results to console and reports/tables/raw_verification.csv.
"""

from pathlib import Path
import pandas as pd


def verify_raw_dataset() -> bool:
    repo_root = Path(__file__).resolve().parent.parent
    raw_path = repo_root / "data" / "raw" / "hotel_bookings.csv"
    output_path = repo_root / "reports" / "tables" / "raw_verification.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading {raw_path}...")
    df = pd.read_csv(raw_path)

    results = []

    def log_check(check_num: int, name: str, passed: bool, expected: str, actual: str):
        status = "PASS" if passed else "FAIL"
        print(f"Check {check_num} [{status}] - {name}")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")
        results.append({
            "check_num": check_num,
            "check_name": name,
            "status": status,
            "expected": expected,
            "actual": actual
        })
        return passed

    all_passed = True

    # 1. Shape is exactly (119390, 32)
    expected_shape = (119390, 32)
    actual_shape = df.shape
    c1 = (actual_shape == expected_shape)
    all_passed &= log_check(1, "Dataset Shape", c1, str(expected_shape), str(actual_shape))

    # 2. The 32 column names match exactly
    expected_cols = [
        "hotel", "is_canceled", "lead_time", "arrival_date_year", "arrival_date_month",
        "arrival_date_week_number", "arrival_date_day_of_month", "stays_in_weekend_nights",
        "stays_in_week_nights", "adults", "children", "babies", "meal", "country",
        "market_segment", "distribution_channel", "is_repeated_guest", "previous_cancellations",
        "previous_bookings_not_canceled", "reserved_room_type", "assigned_room_type",
        "booking_changes", "deposit_type", "agent", "company", "days_in_waiting_list",
        "customer_type", "adr", "required_car_parking_spaces", "total_of_special_requests",
        "reservation_status", "reservation_status_date"
    ]
    actual_cols = list(df.columns)
    c2 = (actual_cols == expected_cols)
    all_passed &= log_check(2, "Exact Column Names & Order", c2, ", ".join(expected_cols), ", ".join(actual_cols))

    # 3. hotel has exactly two values: City Hotel and Resort Hotel
    expected_hotels = {"City Hotel", "Resort Hotel"}
    actual_hotels = set(df["hotel"].unique())
    c3 = (actual_hotels == expected_hotels)
    all_passed &= log_check(3, "Hotel Categorical Values", c3, str(sorted(list(expected_hotels))), str(sorted(list(actual_hotels))))

    # 4. reservation_status has exactly Check-Out, Canceled, No-Show (~75166, 43017, 1207)
    status_counts = df["reservation_status"].value_counts().to_dict()
    expected_status_counts = {"Check-Out": 75166, "Canceled": 43017, "No-Show": 1207}
    c4 = (
        set(status_counts.keys()) == set(expected_status_counts.keys()) and
        abs(status_counts.get("Check-Out", 0) - 75166) <= 50 and
        abs(status_counts.get("Canceled", 0) - 43017) <= 50 and
        abs(status_counts.get("No-Show", 0) - 1207) <= 50
    )
    all_passed &= log_check(4, "Reservation Status Frequencies", c4, str(expected_status_counts), str(status_counts))

    # 5. is_canceled equals 1 exactly when reservation_status is Canceled or No-Show
    expected_canceled_mask = df["reservation_status"].isin(["Canceled", "No-Show"])
    actual_canceled_mask = (df["is_canceled"] == 1)
    c5 = (expected_canceled_mask == actual_canceled_mask).all()
    mismatches = int((expected_canceled_mask != actual_canceled_mask).sum())
    all_passed &= log_check(5, "is_canceled Consistency", c5, "is_canceled == 1 exactly for Canceled / No-Show (0 mismatches)", f"{mismatches} mismatches")

    # 6. Overall cancellation rate ~37.0% (36.9 to 37.1). City ~41.7% (+/-0.2), Resort ~27.8% (+/-0.2)
    overall_cancel_rate = df["is_canceled"].mean() * 100
    city_cancel_rate = df[df["hotel"] == "City Hotel"]["is_canceled"].mean() * 100
    resort_cancel_rate = df[df["hotel"] == "Resort Hotel"]["is_canceled"].mean() * 100
    c6_overall = (36.9 <= overall_cancel_rate <= 37.1)
    c6_city = (41.5 <= city_cancel_rate <= 41.9)
    c6_resort = (27.6 <= resort_cancel_rate <= 28.0)
    c6 = c6_overall and c6_city and c6_resort
    exp_c6 = "Overall: 36.9-37.1%, City: 41.5-41.9%, Resort: 27.6-28.0%"
    act_c6 = f"Overall: {overall_cancel_rate:.2f}%, City: {city_cancel_rate:.2f}%, Resort: {resort_cancel_rate:.2f}%"
    all_passed &= log_check(6, "Cancellation Rates", c6, exp_c6, act_c6)

    # 7. Earliest and latest arrival dates are 2015-07-01 and 2017-08-31
    month_map = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }
    dates = pd.to_datetime(pd.DataFrame({
        "year": df["arrival_date_year"],
        "month": df["arrival_date_month"].map(month_map),
        "day": df["arrival_date_day_of_month"]
    }))
    min_date = dates.min().strftime("%Y-%m-%d")
    max_date = dates.max().strftime("%Y-%m-%d")
    c7 = (min_date == "2015-07-01" and max_date == "2017-08-31")
    all_passed &= log_check(7, "Arrival Date Range", c7, "2015-07-01 to 2017-08-31", f"{min_date} to {max_date}")

    # 8. NaN counts: children ~4, country ~488, agent ~16,340, company ~112,593
    nulls = {col: int(df[col].isna().sum()) for col in ["children", "country", "agent", "company"]}
    c8 = (
        abs(nulls["children"] - 4) <= 2 and
        abs(nulls["country"] - 488) <= 10 and
        abs(nulls["agent"] - 16340) <= 50 and
        abs(nulls["company"] - 112593) <= 100
    )
    exp_c8 = "children ~4, country ~488, agent ~16340, company ~112593"
    act_c8 = f"children: {nulls['children']}, country: {nulls['country']}, agent: {nulls['agent']}, company: {nulls['company']}"
    all_passed &= log_check(8, "Missing Value Counts", c8, exp_c8, act_c8)

    # Save to reports/tables/raw_verification.csv
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)
    print(f"\nVerification results saved to: {output_path}")

    if all_passed:
        print("\nALL 8 CHECKS PASSED.")
    else:
        print("\nONE OR MORE CHECKS FAILED.")

    return all_passed


if __name__ == "__main__":
    success = verify_raw_dataset()
    if not success:
        exit(1)
