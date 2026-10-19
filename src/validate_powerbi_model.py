"""
Phase 4 Power BI Star Schema Model Validation: src/validate_powerbi_model.py
Validates the CSVs in powerbi/data across 6 rigorous categories:
1. Keys unique and not null
2. Referential integrity across all star relationships
3. Data types (dates parse as ISO dates, flags strictly in {0,1}, 0 literal 'nan' strings)
4. Reconciliation against data/outputs (v_booking_trends, v_monthly_kpis)
5. Model simulation in pandas for Resort Hotel 2016 (merging facts to dimensions only, no database queries)
6. dim_profile has 0 duplicate combinations

Prints PASS or FAIL for each check. Exits with non-zero code on any failure per Rule R5.
"""

import csv
import sys
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "powerbi" / "data"
OUTPUTS_DIR = REPO_ROOT / "data" / "outputs"


def validate_key_uniqueness_and_nulls(
    dim_date: pd.DataFrame,
    dim_hotel: pd.DataFrame,
    dim_profile: pd.DataFrame,
    fact_bookings: pd.DataFrame,
    fact_capacity: pd.DataFrame,
    fact_stay_nights: pd.DataFrame
) -> list:
    results = []

    # 1.1 dim_date.date_key
    null_dk = dim_date["date_key"].isna().sum()
    dup_dk = dim_date["date_key"].duplicated().sum()
    passed = (null_dk == 0 and dup_dk == 0)
    results.append((
        "C1.1",
        "dim_date.date_key unique and not null",
        f"Rows: {len(dim_date)}, Nulls: {null_dk}, Duplicates: {dup_dk}",
        "PASS" if passed else "FAIL"
    ))

    # 1.2 dim_hotel.hotel_key
    null_hk = dim_hotel["hotel_key"].isna().sum()
    dup_hk = dim_hotel["hotel_key"].duplicated().sum()
    passed = (null_hk == 0 and dup_hk == 0)
    results.append((
        "C1.2",
        "dim_hotel.hotel_key unique and not null",
        f"Rows: {len(dim_hotel)}, Nulls: {null_hk}, Duplicates: {dup_hk}",
        "PASS" if passed else "FAIL"
    ))

    # 1.3 dim_profile.profile_key
    null_pk = dim_profile["profile_key"].isna().sum()
    dup_pk = dim_profile["profile_key"].duplicated().sum()
    passed = (null_pk == 0 and dup_pk == 0)
    results.append((
        "C1.3",
        "dim_profile.profile_key unique and not null",
        f"Rows: {len(dim_profile)}, Nulls: {null_pk}, Duplicates: {dup_pk}",
        "PASS" if passed else "FAIL"
    ))

    # 1.4 fact_bookings.booking_id
    null_bid = fact_bookings["booking_id"].isna().sum()
    dup_bid = fact_bookings["booking_id"].duplicated().sum()
    passed = (null_bid == 0 and dup_bid == 0)
    results.append((
        "C1.4",
        "fact_bookings.booking_id unique and not null",
        f"Rows: {len(fact_bookings)}, Nulls: {null_bid}, Duplicates: {dup_bid}",
        "PASS" if passed else "FAIL"
    ))

    # 1.5 fact_capacity (hotel_key, date_key)
    null_cap = fact_capacity[["hotel_key", "date_key"]].isna().any().sum()
    dup_cap = fact_capacity.duplicated(subset=["hotel_key", "date_key"]).sum()
    passed = (null_cap == 0 and dup_cap == 0)
    results.append((
        "C1.5",
        "fact_capacity (hotel_key, date_key) unique and not null",
        f"Rows: {len(fact_capacity)}, Nulls: {null_cap}, Duplicates: {dup_cap}",
        "PASS" if passed else "FAIL"
    ))

    # 1.6 fact_stay_nights (booking_id, stay_date)
    null_sn = fact_stay_nights[["booking_id", "stay_date"]].isna().any().sum()
    dup_sn = fact_stay_nights.duplicated(subset=["booking_id", "stay_date"]).sum()
    passed = (null_sn == 0 and dup_sn == 0)
    results.append((
        "C1.6",
        "fact_stay_nights (booking_id, stay_date) unique and not null",
        f"Rows: {len(fact_stay_nights)}, Nulls: {null_sn}, Duplicates: {dup_sn}",
        "PASS" if passed else "FAIL"
    ))

    return results


