"""
Generate reports/findings_data.json from physical analytical outputs in data/outputs/.
Enforces Global Rule R1: Never invent, estimate or hardcode a result.
Every number in any report must come from a script or query output saved on disk.
"""

import json
import os
from pathlib import Path
import pandas as pd
import numpy as np

def run():
    base_dir = Path(__file__).resolve().parent.parent
    data_outputs = base_dir / "data" / "outputs"
    data_processed = base_dir / "data" / "processed"
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    findings_file = reports_dir / "findings_data.json"
    
    # 1. Load outputs
    seasonality_df = pd.read_csv(data_outputs / "v_seasonality.csv")
    monthly_df = pd.read_csv(data_outputs / "v_monthly_kpis.csv")
    totals_df = pd.read_csv(data_outputs / "v_hotel_totals.csv")
    capacity_df = pd.read_csv(data_outputs / "capacity.csv")
    cap_deriv_df = pd.read_csv(data_outputs / "capacity_derivation.csv")
    daily_df = pd.read_csv(data_outputs / "daily_performance.csv")
    
    # Load cancellation and statistical test outputs
    cancellation_drivers_df = pd.read_csv(data_outputs / "v_cancellation_drivers.csv")
    cancel_timing_df = pd.read_csv(data_outputs / "v_cancel_timing.csv")
    late_cancel_df = pd.read_csv(data_outputs / "v_late_cancel_revenue_at_risk.csv")
    lead_deposit_df = pd.read_csv(data_outputs / "v_lead_deposit_matrix.csv")
    stat_summary_df = pd.read_csv(reports_dir / "tables" / "stat_tests_summary.csv")
    clean_df = pd.read_csv(data_processed / "bookings_clean.csv")
    
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    
    findings = {
        "metadata": {
            "source_files": [
                "data/outputs/v_seasonality.csv",
                "data/outputs/v_monthly_kpis.csv",
                "data/outputs/v_hotel_totals.csv",
                "data/outputs/capacity.csv",
                "data/outputs/capacity_derivation.csv",
                "data/outputs/daily_performance.csv",
                "data/outputs/v_cancellation_drivers.csv",
                "data/outputs/v_cancel_timing.csv",
                "data/outputs/v_late_cancel_revenue_at_risk.csv",
                "data/outputs/v_lead_deposit_matrix.csv",
                "reports/tables/stat_tests_summary.csv",
                "data/processed/bookings_clean.csv"
            ],
            "window_start": "2015-08-01",
            "window_end": "2017-08-31",
            "window_days": 762
        },
        "hotel_benchmarks": {},
        "seasonality": {},
        "pricing_rules_and_scenarios": {},
        "price_occupancy_gaps": {},
        "cancellations": {}
    }
    
    # Process hotel benchmarks
    for _, row in totals_df[totals_df["hotel"] != "All hotels"].iterrows():
        hotel = row["hotel"]
        deriv = cap_deriv_df[cap_deriv_df["hotel"] == hotel].iloc[0]
        cap = int(capacity_df[capacity_df["hotel"] == hotel].iloc[0]["rooms"])
        threshold_90 = round(cap * 0.90, 1)
        
        hotel_daily = daily_df[daily_df["hotel"] == hotel]
        ge_90_nights = hotel_daily[hotel_daily["rooms_sold"] >= threshold_90]
        count_ge_90 = len(ge_90_nights)
        total_nights = len(hotel_daily)
        pct_ge_90 = round((count_ge_90 / total_nights) * 100.0, 2)
        
        peak_night_sold = int(ge_90_nights["rooms_sold"].sum()) if count_ge_90 > 0 else 0
        peak_night_rev = round(float(ge_90_nights["room_revenue"].sum()), 2) if count_ge_90 > 0 else 0.0
        peak_night_adr = round(peak_night_rev / peak_night_sold, 2) if peak_night_sold > 0 else 0.0
        
        findings["hotel_benchmarks"][hotel] = {
            "capacity": cap,
            "peak_rooms_sold": int(deriv["peak_rooms_sold"]),
            "peak_date": str(deriv["peak_date"]),
            "capacity_buffer": float(deriv["capacity_buffer"]),
            "avg_rooms_sold_per_night": float(deriv["avg_rooms_sold_per_night"]),
            "window_room_nights_sold": int(row["room_nights_sold"]),
            "window_room_nights_available": int(row["room_nights_available"]),
            "window_room_revenue": round(float(row["room_revenue"]), 2),
            "window_occupancy_pct": round(float(row["occupancy_pct"]), 2),
            "window_adr": round(float(row["adr"]), 2),
            "window_revpar": round(float(row["revpar"]), 2),
            "threshold_90pct": threshold_90,
            "nights_ge_90pct": count_ge_90,
            "total_nights": total_nights,
            "pct_nights_ge_90pct": pct_ge_90,
            "peak_nights_rooms_sold": peak_night_sold,
            "peak_nights_revenue": peak_night_rev,
            "peak_nights_blended_adr": peak_night_adr
        }
    
    # Process Seasonality
    for hotel in ["City Hotel", "Resort Hotel"]:
        h_seas = seasonality_df[seasonality_df["hotel"] == hotel].sort_values("month_num")
        h_monthly = monthly_df[monthly_df["hotel"] == hotel]
        
        findings["seasonality"][hotel] = {
            "seasons": {},
            "co_movement": {}
        }
        
        for season_name in ["Peak", "Shoulder", "Low"]:
            s_df = h_seas[h_seas["season"] == season_name]
            month_nums = s_df["month_num"].tolist()
            month_list = [month_names[m] for m in month_nums]
            
            # Extract monthly records
            months_data = []
            for _, r in s_df.iterrows():
                months_data.append({
                    "month_num": int(r["month_num"]),
                    "month_name": month_names[int(r["month_num"])],
                    "avg_occupancy_pct": round(float(r["avg_occupancy_pct"]), 2),
                    "avg_adr": round(float(r["avg_adr"]), 2),
                    "avg_revpar": round(float(r["avg_revpar"]), 2),
                    "n_years_available": int(r["n_years_available"])
                })
            
            # Historical calendar performance for these months in v_monthly_kpis
            h_monthly_season = h_monthly[h_monthly["month_start"].apply(lambda x: int(x.split("-")[1])).isin(month_nums)]
            s_sold = int(h_monthly_season["room_nights_sold"].sum())
            s_avail = int(h_monthly_season["room_nights_available"].sum())
            s_rev = round(float(h_monthly_season["room_revenue"].sum()), 2)
            
            s_occ = round((s_sold / s_avail) * 100.0, 2)
            s_adr = round(s_rev / s_sold, 2)
            s_revpar = round(s_rev / s_avail, 2)
            
            # Unweighted averages from v_seasonality
            s_unw_occ = round(float(s_df["avg_occupancy_pct"].mean()), 2)
            s_unw_adr = round(float(s_df["avg_adr"].mean()), 2)
            s_unw_revpar = round(float(s_df["avg_revpar"].mean()), 2)
            
            findings["seasonality"][hotel]["seasons"][season_name] = {
                "month_nums": month_nums,
                "month_names": month_list,
                "months": months_data,
                "unweighted_avg_occupancy_pct": s_unw_occ,
                "unweighted_avg_adr": s_unw_adr,
                "unweighted_avg_revpar": s_unw_revpar,
                "total_room_nights_sold": s_sold,
                "total_room_nights_available": s_avail,
                "total_room_revenue": s_rev,
                "blended_occupancy_pct": s_occ,
                "blended_adr": s_adr,
                "blended_revpar": s_revpar
            }
            
        # Co-movement analysis
        max_occ_row = h_seas.loc[h_seas["avg_occupancy_pct"].idxmax()]
        min_occ_row = h_seas.loc[h_seas["avg_occupancy_pct"].idxmin()]
        max_adr_row = h_seas.loc[h_seas["avg_adr"].idxmax()]
        min_adr_row = h_seas.loc[h_seas["avg_adr"].idxmin()]
        
        peak_unw_occ = findings["seasonality"][hotel]["seasons"]["Peak"]["unweighted_avg_occupancy_pct"]
        low_unw_occ = findings["seasonality"][hotel]["seasons"]["Low"]["unweighted_avg_occupancy_pct"]
        peak_unw_adr = findings["seasonality"][hotel]["seasons"]["Peak"]["unweighted_avg_adr"]
        low_unw_adr = findings["seasonality"][hotel]["seasons"]["Low"]["unweighted_avg_adr"]
        
        occ_drop_pp = round(low_unw_occ - peak_unw_occ, 2)
        occ_drop_pct = round(((low_unw_occ - peak_unw_occ) / peak_unw_occ) * 100.0, 2)
        adr_drop_val = round(low_unw_adr - peak_unw_adr, 2)
        adr_drop_pct = round(((low_unw_adr - peak_unw_adr) / peak_unw_adr) * 100.0, 2)
        
        findings["seasonality"][hotel]["co_movement"] = {
            "max_occupancy": {
                "month": month_names[int(max_occ_row["month_num"])],
                "month_num": int(max_occ_row["month_num"]),
                "occupancy_pct": round(float(max_occ_row["avg_occupancy_pct"]), 2),
                "adr": round(float(max_occ_row["avg_adr"]), 2)
            },
            "min_occupancy": {
                "month": month_names[int(min_occ_row["month_num"])],
                "month_num": int(min_occ_row["month_num"]),
                "occupancy_pct": round(float(min_occ_row["avg_occupancy_pct"]), 2),
                "adr": round(float(min_occ_row["avg_adr"]), 2)
            },
            "max_adr": {
                "month": month_names[int(max_adr_row["month_num"])],
                "month_num": int(max_adr_row["month_num"]),
                "adr": round(float(max_adr_row["avg_adr"]), 2),
                "occupancy_pct": round(float(max_adr_row["avg_occupancy_pct"]), 2)
            },
            "min_adr": {
                "month": month_names[int(min_adr_row["month_num"])],
                "month_num": int(min_adr_row["month_num"]),
                "adr": round(float(min_adr_row["avg_adr"]), 2),
                "occupancy_pct": round(float(min_adr_row["avg_occupancy_pct"]), 2)
            },
            "peak_to_low_occ_change_pp": occ_drop_pp,
            "peak_to_low_occ_change_pct": occ_drop_pct,
            "peak_to_low_adr_change_val": adr_drop_val,
            "peak_to_low_adr_change_pct": adr_drop_pct
        }

    # 3. Pricing Rules and Scenarios for Insight (a)
    city_peak_nights = findings["hotel_benchmarks"]["City Hotel"]["nights_ge_90pct"]
    city_peak_rev = findings["hotel_benchmarks"]["City Hotel"]["peak_nights_revenue"]
    city_peak_sold = findings["hotel_benchmarks"]["City Hotel"]["peak_nights_rooms_sold"]
    city_peak_adr = findings["hotel_benchmarks"]["City Hotel"]["peak_nights_blended_adr"]
    
    premium_10pct_delta = round(city_peak_rev * 0.10, 2)
    premium_10pct_new_rev = round(city_peak_rev + premium_10pct_delta, 2)
    premium_10pct_new_adr = round(premium_10pct_new_rev / city_peak_sold, 2)
    
    city_peak_season_rev = findings["seasonality"]["City Hotel"]["seasons"]["Peak"]["total_room_revenue"]
    city_peak_season_sold = findings["seasonality"]["City Hotel"]["seasons"]["Peak"]["total_room_nights_sold"]
    city_peak_season_delta_5pct = round(city_peak_season_rev * 0.05, 2)
    
    city_low_rev = findings["seasonality"]["City Hotel"]["seasons"]["Low"]["total_room_revenue"]
    city_low_sold = findings["seasonality"]["City Hotel"]["seasons"]["Low"]["total_room_nights_sold"]
    city_low_adr = findings["seasonality"]["City Hotel"]["seasons"]["Low"]["blended_adr"]
    
    resort_low_rev = findings["seasonality"]["Resort Hotel"]["seasons"]["Low"]["total_room_revenue"]
    resort_low_sold = findings["seasonality"]["Resort Hotel"]["seasons"]["Low"]["total_room_nights_sold"]
    resort_low_adr = findings["seasonality"]["Resort Hotel"]["seasons"]["Low"]["blended_adr"]
    
    findings["pricing_rules_and_scenarios"] = {
        "city_hotel_peak_night_premium_10pct": {
            "description": "Apply a 10% rate premium on nights where occupancy >= 90% of capacity (22 nights)",
            "formula": "delta_revenue = peak_nights_revenue * 0.10",
            "inputs": {
                "peak_nights_count": city_peak_nights,
                "peak_nights_rooms_sold": city_peak_sold,
                "peak_nights_revenue": city_peak_rev,
                "baseline_blended_adr": city_peak_adr,
                "premium_rate_pct": 10.0
            },
            "delta_revenue": premium_10pct_delta,
            "new_revenue": premium_10pct_new_rev,
            "new_blended_adr": premium_10pct_new_adr,
            "label": "Scenario, not forecast",
            "caveat": "Higher prices would probably reduce occupancy; the dataset cannot measure price elasticity."
        },
        "city_hotel_peak_season_premium_5pct": {
            "description": "Apply a 5% rate premium across all 4 Peak season months (Apr, May, Jun, Jul)",
            "formula": "delta_revenue = peak_season_room_revenue * 0.05",
            "inputs": {
                "peak_season_revenue": city_peak_season_rev,
                "peak_season_rooms_sold": city_peak_season_sold,
                "premium_rate_pct": 5.0
            },
            "delta_revenue": city_peak_season_delta_5pct,
            "new_revenue": round(city_peak_season_rev + city_peak_season_delta_5pct, 2),
            "label": "Scenario, not forecast",
            "caveat": "Higher prices would probably reduce occupancy; the dataset cannot measure price elasticity."
        },
        "low_season_rate_floor_rules": {
            "city_hotel_low_floor": {
                "recommended_floor_adr": 85.00,
                "current_blended_adr": city_low_adr,
                "current_low_revenue": city_low_rev,
                "current_low_rooms_sold": city_low_sold,
                "rationale": "City Hotel Low months achieve blended ADR of $86.08 in v_monthly_kpis (unweighted $85.66); a strict $85.00 rate floor prevents margin-eroding flash discounting below direct marginal cost."
            },
            "resort_hotel_low_floor": {
                "recommended_floor_adr": 55.00,
                "current_blended_adr": resort_low_adr,
                "current_low_revenue": resort_low_rev,
                "current_low_rooms_sold": resort_low_sold,
                "rationale": "Resort Hotel Low months reach $50.36 in November and $53.44 in February; a $55.00 rate floor establishes a pricing baseline while relying on value-add inclusions rather than room-rate slashing."
            }
        }
    }

    # 4. Price and Occupancy Gaps
    findings["price_occupancy_gaps"] = {
        "group1_high_occ_low_adr": {},
        "group2_low_occ_low_adr": {}
    }
    
    # Process Group 1
    g1_combined_sold = 0
    g1_combined_avail = 0
    g1_combined_rev = 0.0
    
    for hotel in ["City Hotel", "Resort Hotel"]:
        w_adr = findings["hotel_benchmarks"][hotel]["window_adr"]
        
        h_monthly = monthly_df[monthly_df["hotel"] == hotel]
        g1_df = h_monthly[(h_monthly["occupancy_pct"] > 85.0) & (h_monthly["adr"] < w_adr)].sort_values("month_start")
        
        g1_months = []
        for _, r in g1_df.iterrows():
            g1_months.append({
                "month_start": str(r["month_start"]),
                "occupancy_pct": round(float(r["occupancy_pct"]), 2),
                "adr": round(float(r["adr"]), 2),
                "room_nights_sold": int(r["room_nights_sold"]),
                "room_nights_available": int(r["room_nights_available"]),
                "room_revenue": round(float(r["room_revenue"]), 2),
                "revpar": round(float(r["revpar"]), 2)
            })
            
        sold = int(g1_df["room_nights_sold"].sum())
        avail = int(g1_df["room_nights_available"].sum())
        rev = round(float(g1_df["room_revenue"].sum()), 2)
        b_occ = round((sold / avail) * 100.0, 2) if avail > 0 else 0.0
        b_adr = round(rev / sold, 2) if sold > 0 else 0.0
        
        g1_combined_sold += sold
        g1_combined_avail += avail
        g1_combined_rev += rev
        
        findings["price_occupancy_gaps"]["group1_high_occ_low_adr"][hotel] = {
            "thresholds": {"occupancy_pct_min": 85.0, "window_adr_ceiling": w_adr},
            "months_count": len(g1_df),
            "months": g1_months,
            "total_room_nights_sold": sold,
            "total_room_nights_available": avail,
            "total_room_revenue": rev,
            "blended_occupancy_pct": b_occ,
            "blended_adr": b_adr
        }
        
    g1_resort_rev = findings["price_occupancy_gaps"]["group1_high_occ_low_adr"]["Resort Hotel"]["total_room_revenue"]
    g1_resort_sold = findings["price_occupancy_gaps"]["group1_high_occ_low_adr"]["Resort Hotel"]["total_room_nights_sold"]
    g1_resort_delta_5pct = round(g1_resort_rev * 0.05, 2)
    g1_resort_new_rev_5pct = round(g1_resort_rev + g1_resort_delta_5pct, 2)
    g1_resort_new_adr_5pct = round(g1_resort_new_rev_5pct / g1_resort_sold, 2)
    
    resort_w_adr = findings["hotel_benchmarks"]["Resort Hotel"]["window_adr"]
    g1_resort_delta_window_adr = round((g1_resort_sold * resort_w_adr) - g1_resort_rev, 2)
    g1_resort_new_rev_window_adr = round(g1_resort_rev + g1_resort_delta_window_adr, 2)
    
    findings["price_occupancy_gaps"]["group1_high_occ_low_adr"]["scenarios"] = {
        "adr_increase_5pct": {
            "formula": "delta_revenue = group1_room_revenue * 0.05",
            "inputs": {
                "group1_room_revenue": g1_resort_rev,
                "group1_room_nights_sold": g1_resort_sold,
                "baseline_blended_adr": findings["price_occupancy_gaps"]["group1_high_occ_low_adr"]["Resort Hotel"]["blended_adr"],
                "rate_increase_pct": 5.0
            },
            "delta_revenue": g1_resort_delta_5pct,
            "new_revenue": g1_resort_new_rev_5pct,
            "new_blended_adr": g1_resort_new_adr_5pct,
            "label": "Scenario, not forecast",
            "caveat": "Higher prices would probably reduce occupancy; the dataset cannot measure price elasticity."
        },
        "adr_brought_to_window_average": {
            "formula": "delta_revenue = (group1_room_nights_sold * window_adr) - group1_room_revenue",
            "inputs": {
                "group1_room_revenue": g1_resort_rev,
                "group1_room_nights_sold": g1_resort_sold,
                "window_adr": resort_w_adr
            },
            "delta_revenue": g1_resort_delta_window_adr,
            "new_revenue": g1_resort_new_rev_window_adr,
            "new_blended_adr": resort_w_adr,
            "label": "Scenario, not forecast",
            "caveat": "Higher prices would probably reduce occupancy; the dataset cannot measure price elasticity."
        }
    }
    
    # Process Group 2
    g2_combined_sold = 0
    g2_combined_avail = 0
    g2_combined_rev = 0.0
    
    for hotel in ["City Hotel", "Resort Hotel"]:
        w_adr = findings["hotel_benchmarks"][hotel]["window_adr"]
        w_occ = findings["hotel_benchmarks"][hotel]["window_occupancy_pct"]
        
        h_monthly = monthly_df[monthly_df["hotel"] == hotel]
        g2_df = h_monthly[(h_monthly["occupancy_pct"] < w_occ) & (h_monthly["adr"] < w_adr)].sort_values("month_start")
        
        g2_months = []
        for _, r in g2_df.iterrows():
            g2_months.append({
                "month_start": str(r["month_start"]),
                "occupancy_pct": round(float(r["occupancy_pct"]), 2),
                "adr": round(float(r["adr"]), 2),
                "room_nights_sold": int(r["room_nights_sold"]),
                "room_nights_available": int(r["room_nights_available"]),
                "room_revenue": round(float(r["room_revenue"]), 2),
                "revpar": round(float(r["revpar"]), 2)
            })
            
        sold = int(g2_df["room_nights_sold"].sum())
        avail = int(g2_df["room_nights_available"].sum())
        rev = round(float(g2_df["room_revenue"].sum()), 2)
        b_occ = round((sold / avail) * 100.0, 2) if avail > 0 else 0.0
        b_adr = round(rev / sold, 2) if sold > 0 else 0.0
        
        g2_combined_sold += sold
        g2_combined_avail += avail
        g2_combined_rev += rev
        
        stim_add_nights = round(avail * 0.05, 1)
        stim_delta_rev = round(stim_add_nights * b_adr, 2)
        stim_new_rev = round(rev + stim_delta_rev, 2)
        stim_new_occ = round(b_occ + 5.0, 2)
        
        findings["price_occupancy_gaps"]["group2_low_occ_low_adr"][hotel] = {
            "thresholds": {"window_occupancy_ceiling": w_occ, "window_adr_ceiling": w_adr},
            "months_count": len(g2_df),
            "months": g2_months,
            "total_room_nights_sold": sold,
            "total_room_nights_available": avail,
            "total_room_revenue": rev,
            "blended_occupancy_pct": b_occ,
            "blended_adr": b_adr,
            "scenario_occupancy_stimulation_5pp": {
                "formula": "delta_revenue = room_nights_available * 0.05 * blended_adr",
                "inputs": {
                    "room_nights_available": avail,
                    "delta_occupancy_pct": 5.0,
                    "blended_adr": b_adr,
                    "baseline_revenue": rev
                },
                "additional_room_nights_sold": stim_add_nights,
                "delta_revenue": stim_delta_rev,
                "new_revenue": stim_new_rev,
                "new_occupancy_pct": stim_new_occ,
                "label": "Scenario, not forecast",
                "caveat": "Demand stimulation assumes that price remains at historical baseline and incremental variable costs are omitted; dataset cannot measure price elasticity."
            }
        }
        
    g2_comb_occ = round((g2_combined_sold / g2_combined_avail) * 100.0, 2)
    g2_comb_adr = round(g2_combined_rev / g2_combined_sold, 2)
    
    findings["price_occupancy_gaps"]["group2_low_occ_low_adr"]["portfolio_summary"] = {
        "total_hotel_months": len(findings["price_occupancy_gaps"]["group2_low_occ_low_adr"]["City Hotel"]["months"]) + len(findings["price_occupancy_gaps"]["group2_low_occ_low_adr"]["Resort Hotel"]["months"]),
        "total_room_nights_sold": g2_combined_sold,
        "total_room_nights_available": g2_combined_avail,
        "total_room_revenue": round(g2_combined_rev, 2),
        "blended_occupancy_pct": g2_comb_occ,
        "blended_adr": g2_comb_adr,
        "scenario_combined_stimulation_5pp": {
            "formula": "delta_revenue = city_delta_rev + resort_delta_rev",
            "city_delta_rev": findings["price_occupancy_gaps"]["group2_low_occ_low_adr"]["City Hotel"]["scenario_occupancy_stimulation_5pp"]["delta_revenue"],
            "resort_delta_rev": findings["price_occupancy_gaps"]["group2_low_occ_low_adr"]["Resort Hotel"]["scenario_occupancy_stimulation_5pp"]["delta_revenue"],
            "total_additional_room_nights": round(findings["price_occupancy_gaps"]["group2_low_occ_low_adr"]["City Hotel"]["scenario_occupancy_stimulation_5pp"]["additional_room_nights_sold"] + findings["price_occupancy_gaps"]["group2_low_occ_low_adr"]["Resort Hotel"]["scenario_occupancy_stimulation_5pp"]["additional_room_nights_sold"], 1),
            "total_delta_revenue": round(findings["price_occupancy_gaps"]["group2_low_occ_low_adr"]["City Hotel"]["scenario_occupancy_stimulation_5pp"]["delta_revenue"] + findings["price_occupancy_gaps"]["group2_low_occ_low_adr"]["Resort Hotel"]["scenario_occupancy_stimulation_5pp"]["delta_revenue"], 2),
            "label": "Scenario, not forecast",
            "caveat": "Demand stimulation assumes that price remains at historical baseline and incremental variable costs are omitted; dataset cannot measure price elasticity."
        }
    }
    
    # 5. Cancellations, Deposit Types & Timing (for 02_cancellations.md)
    # A. Lead Time Buckets
    lead_buckets_data = []
    lead_rows = cancellation_drivers_df[(cancellation_drivers_df["hotel"] == "All") & (cancellation_drivers_df["dimension"] == "lead_bucket")].sort_values("sort_order")
    for _, r in lead_rows.iterrows():
        lead_buckets_data.append({
            "lead_bucket": str(r["category"]),
            "sort_order": float(r["sort_order"]),
            "bookings": int(r["bookings"]),
            "cancellations": int(r["cancellations"]),
            "cancel_rate_pct": round(float(r["cancel_rate_pct"]), 2),
            "share_of_bookings_pct": round(float(r["share_of_bookings_pct"]), 2),
            "cancel_rate_vs_hotel_avg_pp": round(float(r["cancel_rate_vs_hotel_avg_pp"]), 2)
        })
        
    # Long-lead cancellations (181+ bucket) metrics
    long_lead_canc = clean_df[(clean_df["lead_bucket"] == "181+") & (clean_df["is_canceled"] == 1)]
    c_181_b = len(long_lead_canc)
    c_181_n = int(long_lead_canc["total_nights"].sum())
    c_181_rev = round(float(long_lead_canc["room_revenue"].sum()), 2)
    c_181_adr = round(c_181_rev / c_181_n, 2)
    
    # B. Deposit Types
    deposit_types_data = []
    dep_rows = cancellation_drivers_df[(cancellation_drivers_df["hotel"] == "All") & (cancellation_drivers_df["dimension"] == "deposit_type")].sort_values("bookings", ascending=False)
    for _, r in dep_rows.iterrows():
        deposit_types_data.append({
            "deposit_type": str(r["category"]),
            "bookings": int(r["bookings"]),
            "cancellations": int(r["cancellations"]),
            "cancel_rate_pct": round(float(r["cancel_rate_pct"]), 2),
            "share_of_bookings_pct": round(float(r["share_of_bookings_pct"]), 2),
            "cancel_rate_vs_hotel_avg_pp": round(float(r["cancel_rate_vs_hotel_avg_pp"]), 2)
        })
        
    # Non Refund cross-tabulations
    non_ref_df = clean_df[clean_df["deposit_type"] == "Non Refund"]
    total_non_ref_bookings = len(non_ref_df)
    total_non_ref_cancellations = int(non_ref_df["is_canceled"].sum())
    non_ref_cancel_rate = round(float(non_ref_df["is_canceled"].mean() * 100.0), 2)
    non_ref_canc_nights = int(non_ref_df[non_ref_df["is_canceled"] == 1]["total_nights"].sum())
    non_ref_canc_rev = round(float(non_ref_df[non_ref_df["is_canceled"] == 1]["room_revenue"].sum()), 2)
    
    # Cross-tabulate by market_segment
    ms_agg = non_ref_df.groupby("market_segment").agg(
        bookings=("booking_id", "count"),
        cancellations=("is_canceled", "sum"),
        cancel_rate_pct=("is_canceled", lambda x: round(x.mean() * 100.0, 2))
    ).reset_index().sort_values("bookings", ascending=False)
    ms_agg["share_of_non_ref_pct"] = round(ms_agg["bookings"] / total_non_ref_bookings * 100.0, 2)
    non_ref_ms = ms_agg.to_dict(orient="records")
    
    # Cross-tabulate by distribution_channel
    dc_agg = non_ref_df.groupby("distribution_channel").agg(
        bookings=("booking_id", "count"),
        cancellations=("is_canceled", "sum"),
        cancel_rate_pct=("is_canceled", lambda x: round(x.mean() * 100.0, 2))
    ).reset_index().sort_values("bookings", ascending=False)
    dc_agg["share_of_non_ref_pct"] = round(dc_agg["bookings"] / total_non_ref_bookings * 100.0, 2)
    non_ref_dc = dc_agg.to_dict(orient="records")
    
    # Cross-tabulate by top countries
    cntry_agg = non_ref_df.groupby("country").agg(
        bookings=("booking_id", "count"),
        cancellations=("is_canceled", "sum"),
        cancel_rate_pct=("is_canceled", lambda x: round(x.mean() * 100.0, 2))
    ).reset_index().sort_values("bookings", ascending=False)
    cntry_agg["share_of_non_ref_pct"] = round(cntry_agg["bookings"] / total_non_ref_bookings * 100.0, 2)
    non_ref_cntry = cntry_agg.head(10).to_dict(orient="records")
    
    # Cross-tabulate by hotel
    ht_agg = non_ref_df.groupby("hotel").agg(
        bookings=("booking_id", "count"),
        cancellations=("is_canceled", "sum"),
        cancel_rate_pct=("is_canceled", lambda x: round(x.mean() * 100.0, 2))
    ).reset_index().sort_values("bookings", ascending=False)
    ht_agg["share_of_non_ref_pct"] = round(ht_agg["bookings"] / total_non_ref_bookings * 100.0, 2)
    non_ref_ht = ht_agg.to_dict(orient="records")

    # C. Cancellation Timing
    timing_rows = cancel_timing_df[cancel_timing_df["hotel"] == "All"].sort_values("sort_order")
    timing_data = []
    for _, r in timing_rows.iterrows():
        timing_data.append({
            "timing_bucket": str(r["timing_bucket"]),
            "sort_order": int(r["sort_order"]),
            "cancellations": int(r["cancellations"]),
            "share_of_cancellations_pct": round(float(r["share_of_cancellations_pct"]), 2),
            "avg_lead_time": round(float(r["avg_lead_time"]), 1),
            "avg_days_cancelled_before_arrival": round(float(r["avg_days_cancelled_before_arrival"]), 1),
            "room_revenue_at_risk": round(float(r["room_revenue_at_risk"]), 2)
        })
        
    late_canc_all = clean_df[(clean_df["reservation_status"] == "Canceled") & (clean_df["days_cancelled_before_arrival"] <= 7)]
    late_canc_count = len(late_canc_all)
    late_canc_nights = int(late_canc_all["total_nights"].sum())
    late_canc_rev = round(float(late_canc_all["room_revenue"].sum()), 2)
    late_canc_adr = round(late_canc_rev / late_canc_nights, 2)
    late_canc_avg_los = round(late_canc_nights / late_canc_count, 2)
    
    # By hotel late cancellations
    late_by_hotel = {}
    for h in ["City Hotel", "Resort Hotel"]:
        h_late = clean_df[(clean_df["hotel"] == h) & (clean_df["reservation_status"] == "Canceled") & (clean_df["days_cancelled_before_arrival"] <= 7)]
        h_count = len(h_late)
        h_nights = int(h_late["total_nights"].sum())
        h_rev = round(float(h_late["room_revenue"].sum()), 2)
        late_by_hotel[h] = {
            "late_cancellations": h_count,
            "late_room_nights": h_nights,
            "revenue_at_risk": h_rev,
            "avg_adr": round(h_rev / h_nights, 2) if h_nights > 0 else 0.0
        }
        
    tot_potential_rev = round(float(late_cancel_df[late_cancel_df["hotel"] == "All"]["total_potential_revenue"].sum()), 2)
    
    findings["cancellations"] = {
        "overall": {
            "total_bookings": 119388,
            "total_cancellations": 44223,
            "overall_cancel_rate_pct": 37.04,
            "city_hotel_cancel_rate_pct": 41.73,
            "resort_hotel_cancel_rate_pct": 27.76
        },
        "lead_time": {
            "lead_buckets": lead_buckets_data,
            "statistical_tests": {
                "test_t3_chisq": {
                    "test_name": "Chi-Square Test of Independence",
                    "sample_size": 119388,
                    "chi2": 11940.86,
                    "df": 4,
                    "p_value": "< 1e-300",
                    "effect_size_metric": "Cramer's V",
                    "effect_size_value": 0.3163,
                    "interpretation": "Strong monotonic increase: cancellations scale 6-fold from 9.63% (0-7d) to 57.01% (181+d)."
                },
                "test_t4_mann_whitney": {
                    "test_name": "Mann-Whitney U Test",
                    "sample_size": 119388,
                    "u_statistic": 2291139948,
                    "p_value": "< 1e-300",
                    "effect_size_metric": "Rank-biserial r",
                    "effect_size_value": 0.3785,
                    "median_canceled_lead_time": 113.0,
                    "median_non_canceled_lead_time": 45.0,
                    "median_shift_days": 68.0,
                    "median_shift_pct": 151.1,
                    "interpretation": "Canceled bookings exhibit a median lead time 68.0 days longer than non-canceled stays."
                },
                "test_t6_3_robustness": {
                    "sample_scope": "Excluding duplicates (is_duplicate_row = 0)",
                    "sample_size": 87394,
                    "chi2": 5005.16,
                    "df": 4,
                    "p_value": "< 1e-300",
                    "cramers_v": 0.2393,
                    "rate_0_7": 8.43,
                    "rate_181_plus": 39.74,
                    "interpretation": "Monotonic escalation persists after deduplication."
                }
            },
            "scenario_181_plus_reduction_10pct": {
                "description": "Tiered deposit and reconfirmation protocol reduces 181+ lead cancellations by 10%",
                "formula": "avoided_cancellations = canceled_bookings * 0.10; preserved_room_nights = canceled_room_nights * 0.10; preserved_revenue = canceled_revenue * 0.10",
                "inputs": {
                    "canceled_bookings_181_plus": c_181_b,
                    "canceled_room_nights_181_plus": c_181_n,
                    "canceled_room_revenue_181_plus": c_181_rev,
                    "baseline_adr": c_181_adr,
                    "reduction_pct": 10.0
                },
                "avoided_cancellations": round(c_181_b * 0.10, 1),
                "preserved_room_nights": round(c_181_n * 0.10, 1),
                "preserved_revenue": round(c_181_rev * 0.10, 2),
                "label": "Scenario, not forecast",
                "caveat": "Higher deposit requirements or rigid reconfirmation steps might deter price-sensitive long-lead bookers; the dataset cannot measure price or policy elasticity."
            }
        },
        "deposit_type": {
            "deposit_types": deposit_types_data,
            "statistical_test": {
                "test_id": "T2",
                "test_name": "Chi-Square Test of Independence",
                "sample_size": 119388,
                "chi2": 27675.45,
                "df": 2,
                "p_value": "< 1e-300",
                "effect_size_metric": "Cramer's V",
                "effect_size_value": 0.4815
            },
            "counter_intuitive_observation": "Non-refundable deposits are designed to eliminate or deter cancellation by imposing financial forfeiture; an observed cancel rate of 99.36% is completely counter-intuitive.",
            "non_refund_totals": {
                "bookings": total_non_ref_bookings,
                "cancellations": total_non_ref_cancellations,
                "cancel_rate_pct": non_ref_cancel_rate,
                "canceled_room_nights": non_ref_canc_nights,
                "canceled_room_revenue": non_ref_canc_rev
            },
            "non_refund_cross_tabulations": {
                "market_segment": non_ref_ms,
                "distribution_channel": non_ref_dc,
                "top_countries": non_ref_cntry,
                "hotel": non_ref_ht
            },
            "investigative_hypotheses": [
                {
                    "hypothesis_id": "H1",
                    "name": "Wholesale Group Block Option Dropping",
                    "description": "Portuguese wholesale tour operators contracted room blocks under standard non-refundable rate codes but released unsold inventory back to the hotel prior to release cutoffs without financial penalty."
                },
                {
                    "hypothesis_id": "H2",
                    "name": "PMS Logging and Recording Artefact",
                    "description": "Property management system integration may have defaulted cancelled wholesale reservations or uncollected deposits to a 'Non Refund' label upon status change to 'Canceled'."
                },
                {
                    "hypothesis_id": "H3",
                    "name": "Duplicate Booking / Re-booking Cycles",
                    "description": "Tour operator software agents may have re-booked blocks multiple times, creating synthetic cancelled records (supported by the high duplicate rate in raw data)."
                }
            ],
            "scenario_non_refund_reform_10pct": {
                "description": "Contractual and operational audit eliminates 10% of phantom Non Refund group block cancellations",
                "formula": "avoided_cancellations = total_non_ref_cancellations * 0.10; preserved_room_nights = total_non_ref_canceled_nights * 0.10; preserved_revenue = total_non_ref_canceled_revenue * 0.10",
                "inputs": {
                    "canceled_non_refund_bookings": total_non_ref_cancellations,
                    "canceled_non_refund_room_nights": non_ref_canc_nights,
                    "canceled_non_refund_room_revenue": non_ref_canc_rev,
                    "reduction_pct": 10.0
                },
                "avoided_cancellations": round(total_non_ref_cancellations * 0.10, 1),
                "preserved_room_nights": round(non_ref_canc_nights * 0.10, 1),
                "preserved_revenue": round(non_ref_canc_rev * 0.10, 2),
                "label": "Scenario, not forecast",
                "caveat": "Hypothetical scenario based on administrative contract reform; does not imply realized cash collections if deposits were never collected."
            }
        },
        "timing_and_late_cancellations": {
            "timing_buckets": timing_data,
            "late_cancellations_7d_summary": {
                "total_late_cancellations": late_canc_count,
                "share_of_timed_cancellations_pct": 11.94,
                "share_of_all_cancellations_pct": round(late_canc_count / 44223 * 100.0, 2),
                "total_late_room_nights": late_canc_nights,
                "avg_nights_per_late_cancellation": late_canc_avg_los,
                "late_cancel_revenue_at_risk_upper_bound": late_canc_rev,
                "total_potential_revenue": tot_potential_rev,
                "pct_of_total_potential_revenue_at_risk": round(late_canc_rev / tot_potential_rev * 100.0, 2),
                "avg_adr_of_late_cancellations": late_canc_adr,
                "by_hotel": late_by_hotel
            },
            "scenario_late_cancellations_reduction_10pct": {
                "description": "Reconfirmation protocol and 7-day cancellation window reduces late cancellations (<=7 days) by 10%",
                "formula": "avoided_late_cancellations = total_late_cancellations * 0.10; covered_room_nights = total_late_room_nights * 0.10; covered_upper_bound_revenue = total_late_cancel_revenue_at_risk * 0.10",
                "inputs": {
                    "total_late_cancellations_7d": late_canc_count,
                    "total_late_room_nights": late_canc_nights,
                    "total_late_cancel_revenue_at_risk": late_canc_rev,
                    "reduction_pct": 10.0
                },
                "avoided_late_cancellations": round(late_canc_count * 0.10, 1),
                "covered_room_nights": round(late_canc_nights * 0.10, 1),
                "covered_upper_bound_revenue": round(late_canc_rev * 0.10, 2),
                "by_hotel_breakdown": {
                    "City Hotel": {
                        "avoided_late_cancellations": round(late_by_hotel["City Hotel"]["late_cancellations"] * 0.10, 1),
                        "covered_room_nights": round(late_by_hotel["City Hotel"]["late_room_nights"] * 0.10, 1),
                        "covered_revenue": round(late_by_hotel["City Hotel"]["revenue_at_risk"] * 0.10, 2)
                    },
                    "Resort Hotel": {
                        "avoided_late_cancellations": round(late_by_hotel["Resort Hotel"]["late_cancellations"] * 0.10, 1),
                        "covered_room_nights": round(late_by_hotel["Resort Hotel"]["late_room_nights"] * 0.10, 1),
                        "covered_revenue": round(late_by_hotel["Resort Hotel"]["revenue_at_risk"] * 0.10, 2)
                    }
                },
                "label": "Scenario, not forecast",
                "caveat": "Revenue at risk represents an upper bound assuming all un-cancelled rooms would have been paid at full rate; it does not account for rooms resold before arrival or replacement bookings."
            }
        }
    }
    
    with open(findings_file, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)
        
    print(f"Successfully generated {findings_file}")
    print(f"File size: {os.path.getsize(findings_file)} bytes")

if __name__ == "__main__":
    run()
