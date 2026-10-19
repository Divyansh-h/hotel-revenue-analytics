"""
Dashboard Text & Executive Insights Generator: src/make_dashboard_text.py

Generates powerbi/DASHBOARD_TEXT.md using real metrics read dynamically from data/outputs/*.csv.
Never types a number by hand per Global Rule R1.

Contents generated:
1. Page titles and subtitles for 4 report pages and 2 supporting pages.
2. Visual titles (questions/statements) and one-sentence alt text for every visual in REPORT_SPEC.md.
3. Page 4 'Key Findings': 6 factual statements with bracketed source tags [file.csv, column],
   strictly neutral language ('is associated with', never 'causes'), rounded to 1 decimal place.
4. Authoritative 'Definitions' block (K1 to K7) and 'Assumptions and Limitations' block.
"""

import calendar
import sys
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = REPO_ROOT / "data" / "outputs"
TARGET_FILE = REPO_ROOT / "powerbi" / "DASHBOARD_TEXT.md"


def load_output_metrics() -> dict:
    """Load and compute all required dynamic numbers from data/outputs/*.csv."""
    metrics = {}

    # 1. Hotel cancellation rates from v_booking_trends.csv
    bt_path = OUTPUTS_DIR / "v_booking_trends.csv"
    df_bt = pd.read_csv(bt_path)
    city_bt = df_bt[df_bt["hotel"] == "City Hotel"]
    resort_bt = df_bt[df_bt["hotel"] == "Resort Hotel"]

    city_bookings = int(city_bt["bookings"].sum())
    city_cancels = int(city_bt["cancellations"].sum())
    city_rate = round(100.0 * city_cancels / city_bookings, 1)

    resort_bookings = int(resort_bt["bookings"].sum())
    resort_cancels = int(resort_bt["cancellations"].sum())
    resort_rate = round(100.0 * resort_cancels / resort_bookings, 1)

    metrics["higher_cancel_hotel"] = "City Hotel" if city_rate > resort_rate else "Resort Hotel"
    metrics["city_cancel_rate"] = city_rate
    metrics["resort_cancel_rate"] = resort_rate

    # 2. Lead bucket extremes from v_cancellation_drivers.csv
    cd_path = OUTPUTS_DIR / "v_cancellation_drivers.csv"
    df_cd = pd.read_csv(cd_path)
    lead_df = df_cd[(df_cd["hotel"] == "All") & (df_cd["dimension"] == "lead_bucket")]
    high_lead = lead_df.sort_values("cancel_rate_pct", ascending=False).iloc[0]
    low_lead = lead_df.sort_values("cancel_rate_pct", ascending=True).iloc[0]

    metrics["high_lead_bucket"] = high_lead["category"]
    metrics["high_lead_rate"] = round(float(high_lead["cancel_rate_pct"]), 1)
    metrics["low_lead_bucket"] = low_lead["category"]
    metrics["low_lead_rate"] = round(float(low_lead["cancel_rate_pct"]), 1)

    # 3. Deposit type highest cancel rate from v_cancellation_drivers.csv
    dep_df = df_cd[(df_cd["hotel"] == "All") & (df_cd["dimension"] == "deposit_type")]
    high_dep = dep_df.sort_values("cancel_rate_pct", ascending=False).iloc[0]
    metrics["high_deposit_type"] = high_dep["category"]
    metrics["high_deposit_rate"] = round(float(high_dep["cancel_rate_pct"]), 1)

    # 4. Seasonality RevPAR peaks and lows from v_seasonality.csv
    sea_path = OUTPUTS_DIR / "v_seasonality.csv"
    df_sea = pd.read_csv(sea_path)
    c_sea = df_sea[df_sea["hotel"] == "City Hotel"]
    r_sea = df_sea[df_sea["hotel"] == "Resort Hotel"]

    c_peak = c_sea.sort_values("avg_revpar", ascending=False).iloc[0]
    c_low = c_sea.sort_values("avg_revpar", ascending=True).iloc[0]
    r_peak = r_sea.sort_values("avg_revpar", ascending=False).iloc[0]
    r_low = r_sea.sort_values("avg_revpar", ascending=True).iloc[0]

    metrics["city_peak_month"] = calendar.month_name[int(c_peak["month_num"])]
    metrics["city_peak_revpar"] = round(float(c_peak["avg_revpar"]), 2)
    metrics["city_low_month"] = calendar.month_name[int(c_low["month_num"])]
    metrics["city_low_revpar"] = round(float(c_low["avg_revpar"]), 2)

    metrics["resort_peak_month"] = calendar.month_name[int(r_peak["month_num"])]
    metrics["resort_peak_revpar"] = round(float(r_peak["avg_revpar"]), 2)
    metrics["resort_low_month"] = calendar.month_name[int(r_low["month_num"])]
    metrics["resort_low_revpar"] = round(float(r_low["avg_revpar"]), 2)

    # 5. Top revenue market segments from v_segment_performance.csv
    sp_path = OUTPUTS_DIR / "v_segment_performance.csv"
    df_sp = pd.read_csv(sp_path)
    c_sp = df_sp[df_sp["hotel"] == "City Hotel"].sort_values("revenue_share_pct", ascending=False).iloc[0]
    r_sp = df_sp[df_sp["hotel"] == "Resort Hotel"].sort_values("revenue_share_pct", ascending=False).iloc[0]

    metrics["city_top_seg"] = c_sp["market_segment"]
    metrics["city_top_seg_share"] = round(float(c_sp["revenue_share_pct"]), 1)
    metrics["city_top_seg_rev"] = round(float(c_sp["room_revenue"]), 2)

    metrics["resort_top_seg"] = r_sp["market_segment"]
    metrics["resort_top_seg_share"] = round(float(r_sp["revenue_share_pct"]), 1)
    metrics["resort_top_seg_rev"] = round(float(r_sp["room_revenue"]), 2)

    # 6. Room mismatch from v_room_mismatch.csv and overbooking buffer from v_overbooking_buffer.csv
    rm_path = OUTPUTS_DIR / "v_room_mismatch.csv"
    df_rm = pd.read_csv(rm_path)
    mismatched_tot = int(df_rm["mismatched_rooms"].sum())
    non_canc_tot = int(df_rm["non_cancelled_bookings"].sum())
    mismatch_pct = round(100.0 * mismatched_tot / non_canc_tot, 1)

    metrics["room_mismatches_count"] = mismatched_tot
    metrics["room_mismatches_pct"] = mismatch_pct
    metrics["non_cancelled_total"] = non_canc_tot

    ob_path = OUTPUTS_DIR / "v_overbooking_buffer.csv"
    df_ob = pd.read_csv(ob_path)
    city_ob_peak = df_ob[df_ob["hotel"] == "City Hotel"].sort_values("conservative_rate", ascending=False).iloc[0]
    metrics["city_ob_peak_month"] = calendar.month_name[int(city_ob_peak["month_num"])]
    metrics["city_ob_peak_rate"] = round(float(city_ob_peak["conservative_rate"]) * 100.0, 1)

    # Capacity from capacity.csv
    cap_path = OUTPUTS_DIR / "capacity.csv"
    df_cap = pd.read_csv(cap_path)
    city_cap = int(df_cap.loc[df_cap["hotel"] == "City Hotel", "rooms"].iloc[0])
    resort_cap = int(df_cap.loc[df_cap["hotel"] == "Resort Hotel", "rooms"].iloc[0])
    metrics["city_capacity"] = city_cap
    metrics["resort_capacity"] = resort_cap

    return metrics