def validate_referential_integrity(
    dim_date: pd.DataFrame,
    dim_hotel: pd.DataFrame,
    dim_profile: pd.DataFrame,
    fact_bookings: pd.DataFrame,
    fact_capacity: pd.DataFrame,
    fact_stay_nights: pd.DataFrame
) -> list:
    results = []

    hotel_keys = set(dim_hotel["hotel_key"])
    profile_keys = set(dim_profile["profile_key"])
    date_keys = set(dim_date["date_key"])

    # 2.1 hotel_key in all three fact tables
    unmatched_b_hk = len(set(fact_bookings["hotel_key"]) - hotel_keys)
    unmatched_sn_hk = len(set(fact_stay_nights["hotel_key"]) - hotel_keys)
    unmatched_cap_hk = len(set(fact_capacity["hotel_key"]) - hotel_keys)
    passed = (unmatched_b_hk == 0 and unmatched_sn_hk == 0 and unmatched_cap_hk == 0)
    results.append((
        "C2.1",
        "hotel_key referential integrity (dim_hotel)",
        f"Unmatched keys: fact_bookings={unmatched_b_hk}, fact_stay_nights={unmatched_sn_hk}, fact_capacity={unmatched_cap_hk}",
        "PASS" if passed else "FAIL"
    ))

    # 2.2 profile_key in fact_bookings and fact_stay_nights
    unmatched_b_pk = len(set(fact_bookings["profile_key"]) - profile_keys)
    unmatched_sn_pk = len(set(fact_stay_nights["profile_key"]) - profile_keys)
    passed = (unmatched_b_pk == 0 and unmatched_sn_pk == 0)
    results.append((
        "C2.2",
        "profile_key referential integrity (dim_profile)",
        f"Unmatched keys: fact_bookings={unmatched_b_pk}, fact_stay_nights={unmatched_sn_pk}",
        "PASS" if passed else "FAIL"
    ))

    # 2.3 date_key / arrival_date / stay_date in dim_date
    unmatched_b_date = len(set(fact_bookings["arrival_date"]) - date_keys)
    unmatched_sn_date = len(set(fact_stay_nights["stay_date"]) - date_keys)
    unmatched_cap_date = len(set(fact_capacity["date_key"]) - date_keys)
    passed = (unmatched_b_date == 0 and unmatched_sn_date == 0 and unmatched_cap_date == 0)
    results.append((
        "C2.3",
        "date_key referential integrity (dim_date)",
        f"Unmatched dates: fact_bookings={unmatched_b_date}, fact_stay_nights={unmatched_sn_date}, fact_capacity={unmatched_cap_date}",
        "PASS" if passed else "FAIL"
    ))

    return results


