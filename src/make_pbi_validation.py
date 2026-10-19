"""
Phase 4 Validation Benchmark Generator: src/make_pbi_validation.py
Computes the exact expected values for each numeric measure in powerbi/measures.dax
across 6 slicer scenarios from the star schema CSVs in powerbi/data/.

Scenarios:
- S1: No filters (Portfolio baseline)
- S2: Hotel = City Hotel
- S3: Hotel = Resort Hotel and Year = 2016
- S4: Market Segment = Online TA
- S5: Distribution Channel = Direct and Year = 2017
- S6: Hotel = City Hotel, Market Segment = Groups and Year = 2016

Columns: scenario_id, slicers, measure, expected_value, tolerance
"""

import sys
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "powerbi" / "data"
OUTPUT_FILE = REPO_ROOT / "powerbi" / "validation_expected.csv"


def load_star_schema():
    dim_date = pd.read_csv(DATA_DIR / "dim_date.csv")
    dim_hotel = pd.read_csv(DATA_DIR / "dim_hotel.csv")
    dim_profile = pd.read_csv(DATA_DIR / "dim_profile.csv")
    fact_bookings = pd.read_csv(DATA_DIR / "fact_bookings.csv")
    fact_stay_nights = pd.read_csv(DATA_DIR / "fact_stay_nights.csv")
    fact_capacity = pd.read_csv(DATA_DIR / "fact_capacity.csv")

    # Join dimensions to facts
    fb = fact_bookings.merge(dim_hotel[["hotel_key", "hotel"]], on="hotel_key")
    fb = fb.merge(dim_profile[["profile_key", "market_segment", "distribution_channel"]], on="profile_key")
    fb["arrival_year"] = pd.to_datetime(fb["arrival_date"]).dt.year

    fsn = fact_stay_nights.merge(dim_hotel[["hotel_key", "hotel"]], on="hotel_key")
    fsn = fsn.merge(dim_profile[["profile_key", "market_segment", "distribution_channel"]], on="profile_key")
    fsn["stay_year"] = pd.to_datetime(fsn["stay_date"]).dt.year

    fc = fact_capacity.merge(dim_hotel[["hotel_key", "hotel"]], on="hotel_key")
    fc["capacity_year"] = pd.to_datetime(fc["date_key"]).dt.year

    return fb, fsn, fc