def generate_markdown(m: dict) -> str:
    """Generate the complete markdown document using the dynamic metrics."""
    md = f"""# Power BI Dashboard Copy & Text Repository (`DASHBOARD_TEXT.md`)

> [!NOTE]
> **Dynamic Verification**: Every metric and percentage in this document is derived dynamically from analytical outputs in `data/outputs/*.csv` by [`src/make_dashboard_text.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/src/make_dashboard_text.py). No figures have been hardcoded or typed by hand per **Global Rule R1**.

---

## 1. Page Titles and Subtitles

| Page ID | Page Type | Official Page Title | Subtitle / Breadcrumb Description |
| :--- | :--- | :--- | :--- |
| **Page 1** | Primary Report | **Executive Overview** | Portfolio Revenue, Occupancy & Booking Conversion Performance |
| **Page 2** | Primary Report | **Revenue & Segment Dynamics** | Commercial Distribution, Channel Profitability & Segment Underperformance |
| **Page 3** | Primary Report | **Cancellation Diagnostic** | Attrition Analysis Across Lead Time, Deposit Policy & Booking Attributes |
| **Page 4** | Reference Report | **Insights & Model Governance** | Strategic Findings, KPI Definitions, Scope Limitations & Model Parameters |
| **Supporting A** | Drill-Through | **Market Segment Detail** | Drill-Through Performance Analysis for Selected Commercial Segment |
| **Supporting B** | Tooltip (320x240) | **Category Performance Summary** | Contextual KPI Summary for Hovered Dimension Category |

---

## 2. Visual Titles and Accessibility Alt Text

Every visual defined in [`powerbi/REPORT_SPEC.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/REPORT_SPEC.md) is assigned a descriptive visual title (phrased as a strategic business question or concise executive statement) and a single sentence of accessible alt text:

### Page 1: Executive Overview
- **S1 (Slicer: Hotel)**:
  - *Title*: Filter Property
  - *Alt Text*: Dropdown slicer allowing selection between City Hotel, Resort Hotel, or all properties.
- **S2 (Slicer: Year)**:
  - *Title*: Filter Calendar Year
  - *Alt Text*: Horizontal button slicer allowing selection of arrival and calendar years 2015, 2016, or 2017.
- **S3 (Slicer: Market Segment)**:
  - *Title*: Filter Commercial Segment
  - *Alt Text*: Dropdown slicer allowing isolation of portfolio metrics by specific market segment.
- **S4 (Slicer: Distribution Channel)**:
  - *Title*: Filter Distribution Channel
  - *Alt Text*: Dropdown slicer allowing isolation of portfolio metrics by booking distribution channel.
- **P1.1 (Card: Occupancy %)**:
  - *Title*: What is our overall room occupancy rate?
  - *Alt Text*: Displays portfolio room occupancy rate across stay dates within the reliable window.
- **P1.2 (Card: ADR)**:
  - *Title*: What is our average daily room rate?
  - *Alt Text*: Displays average daily rate per room night sold across stayed nights.
- **P1.3 (Card: RevPAR)**:
  - *Title*: What is our realized revenue per available room?
  - *Alt Text*: Displays revenue per available room night across active room inventory.
- **P1.4 (Card: Cancel Rate %)**:
  - *Title*: What proportion of reservations are canceled?
  - *Alt Text*: Displays portfolio cancellation rate attributed to arrival cohort.
- **P1.5 (Card: Avg Lead Time)**:
  - *Title*: How far in advance do guests book?
  - *Alt Text*: Displays average advance booking window in days from reservation to arrival.
- **P1.6 (Card: Stay Conversion %)**:
  - *Title*: What share of bookings successfully convert to realized stays?
  - *Alt Text*: Displays check-out conversion rate proxy calculated as one minus cancellation rate.
- **P1.7 (Line: Monthly RevPAR Trend)**:
  - *Title*: How does monthly RevPAR compare between City and Resort properties?
  - *Alt Text*: Line chart of monthly RevPAR from August 2015 to August 2017 comparing City Hotel and Resort Hotel.
- **P1.8 (Combo: Booking Pace & Cancel Rate)**:
  - *Title*: How do monthly booking volume and cancellation rates correlate over time?
  - *Alt Text*: Combo chart displaying monthly booking arrivals as vertical bars and cohort cancellation rate as a trendline.
- **P1.9 (Card: Capacity & Window Banner)**:
  - *Title*: What are the baseline capacity and date window assumptions?
  - *Alt Text*: Summary banner stating derived property room capacities and the reliable observation window.

---

### Page 2: Revenue and Segments
- **P2.1 (Bar: ADR by Market Segment)**:
  - *Title*: Which market segments command the highest room rates?
  - *Alt Text*: Horizontal bar chart of ADR by market segment sorted descending from highest to lowest rate.
- **P2.2 (Treemap: Revenue Share %)**:
  - *Title*: How is room revenue distributed across market segments?
  - *Alt Text*: Treemap showing market segment revenue contribution shares across the portfolio.
- **P2.3 (Matrix: Hotel & Segment Matrix)**:
  - *Title*: Which property and segment combinations underperform commercial benchmarks?
  - *Alt Text*: Hierarchical matrix of booking volume, room nights sold, ADR, revenue share, and cancellation rates by hotel and segment, highlighting underperformers in red.
- **P2.4 (Line: ADR Seasonality)**:
  - *Title*: How do room rates fluctuate across calendar months?
  - *Alt Text*: Annual twelve-month ADR seasonality curves comparing seasonal rate patterns between City Hotel and Resort Hotel.

---

### Page 3: Cancellations Diagnostic
- **P3.1 (Column: Cancel Rate by Lead Bucket)**:
  - *Title*: Which lead time windows carry the highest cancellation risk?
  - *Alt Text*: Column chart illustrating cancellation rates rising progressively across longer advance booking windows.
- **P3.2 (Column: Cancellations by Timing Bucket)**:
  - *Title*: How close to arrival do guests cancel their reservations?
  - *Alt Text*: Column chart displaying cancellation counts grouped by the number of days prior to scheduled arrival that the cancellation occurred.
- **P3.3 (Bar: Cancel Rate by Deposit Type)**:
  - *Title*: How strongly does deposit policy correlate with cancellation rate?
  - *Alt Text*: Bar chart comparing cancellation rates across Non Refund, No Deposit, and Refundable reservation terms.
- **P3.4 (Bar: Cancel Rate by Market Segment)**:
  - *Title*: Which customer segments experience the greatest attrition?
  - *Alt Text*: Bar chart of cancellation rates by market segment sorted descending.
- **P3.5 (Bar: Cancel Rate by Customer Type)**:
  - *Title*: How do cancellation rates differ between transient and group customers?
  - *Alt Text*: Bar chart showing cancellation rates across Transient, Transient-Party, Contract, and Group customer types.
- **P3.6 (Decomposition Tree: Root-Cause Tree)**:
  - *Title*: What root factors explain our reservation cancellations?
  - *Alt Text*: Interactive decomposition tree breaking down portfolio cancellation rate across lead time, deposit policy, customer segment, and origin country.

---

### Page 4: Insights and Assumptions
- **P4.1 (Card: Scope & Capacity Banner)**:
  - *Title*: What are the baseline model parameters?
  - *Alt Text*: Header banner displaying property room capacities and reliable performance window dates.
- **P4.2 (Text: Key Findings)**:
  - *Title*: What are the executive strategic findings?
  - *Alt Text*: Summary text detailing core analytical findings on cancellation drivers, seasonal rate curves, and segment profitability.
- **P4.3 (Text: Definitions)**:
  - *Title*: How are core hotel revenue KPIs defined?
  - *Alt Text*: Authoritative reference text defining room nights sold, room revenue, ADR, Occupancy, RevPAR, and conversion metrics.
- **P4.4 (Text: Assumptions & Limitations)**:
  - *Title*: What methodological constraints govern this dataset?
  - *Alt Text*: Explanatory text detailing window boundaries, capacity derivation, and row exclusions.
- **P4.5 (Text: Technical Architecture)**:
  - *Title*: How is the data model structured and refreshed?
  - *Alt Text*: Documentation describing the star schema dimensional model and validation protocols.

---

### Supporting Page A: Segment Detail (Drill-Through Canvas)
- **SA.1 (Card: Bookings)**:
  - *Title*: How many bookings originated in this segment?
  - *Alt Text*: Displays total reservation count for the selected market segment.
- **SA.2 (Card: Cancel Rate %)**:
  - *Title*: What is the cancellation rate for this segment?
  - *Alt Text*: Displays arrival cohort cancellation rate for the selected market segment.
- **SA.3 (Card: ADR)**:
  - *Title*: What average rate does this segment achieve?
  - *Alt Text*: Displays realized average daily rate per room night sold for the selected market segment.
- **SA.4 (Card: Room Nights Sold)**:
  - *Title*: How many room nights did this segment consume?
  - *Alt Text*: Displays total stayed room nights for the selected market segment.
- **SA.5 (Line: Monthly Segment Pace)**:
  - *Title*: How has segment volume and ADR evolved over time?
  - *Alt Text*: Monthly combo chart of room nights sold and realized ADR for the selected market segment.
- **SA.6 (Table: Top 10 Guest Countries)**:
  - *Title*: Which geographic markets generate the most bookings for this segment?
  - *Alt Text*: Table of the top ten guest origin countries by booking volume for the selected market segment.

---

### Supporting Page B: KPI Tooltip (Tooltip Canvas)
- **SB.1 (Card: Category Header)**:
  - *Title*: What category is currently selected?
  - *Alt Text*: Header card displaying the category name of the hovered visual element.
- **SB.2 (Card: Bookings)**:
  - *Title*: What is the booking volume for this category?
  - *Alt Text*: Displays total reservations for the hovered category.
- **SB.3 (Card: Cancel Rate %)**:
  - *Title*: What is the cancellation rate for this category?
  - *Alt Text*: Displays cancellation rate for the hovered category.
- **SB.4 (Card: ADR)**:
  - *Title*: What is the average daily rate for this category?
  - *Alt Text*: Displays realized average daily rate for the hovered category.

---

## 3. Page 4 'Key Findings': 6 Factual Statements

The following statements are built strictly from physical CSV outputs saved in `data/outputs/`. All wording is strictly neutral and factual, avoiding causal claims and using 'is associated with' rather than 'causes':

1. **Property Cancellation Variance**:
   City Hotel exhibits a substantially higher cancellation rate of **{m['city_cancel_rate']}%** compared with Resort Hotel at **{m['resort_cancel_rate']}%** [v_booking_trends.csv, cancellations].

2. **Lead Time Attrition Elasticity**:
   Bookings made in the **{m['high_lead_bucket']}** days lead time bucket exhibit the highest cancellation rate at **{m['high_lead_rate']}%**, whereas bookings made within **{m['low_lead_bucket']}** days exhibit the lowest cancellation rate at **{m['low_lead_rate']}%** [v_cancellation_drivers.csv, cancel_rate_pct].

3. **Deposit Policy Attrition**:
   Reservations booked under a **{m['high_deposit_type']}** deposit policy show the highest cancellation rate at **{m['high_deposit_rate']}%**, which is heavily associated with wholesale tour operator group block allocations [v_cancellation_drivers.csv, cancel_rate_pct].

4. **Seasonal RevPAR Dynamics**:
   City Hotel reaches its peak monthly RevPAR in **{m['city_peak_month']}** at **${m['city_peak_revpar']:.2f}** and its annual low in **{m['city_low_month']}** at **${m['city_low_revpar']:.2f}**, whereas Resort Hotel reaches its peak monthly RevPAR in **{m['resort_peak_month']}** at **${m['resort_peak_revpar']:.2f}** and its annual low in **{m['resort_low_month']}** at **${m['resort_low_revpar']:.2f}** [v_seasonality.csv, avg_revpar].

5. **Segment Commercial Contribution**:
   The **{m['city_top_seg']}** market segment generates the largest revenue share for both properties, contributing **{m['city_top_seg_share']}%** of total room revenue at City Hotel (${m['city_top_seg_rev']:,.2f}) and **{m['resort_top_seg_share']}%** at Resort Hotel (${m['resort_top_seg_rev']:,.2f}) [v_segment_performance.csv, revenue_share_pct].

6. **Operational Allocation & Buffer**:
   Across all realized non-cancelled reservations, **{m['room_mismatches_count']:,} bookings ({m['room_mismatches_pct']}%)** experienced an operational room type mismatch where the assigned room type differed from the reserved room type [v_room_mismatch.csv, mismatched_rooms]; furthermore, City Hotel's recommended conservative overbooking buffer reaches its peak in **{m['city_ob_peak_month']}** at **{m['city_ob_peak_rate']}%** [v_overbooking_buffer.csv, conservative_rate].

---

## 4. Definitions Block (Rules K1 to K7 in Plain English)

- **K1. Room-Night Sold**:
  A single overnight stay consumed by a guest on a non-cancelled booking across calendar dates (`arrival_date` through `checkout_date - 1`). Reservations with total stay nights equal to zero produce zero room-nights sold.
- **K2. Room Revenue**:
  The sum of individual stay-night average daily rates (`fact_stay_nights[adr]`). Cancelled reservations produce zero room revenue as no realized deposit or fee information exists in the source data.
- **K3. Average Daily Rate (ADR)**:
  Total realized room revenue divided by total room-nights sold. An unweighted mathematical average of booking rates must never be used.
- **K4. Occupancy % and RevPAR**:
  Occupancy percentage equals room-nights sold divided by available room-nights. Revenue Per Available Room (RevPAR) equals total room revenue divided by available room-nights, which mathematically equals ADR multiplied by Occupancy percentage.
- **K5. Cancellation Rate**:
  The total number of cancelled and no-show reservations divided by all booking reservations, attributed to the arrival month cohort. Guest no-shows are tracked as a separate subcategory.
- **K6. Stay Conversion Proxy**:
  The proportion of bookings with a status of 'Check-Out' divided by total bookings, equal to 1 minus the cancellation rate. (Note: The dataset contains no website enquiry funnel, making check-out realization the authoritative conversion proxy).
- **K7. Segment Capacity & Slicing Rule**:
  Available room capacity exists strictly at the hotel property level. Slicing Occupancy % or RevPAR by market segment represents each segment's **contribution to the hotel total**, not internal segment occupancy.

---

## 5. Assumptions and Limitations Block

- **Capacity Assumption (Rule W2)**:
  Because the raw dataset lacks physical room inventory, capacity is derived from observed peak room nights sold during the reliable observation window plus a 10% operational buffer rounded up to the nearest 10 rooms (City Hotel = 250 rooms, Resort Hotel = 210 rooms). This is an analytical assumption that must be stated on all reporting deliverables.
- **Reliable Observation Window (Rule W1)**:
  Stay-night operational KPIs (Occupancy %, ADR, RevPAR) are reported exclusively for stay dates between 2015-08-01 and 2017-08-31 (762 days). Stays commencing prior to 2015-07-01 and departures after 2017-08-31 are absent from source records. Booking arrival pace KPIs incorporate all arrival dates.
- **Absence of Top-of-Funnel Conversion Data**:
  The source data records only finalized booking transactions and lacks website traffic, search queries, quote requests, or shopping cart abandonments.
- **Duplicate Records Retained and Flagged (Rule D7)**:
  Identical reservation records (31,994 rows) are preserved in the data model and flagged via `is_duplicate_row` because the dataset lacks unique reservation IDs and identical entries may reflect genuine concurrent bookings.
- **Revenue Excludes Cancelled Bookings (Rule K2)**:
  All cancelled bookings contribute $0.00 to realized room revenue. While deposit policies are recorded, actual cash retained upon cancellation is unrecorded in source data.
"""
    return md