def validate_data_types_and_tokens(
    data_dir: Path,
    dim_date: pd.DataFrame,
    fact_bookings: pd.DataFrame,
    fact_capacity: pd.DataFrame,
    fact_stay_nights: pd.DataFrame
) -> list:
    results = []

    # 3.1 Date parsing check
    date_cols = [
        ("dim_date", dim_date["date_key"]),
        ("dim_date", dim_date["month_start"]),
        ("fact_bookings", fact_bookings["arrival_date"]),
        ("fact_stay_nights", fact_stay_nights["stay_date"]),
        ("fact_capacity", fact_capacity["date_key"])
    ]
    all_dates_parsed = True
    date_err_details = []
    for tname, s in date_cols:
        try:
            pd.to_datetime(s, format="%Y-%m-%d", errors="raise")
        except Exception as e:
            all_dates_parsed = False
            date_err_details.append(f"{tname}.{s.name}: {e}")

    results.append((
        "C3.1",
        "Dates parse strictly as ISO YYYY-MM-DD",
        "5 date columns validated across dim_date, fact_bookings, fact_stay_nights, fact_capacity" if all_dates_parsed else "; ".join(date_err_details),
        "PASS" if all_dates_parsed else "FAIL"
    ))

    # 3.2 Flag values check: strictly {0, 1}
    flag_cols = [
        "is_canceled", "is_no_show", "is_repeated_guest",
        "room_type_mismatch", "is_duplicate_row"
    ]
    all_flags_valid = True
    flag_details = []
    for col in flag_cols:
        vals = set(fact_bookings[col].unique())
        if not vals.issubset({0, 1}):
            all_flags_valid = False
            flag_details.append(f"{col}: {vals}")

    results.append((
        "C3.2",
        "Flags hold strictly integer values in {0, 1}",
        f"All 5 flag columns strictly hold 0 and 1" if all_flags_valid else "; ".join(flag_details),
        "PASS" if all_flags_valid else "FAIL"
    ))

    # 3.3 No literal 'nan', 'null', 'none' string tokens
    nan_counts = {}
    for csv_path in sorted(data_dir.glob("*.csv")):
        count = 0
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                for val in row:
                    if val.strip().lower() in ["nan", "null", "none"]:
                        count += 1
        nan_counts[csv_path.name] = count

    total_nan_strings = sum(nan_counts.values())
    passed = (total_nan_strings == 0)
    results.append((
        "C3.3",
        "No literal 'nan', 'null', or 'none' string tokens in CSVs",
        f"Total literal nan/null strings across 6 CSVs: {total_nan_strings}" if passed else f"Found literal tokens: {nan_counts}",
        "PASS" if passed else "FAIL"
    ))

    return results


def validate_reconciliation_with_outputs(
    dim_date: pd.DataFrame,
    dim_hotel: pd.DataFrame,
    fact_bookings: pd.DataFrame,
    fact_stay_nights: pd.DataFrame,
    fact_capacity: pd.DataFrame,
    outputs_dir: Path
) -> list:
    results = []

    v_bt = pd.read_csv(outputs_dir / "v_booking_trends.csv")
    v_mk = pd.read_csv(outputs_dir / "v_monthly_kpis.csv")

    # 4.1 Total bookings and cancellations vs v_booking_trends
    fact_b_tot = len(fact_bookings)
    vbt_b_tot = v_bt["bookings"].sum()
    b_diff = abs(fact_b_tot - vbt_b_tot)

    fact_c_tot = (fact_bookings["is_canceled"] == 1).sum()
    vbt_c_tot = v_bt["cancellations"].sum()
    c_diff = abs(fact_c_tot - vbt_c_tot)

    passed = (b_diff == 0 and c_diff == 0)
    results.append((
        "C4.1",
        "Total bookings and cancellations equal v_booking_trends",
        f"Bookings: {fact_b_tot} vs {vbt_b_tot} (diff={b_diff}); Cancellations: {fact_c_tot} vs {vbt_c_tot} (diff={c_diff})",
        "PASS" if passed else "FAIL"
    ))

    # 4.2 Per hotel-month stay nights, revenue, capacity, occupancy, and RevPAR vs v_monthly_kpis
    sn_merged = (
        fact_stay_nights.merge(dim_hotel, on="hotel_key")
        .merge(dim_date, left_on="stay_date", right_on="date_key")
    )
    sn_monthly = (
        sn_merged.groupby(["hotel", "month_start"])
        .agg(
            room_nights_sold=("booking_id", "count"),
            room_revenue=("adr", "sum")
        )
        .reset_index()
    )

    cap_merged = (
        fact_capacity.merge(dim_hotel, on="hotel_key")
        .merge(dim_date, on="date_key")
    )
    cap_monthly = (
        cap_merged.groupby(["hotel", "month_start"])
        .agg(room_nights_available=("rooms_available", "sum"))
        .reset_index()
    )

    fact_monthly = sn_monthly.merge(cap_monthly, on=["hotel", "month_start"])
    fact_monthly["occupancy_pct"] = 100.0 * fact_monthly["room_nights_sold"] / fact_monthly["room_nights_available"]
    fact_monthly["adr"] = fact_monthly["room_revenue"] / fact_monthly["room_nights_sold"]
    fact_monthly["revpar"] = fact_monthly["room_revenue"] / fact_monthly["room_nights_available"]

    comparison = fact_monthly.merge(v_mk, on=["hotel", "month_start"], suffixes=("_fact", "_vmk"))

    # Assertions per hotel-month
    sold_diffs = (comparison["room_nights_sold_fact"] != comparison["room_nights_sold_vmk"]).sum()
    avail_diffs = (comparison["room_nights_available_fact"] != comparison["room_nights_available_vmk"]).sum()
    rev_diffs = (abs(comparison["room_revenue_fact"] - comparison["room_revenue_vmk"]) > 0.01).sum()
    occ_diffs = (abs(comparison["occupancy_pct_fact"] - comparison["occupancy_pct_vmk"]) > 0.01).sum()
    revpar_diffs = (abs(comparison["revpar_fact"] - comparison["revpar_vmk"]) > 0.01).sum()

    all_monthly_passed = (
        len(comparison) == 50 and
        sold_diffs == 0 and
        avail_diffs == 0 and
        rev_diffs == 0 and
        occ_diffs == 0 and
        revpar_diffs == 0
    )

    results.append((
        "C4.2",
        "Per hotel-month reconciliation against v_monthly_kpis (50 months)",
        f"Months: {len(comparison)}/50, Sold diffs: {sold_diffs}, Avail diffs: {avail_diffs}, Rev diffs: {rev_diffs}, Occ diffs: {occ_diffs}, RevPAR diffs: {revpar_diffs}",
        "PASS" if all_monthly_passed else "FAIL"
    ))

    return results