def compute_scenario_metrics(fb, fsn, fc, criteria: dict):
    # Base copies
    b_df = fb.copy()
    sn_df = fsn.copy()
    cap_df = fc.copy()

    # Copies for ALLSELECTED(dim_profile) benchmark calculation
    b_prof_benchmark = fb.copy()
    sn_prof_benchmark = fsn.copy()

    # 1. Apply Hotel filter (affects bookings, stay nights, and capacity)
    if "hotel" in criteria:
        h = criteria["hotel"]
        b_df = b_df[b_df["hotel"] == h]
        sn_df = sn_df[sn_df["hotel"] == h]
        cap_df = cap_df[cap_df["hotel"] == h]

        b_prof_benchmark = b_prof_benchmark[b_prof_benchmark["hotel"] == h]
        sn_prof_benchmark = sn_prof_benchmark[sn_prof_benchmark["hotel"] == h]

    # 2. Apply Year filter
    # Respect semantics: Year filters bookings by arrival year and stay nights and capacity by stay year
    if "year" in criteria:
        yr = criteria["year"]
        b_df = b_df[b_df["arrival_year"] == yr]
        sn_df = sn_df[sn_df["stay_year"] == yr]
        cap_df = cap_df[cap_df["capacity_year"] == yr]

        b_prof_benchmark = b_prof_benchmark[b_prof_benchmark["arrival_year"] == yr]
        sn_prof_benchmark = sn_prof_benchmark[sn_prof_benchmark["stay_year"] == yr]

    # 3. Apply Market Segment filter (affects bookings and stay nights; capacity is unaffected)
    if "market_segment" in criteria:
        seg = criteria["market_segment"]
        b_df = b_df[b_df["market_segment"] == seg]
        sn_df = sn_df[sn_df["market_segment"] == seg]

    # 4. Apply Distribution Channel filter (affects bookings and stay nights; capacity is unaffected)
    if "distribution_channel" in criteria:
        ch = criteria["distribution_channel"]
        b_df = b_df[b_df["distribution_channel"] == ch]
        sn_df = sn_df[sn_df["distribution_channel"] == ch]

    # === Calculate Measures ===
    # Bookings folder
    bookings = len(b_df)
    cancelled_bookings = int((b_df["is_canceled"] == 1).sum()) if bookings else 0
    cancellations_canceled = int((b_df["reservation_status"] == "Canceled").sum()) if bookings else 0
    no_shows = int((b_df["is_no_show"] == 1).sum()) if bookings else 0
    cancel_rate_pct = (cancelled_bookings / bookings) if bookings else 0.0
    no_show_rate_pct = (no_shows / bookings) if bookings else 0.0
    stay_conversion_pct = (int((b_df["is_canceled"] == 0).sum()) / bookings) if bookings else 0.0
    avg_lead_time = float(b_df["lead_time"].mean()) if bookings else 0.0

    days_cancel = b_df["days_cancelled_before_arrival"].dropna()
    avg_days_cancelled = float(days_cancel.mean()) if len(days_cancel) else 0.0

    non_canc = b_df[b_df["is_canceled"] == 0]
    room_mismatch_pct = (float((non_canc["room_type_mismatch"] == 1).sum()) / len(non_canc)) if len(non_canc) else 0.0

    # Stay-night KPIs folder
    room_nights_sold = len(sn_df)
    room_revenue = float(sn_df["adr"].sum()) if room_nights_sold else 0.0
    room_nights_available = int(cap_df["rooms_available"].sum())
    adr = (room_revenue / room_nights_sold) if room_nights_sold else 0.0
    occupancy_pct = (room_nights_sold / room_nights_available) if room_nights_available else 0.0
    revpar = (room_revenue / room_nights_available) if room_nights_available else 0.0

    # Shares and trends folder
    denom_rev = float(sn_prof_benchmark["adr"].sum()) if len(sn_prof_benchmark) else 0.0
    denom_sold = len(sn_prof_benchmark)
    revenue_share_pct = (room_revenue / denom_rev) if denom_rev else 0.0
    room_night_share_pct = (room_nights_sold / denom_sold) if denom_sold else 0.0

    # Underperformer Flag:
    # 1 when Cancel Rate % > BenchmarkCancelRate AND ADR < BenchmarkADR AND ADR >= 5; else 0
    benchmark_canc = int((b_prof_benchmark["is_canceled"] == 1).sum())
    benchmark_b = len(b_prof_benchmark)
    benchmark_cancel_rate = (benchmark_canc / benchmark_b) if benchmark_b else 0.0
    benchmark_sold = len(sn_prof_benchmark)
    benchmark_rev = float(sn_prof_benchmark["adr"].sum())
    benchmark_adr = (benchmark_rev / benchmark_sold) if benchmark_sold else 0.0

    is_underperformer = (
        1 if (cancel_rate_pct > benchmark_cancel_rate and adr < benchmark_adr and adr >= 5.0) else 0
    )

    # Current period stay nights and capacity
    cur_sn = sn_df.copy()
    cur_cap = cap_df.copy()

    # Time intelligence ranges
    if "year" in criteria:
        yr = criteria["year"]
        pm_start = f"{yr - 1}-12-01"
        pm_end = f"{yr}-11-30"
        py_start = f"{yr - 1}-01-01"
        py_end = f"{yr - 1}-12-31"
    else:
        pm_start = "2014-12-01"
        pm_end = "2017-11-30"
        py_start = "2014-01-01"
        py_end = "2016-12-31"

    # Prior month stay-nights (hotel/profile filtered, shifted date range)
    pm_sn = fsn.copy()
    if "hotel" in criteria:
        pm_sn = pm_sn[pm_sn["hotel"] == criteria["hotel"]]
    if "market_segment" in criteria:
        pm_sn = pm_sn[pm_sn["market_segment"] == criteria["market_segment"]]
    if "distribution_channel" in criteria:
        pm_sn = pm_sn[pm_sn["distribution_channel"] == criteria["distribution_channel"]]
    pm_sn = pm_sn[(pm_sn["stay_date"] >= pm_start) & (pm_sn["stay_date"] <= pm_end)]
    pm_rev = float(pm_sn["adr"].sum()) if len(pm_sn) else 0.0
    rev_mom_pct = ((room_revenue - pm_rev) / pm_rev) if pm_rev else 0.0

    # Prior year stay-nights and capacity (hotel/profile filtered, shifted date range)
    py_sn = fsn.copy()
    py_cap = fc.copy()
    if "hotel" in criteria:
        py_sn = py_sn[py_sn["hotel"] == criteria["hotel"]]
        py_cap = py_cap[py_cap["hotel"] == criteria["hotel"]]
    if "market_segment" in criteria:
        py_sn = py_sn[py_sn["market_segment"] == criteria["market_segment"]]
    if "distribution_channel" in criteria:
        py_sn = py_sn[py_sn["distribution_channel"] == criteria["distribution_channel"]]
    py_sn = py_sn[(py_sn["stay_date"] >= py_start) & (py_sn["stay_date"] <= py_end)]
    py_cap = py_cap[(py_cap["date_key"] >= py_start) & (py_cap["date_key"] <= py_end)]

    py_rev = float(py_sn["adr"].sum()) if len(py_sn) else 0.0
    py_avail = int(py_cap["rooms_available"].sum()) if len(py_cap) else 0
    py_revpar = (py_rev / py_avail) if py_avail else 0.0
    revpar_yoy_pct = ((revpar - py_revpar) / py_revpar) if py_revpar else 0.0

    return {
        "Bookings": (bookings, 0),
        "Cancelled Bookings": (cancelled_bookings, 0),
        "Cancellations (Canceled status)": (cancellations_canceled, 0),
        "No-Shows": (no_shows, 0),
        "Cancel Rate %": (round(cancel_rate_pct * 100.0, 1), 0.1),
        "No-Show Rate %": (round(no_show_rate_pct * 100.0, 1), 0.1),
        "Stay Conversion %": (round(stay_conversion_pct * 100.0, 1), 0.1),
        "Avg Lead Time": (round(avg_lead_time, 1), 0.1),
        "Avg Days Cancelled Before Arrival": (round(avg_days_cancelled, 1), 0.1),
        "Room Type Mismatch %": (round(room_mismatch_pct * 100.0, 1), 0.1),
        "Room Nights Sold": (room_nights_sold, 0),
        "Room Revenue": (round(room_revenue, 2), 0.01),
        "Room Nights Available": (room_nights_available, 0),
        "ADR": (round(adr, 2), 0.01),
        "Occupancy %": (round(occupancy_pct * 100.0, 1), 0.1),
        "RevPAR": (round(revpar, 2), 0.01),
        "Revenue Share %": (round(revenue_share_pct * 100.0, 1), 0.1),
        "Room Night Share %": (round(room_night_share_pct * 100.0, 1), 0.1),
        "Revenue Prior Month": (round(pm_rev, 2), 0.01),
        "Revenue MoM %": (round(rev_mom_pct * 100.0, 1), 0.1),
        "RevPAR Prior Year": (round(py_revpar, 2), 0.01),
        "RevPAR YoY %": (round(revpar_yoy_pct * 100.0, 1), 0.1),
        "Underperformer Flag": (is_underperformer, 0),
    }