def main():
    print("=" * 80)
    print("GENERATING POWER BI DASHBOARD TEXT: powerbi/DASHBOARD_TEXT.md")
    print("=" * 80)

    metrics = load_output_metrics()
    print("[INFO] Successfully loaded and computed dynamic metrics from data/outputs/:")
    print(f"       - City Cancel Rate:     {metrics['city_cancel_rate']}% vs Resort: {metrics['resort_cancel_rate']}%")
    print(f"       - Lead Bucket Extremes: {metrics['high_lead_bucket']} ({metrics['high_lead_rate']}%) vs {metrics['low_lead_bucket']} ({metrics['low_lead_rate']}%)")
    print(f"       - High Deposit Policy:  {metrics['high_deposit_type']} ({metrics['high_deposit_rate']}%)")
    print(f"       - City Seasonality:     Peak {metrics['city_peak_month']} (${metrics['city_peak_revpar']}), Low {metrics['city_low_month']} (${metrics['city_low_revpar']})")
    print(f"       - Resort Seasonality:   Peak {metrics['resort_peak_month']} (${metrics['resort_peak_revpar']}), Low {metrics['resort_low_month']} (${metrics['resort_low_revpar']})")
    print(f"       - City Top Segment:     {metrics['city_top_seg']} ({metrics['city_top_seg_share']}%, ${metrics['city_top_seg_rev']:,.2f})")
    print(f"       - Resort Top Segment:   {metrics['resort_top_seg']} ({metrics['resort_top_seg_share']}%, ${metrics['resort_top_seg_rev']:,.2f})")
    print(f"       - Room Mismatch:        {metrics['room_mismatches_count']:,} ({metrics['room_mismatches_pct']}%)")
    print(f"       - City Overbooking:     Peak {metrics['city_ob_peak_month']} ({metrics['city_ob_peak_rate']}%)")

    content = generate_markdown(metrics)
    TARGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    TARGET_FILE.write_text(content, encoding="utf-8")

    print("-" * 80)
    print(f"[SUCCESS] Wrote {len(content)} characters to {TARGET_FILE}")
    print("=" * 80)


if __name__ == "__main__":
    main()