def validate_powerbi_model_simulation(
    dim_date: pd.DataFrame,
    dim_hotel: pd.DataFrame,
    fact_stay_nights: pd.DataFrame,
    fact_capacity: pd.DataFrame,
    outputs_dir: Path
) -> list:
    results = []

    # Filter purely within pandas star schema: hotel = Resort Hotel, year = 2016
    resort_key = dim_hotel.loc[dim_hotel["hotel"] == "Resort Hotel", "hotel_key"].iloc[0]
    dates_2016 = set(dim_date.loc[dim_date["year"] == 2016, "date_key"])

    # Simulate Power BI star schema relationship joins
    sn_sim = fact_stay_nights[
        (fact_stay_nights["hotel_key"] == resort_key) &
        (fact_stay_nights["stay_date"].isin(dates_2016))
    ]
    cap_sim = fact_capacity[
        (fact_capacity["hotel_key"] == resort_key) &
        (fact_capacity["date_key"].isin(dates_2016))
    ]

    sim_sold = len(sn_sim)
    sim_rev = sn_sim["adr"].sum()
    sim_avail = cap_sim["rooms_available"].sum()
    sim_adr = sim_rev / sim_sold
    sim_occ = 100.0 * sim_sold / sim_avail
    sim_revpar = sim_rev / sim_avail

    # Expected values from v_monthly_kpis aggregated for Resort Hotel 2016
    v_mk = pd.read_csv(outputs_dir / "v_monthly_kpis.csv")
    vmk_resort_2016 = v_mk[
        (v_mk["hotel"] == "Resort Hotel") &
        (v_mk["month_start"].str.startswith("2016"))
    ]

    exp_sold = vmk_resort_2016["room_nights_sold"].sum()
    exp_rev = vmk_resort_2016["room_revenue"].sum()
    exp_avail = vmk_resort_2016["room_nights_available"].sum()
    exp_adr = exp_rev / exp_sold
    exp_occ = 100.0 * exp_sold / exp_avail
    exp_revpar = exp_rev / exp_avail

    diff_sold = abs(sim_sold - exp_sold)
    diff_rev = abs(sim_rev - exp_rev)
    diff_avail = abs(sim_avail - exp_avail)
    diff_adr = abs(sim_adr - exp_adr)
    diff_occ = abs(sim_occ - exp_occ)
    diff_revpar = abs(sim_revpar - exp_revpar)

    passed = (
        diff_sold == 0 and
        diff_rev <= 0.01 and
        diff_avail == 0 and
        diff_adr <= 0.01 and
        diff_occ <= 0.01 and
        diff_revpar <= 0.01
    )

    detail_str = (
        f"Sold: {sim_sold} vs {exp_sold}; "
        f"Rev: ${sim_rev:.2f} vs ${exp_rev:.2f}; "
        f"Avail: {sim_avail} vs {exp_avail}; "
        f"ADR: ${sim_adr:.2f} vs ${exp_adr:.2f}; "
        f"Occ: {sim_occ:.2f}% vs {exp_occ:.2f}%; "
        f"RevPAR: ${sim_revpar:.2f} vs ${exp_revpar:.2f}"
    )

    results.append((
        "C5.1",
        "Model simulation (Resort Hotel, 2016: Sold, Rev, Avail, ADR, Occ, RevPAR)",
        detail_str,
        "PASS" if passed else "FAIL"
    ))

    return results