def main():
    print("=" * 95)
    print("GENERATING POWER BI VALIDATION BENCHMARKS: powerbi/validation_expected.csv")
    print("=" * 95)

    fb, fsn, fc = load_star_schema()

    scenarios = [
        ("S1", "No filters", {}),
        ("S2", "Hotel = City Hotel", {"hotel": "City Hotel"}),
        ("S3", "Hotel = Resort Hotel, Year = 2016", {"hotel": "Resort Hotel", "year": 2016}),
        ("S4", "Market Segment = Online TA", {"market_segment": "Online TA"}),
        ("S5", "Distribution Channel = Direct, Year = 2017", {"distribution_channel": "Direct", "year": 2017}),
        ("S6", "Hotel = City Hotel, Market Segment = Groups, Year = 2016", {"hotel": "City Hotel", "market_segment": "Groups", "year": 2016}),
    ]

    records = []

    for sid, slicer_desc, criteria in scenarios:
        metrics = compute_scenario_metrics(fb, fsn, fc, criteria)
        print(f"\n[{sid}] {slicer_desc}:")
        for mname, (val, tol) in metrics.items():
            if tol == 0:
                val_str = str(int(round(val)))
                tol_str = "0"
            elif tol == 0.01:
                val_str = f"{val:.2f}"
                tol_str = "0.01"
            elif tol == 0.1:
                val_str = f"{val:.1f}"
                tol_str = "0.1"
            else:
                val_str = str(val)
                tol_str = str(tol)

            records.append({
                "scenario_id": sid,
                "slicers": slicer_desc,
                "measure": mname,
                "expected_value": val_str,
                "tolerance": tol_str,
            })
            if mname in ["Bookings", "Cancel Rate %", "Avg Lead Time", "Room Nights Sold", "Room Revenue", "ADR", "Occupancy %", "RevPAR", "Revenue Share %", "Stay Conversion %"]:
                print(f"       - {mname:<22}: {val_str:>12} (tol: {tol_str})")

    df_out = pd.DataFrame(records)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(OUTPUT_FILE, index=False)

    print("\n" + "-" * 95)
    print(f"[SUCCESS] Wrote {len(df_out)} expected measure benchmarks to {OUTPUT_FILE}")
    print("=" * 95)


if __name__ == "__main__":
    main()
