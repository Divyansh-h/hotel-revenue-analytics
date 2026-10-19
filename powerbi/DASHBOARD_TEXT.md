# Power BI Dashboard Copy & Text Repository (`DASHBOARD_TEXT.md`)

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
   City Hotel exhibits a substantially higher cancellation rate of **41.7%** compared with Resort Hotel at **27.8%** [v_booking_trends.csv, cancellations].

2. **Lead Time Attrition Elasticity**:
   Bookings made in the **181+** days lead time bucket exhibit the highest cancellation rate at **57.0%**, whereas bookings made within **0-7** days exhibit the lowest cancellation rate at **9.6%** [v_cancellation_drivers.csv, cancel_rate_pct].

3. **Deposit Policy Attrition**:
   Reservations booked under a **Non Refund** deposit policy show the highest cancellation rate at **99.4%**, which is heavily associated with wholesale tour operator group block allocations [v_cancellation_drivers.csv, cancel_rate_pct].

4. **Seasonal RevPAR Dynamics**:
   City Hotel reaches its peak monthly RevPAR in **July** at **$102.61** and its annual low in **January** at **$36.27**, whereas Resort Hotel reaches its peak monthly RevPAR in **August** at **$152.24** and its annual low in **January** at **$22.67** [v_seasonality.csv, avg_revpar].

5. **Segment Commercial Contribution**:
   The **Online TA** market segment generates the largest revenue share for both properties, contributing **61.1%** of total room revenue at City Hotel ($8,732,303.32) and **42.8%** at Resort Hotel ($4,662,825.19) [v_segment_performance.csv, revenue_share_pct].

6. **Operational Allocation & Buffer**:
   Across all realized non-cancelled reservations, **14,114 bookings (18.8%)** experienced an operational room type mismatch where the assigned room type differed from the reserved room type [v_room_mismatch.csv, mismatched_rooms]; furthermore, City Hotel's recommended conservative overbooking buffer reaches its peak in **April** at **27.1%** [v_overbooking_buffer.csv, conservative_rate].

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