def validate_dim_profile_distinct(dim_profile: pd.DataFrame) -> list:
    results = []

    dup_count = dim_profile[
        ["market_segment", "distribution_channel", "customer_type", "deposit_type"]
    ].duplicated().sum()

    passed = (dup_count == 0)
    results.append((
        "C6.1",
        "dim_profile has 0 duplicate attribute combinations",
        f"Total profiles: {len(dim_profile)}, Duplicate combinations: {dup_count}",
        "PASS" if passed else "FAIL"
    ))

    return results


def validate_powerbi_model() -> bool:
    print("=" * 110)
    print("POWER BI STAR SCHEMA VALIDATION ENGINE: powerbi/data/*.csv")
    print("=" * 110)

    # 1. Load CSVs
    dim_date = pd.read_csv(DATA_DIR / "dim_date.csv")
    dim_hotel = pd.read_csv(DATA_DIR / "dim_hotel.csv")
    dim_profile = pd.read_csv(DATA_DIR / "dim_profile.csv")
    fact_bookings = pd.read_csv(DATA_DIR / "fact_bookings.csv")
    fact_stay_nights = pd.read_csv(DATA_DIR / "fact_stay_nights.csv")
    fact_capacity = pd.read_csv(DATA_DIR / "fact_capacity.csv")

    all_checks = []

    # Run checks 1 to 6
    all_checks.extend(validate_key_uniqueness_and_nulls(
        dim_date, dim_hotel, dim_profile, fact_bookings, fact_capacity, fact_stay_nights
    ))
    all_checks.extend(validate_referential_integrity(
        dim_date, dim_hotel, dim_profile, fact_bookings, fact_capacity, fact_stay_nights
    ))
    all_checks.extend(validate_data_types_and_tokens(
        DATA_DIR, dim_date, fact_bookings, fact_capacity, fact_stay_nights
    ))
    all_checks.extend(validate_reconciliation_with_outputs(
        dim_date, dim_hotel, fact_bookings, fact_stay_nights, fact_capacity, OUTPUTS_DIR
    ))
    all_checks.extend(validate_powerbi_model_simulation(
        dim_date, dim_hotel, fact_stay_nights, fact_capacity, OUTPUTS_DIR
    ))
    all_checks.extend(validate_dim_profile_distinct(dim_profile))

    # Print results table
    print(f"{'STATUS':<6} | {'ID':<5} | {'CHECK NAME':<55} | {'DETAILS'}")
    print("-" * 110)
    all_passed = True
    for cid, cname, cdetail, cstat in all_checks:
        if cstat != "PASS":
            all_passed = False
        print(f"{cstat:<6} | {cid:<5} | {cname:<55} | {cdetail}")
    print("-" * 110)

    if all_passed:
        print(f"POWER BI STAR SCHEMA VALIDATION SUMMARY: ALL {len(all_checks)} CHECKS PASSED [PASS]")
    else:
        print("POWER BI STAR SCHEMA VALIDATION SUMMARY: FAILURES DETECTED [FAIL]")

    print("=" * 110)
    return all_passed


def main():
    ok = validate_powerbi_model()
    if not ok:
        print("[CRITICAL] Power BI model validation failed! Exiting with non-zero status.")
        sys.exit(1)


if __name__ == "__main__":
    main()
