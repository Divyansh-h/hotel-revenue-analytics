# Power BI Dashboard Validation Checklist

This checklist is used to verify the Power BI report (`hotel_revenue_analytics.pbix`) against the benchmark values calculated directly from the star schema CSV model in [`powerbi/validation_expected.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/validation_expected.csv).

---

## 1. Validation Rules & Tolerances

- **Percentage Measures** (`Cancel Rate %`, `Occupancy %`, `Revenue Share %`, `Stay Conversion %`): Must match within **0.1 percentage points** (e.g., $37.0\% \pm 0.1\%$).
- **Currency Measures** (`Room Revenue`, `ADR`, `RevPAR`): Must match within **$0.01** (e.g., $\$101.45 \pm 0.01$).
- **Integer Counts** (`Bookings`, `Room Nights Sold`): Must match **exactly** ($\text{tolerance} = 0$).
- **Averages** (`Avg Lead Time`): Must match within **0.1 days**.

### Date & Capacity Semantics
1. **Year Slicer**: Filters `fact_bookings` by `arrival_date` year, and filters `fact_stay_nights` and `fact_capacity` by `stay_date` / `date_key` year, strictly within the reliable performance window (`2015-08-01` to `2017-08-31`).
2. **Segment & Channel Slicers (Rule K7)**: Capacity is property-level and does not segment by guest profile. When slicing by Market Segment or Distribution Channel, `Room Nights Available` remains the property capacity for that date/hotel scope; `Occupancy %` and `RevPAR` reflect that segment's contribution to property inventory.
3. **Revenue Share %**: Evaluates the selected segment/channel revenue divided by the benchmark revenue across all profiles in the current hotel/year scope (`ALLSELECTED(dim_profile)`).

---

## 2. Slicer Setup Guide

All visuals use the synchronized top slicer strip located at coordinates `y: 80 to 130` on Pages 1–3:
- **Hotel**: Dropdown slicer mapped to `dim_hotel[hotel]`. Options: `All`, `City Hotel`, `Resort Hotel`.
- **Year**: Tile/Button slicer mapped to `dim_date[year]`. Options: `All`, `2015`, `2016`, `2017`.
- **Market Segment**: Dropdown slicer mapped to `dim_profile[market_segment]`. Options: `All`, `Online TA`, `Offline TA/TO`, `Groups`, `Direct`, `Corporate`, `Complementary`, `Aviation`.
- **Distribution Channel**: Dropdown slicer mapped to `dim_profile[distribution_channel]`. Options: `All`, `TA/TO`, `Direct`, `Corporate`, `GDS`.

> **Resetting Filters**: Before beginning each scenario, click the **Clear all slicers** button in the top right or manually select **(Select All)** on each dropdown and uncheck the active Year tile.

---

## 3. Validation Checklist Table

Fill in the **Dashboard Value** and mark **Match (Y/N)** for each of the 6 scenarios and 10 core measures:

| Scenario | Measure | Expected Value | Dashboard Value | Match (Y/N) | Notes / Tolerances |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **S1: No Filters** | Bookings | 119,388 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S1: No Filters | Cancel Rate % | 37.0% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| S1: No Filters | Avg Lead Time | 104.0 days | | [ ] Y / [ ] N | Tol: $\pm 0.1$ days |
| S1: No Filters | Room Nights Sold | 248,261 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S1: No Filters | Room Revenue | $25,187,186.16 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S1: No Filters | ADR | $101.45 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S1: No Filters | Occupancy % | 70.8% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| S1: No Filters | RevPAR | $71.86 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S1: No Filters | Revenue Share % | 100.0% | | [ ] Y / [ ] N | Baseline portfolio share |
| S1: No Filters | Stay Conversion % | 63.0% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ ($1 - \text{Cancel Rate}$) |
| | | | | | |
| **S2: City Hotel** | Bookings | 79,329 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S2: City Hotel | Cancel Rate % | 41.7% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| S2: City Hotel | Avg Lead Time | 109.7 days | | [ ] Y / [ ] N | Tol: $\pm 0.1$ days |
| S2: City Hotel | Room Nights Sold | 133,860 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S2: City Hotel | Room Revenue | $14,285,466.42 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S2: City Hotel | ADR | $106.72 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S2: City Hotel | Occupancy % | 70.3% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| S2: City Hotel | RevPAR | $74.99 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S2: City Hotel | Revenue Share % | 100.0% | | [ ] Y / [ ] N | Baseline property share |
| S2: City Hotel | Stay Conversion % | 58.3% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| | | | | | |
| **S3: Resort Hotel, 2016** | Bookings | 18,567 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S3: Resort Hotel, 2016 | Cancel Rate % | 26.6% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| S3: Resort Hotel, 2016 | Avg Lead Time | 92.1 days | | [ ] Y / [ ] N | Tol: $\pm 0.1$ days |
| S3: Resort Hotel, 2016 | Room Nights Sold | 54,037 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S3: Resort Hotel, 2016 | Room Revenue | $4,822,927.67 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S3: Resort Hotel, 2016 | ADR | $89.25 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S3: Resort Hotel, 2016 | Occupancy % | 70.3% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| S3: Resort Hotel, 2016 | RevPAR | $62.75 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S3: Resort Hotel, 2016 | Revenue Share % | 100.0% | | [ ] Y / [ ] N | Baseline hotel-year share |
| S3: Resort Hotel, 2016 | Stay Conversion % | 73.4% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| | | | | | |
| **S4: Online TA** | Bookings | 56,477 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S4: Online TA | Cancel Rate % | 36.7% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| S4: Online TA | Avg Lead Time | 83.0 days | | [ ] Y / [ ] N | Tol: $\pm 0.1$ days |
| S4: Online TA | Room Nights Sold | 116,701 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S4: Online TA | Room Revenue | $13,395,128.51 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S4: Online TA | ADR | $114.78 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S4: Online TA | Occupancy % | 33.3% | | [ ] Y / [ ] N | Segment contribution to capacity |
| S4: Online TA | RevPAR | $38.22 | | [ ] Y / [ ] N | Segment contribution to RevPAR |
| S4: Online TA | Revenue Share % | 53.2% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| S4: Online TA | Stay Conversion % | 63.3% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| | | | | | |
| **S5: Direct Channel, 2017** | Bookings | 5,060 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S5: Direct Channel, 2017 | Cancel Rate % | 17.6% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| S5: Direct Channel, 2017 | Avg Lead Time | 63.3 days | | [ ] Y / [ ] N | Tol: $\pm 0.1$ days |
| S5: Direct Channel, 2017 | Room Nights Sold | 12,818 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S5: Direct Channel, 2017 | Room Revenue | $1,665,009.93 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S5: Direct Channel, 2017 | ADR | $129.90 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S5: Direct Channel, 2017 | Occupancy % | 11.5% | | [ ] Y / [ ] N | Channel contribution to capacity |
| S5: Direct Channel, 2017 | RevPAR | $14.90 | | [ ] Y / [ ] N | Channel contribution to RevPAR |
| S5: Direct Channel, 2017 | Revenue Share % | 17.1% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ of 2017 revenue |
| S5: Direct Channel, 2017 | Stay Conversion % | 82.4% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |
| | | | | | |
| **S6: City, Groups, 2016** | Bookings | 4,687 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S6: City, Groups, 2016 | Cancel Rate % | 74.7% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ (Underperformer) |
| S6: City, Groups, 2016 | Avg Lead Time | 240.8 days | | [ ] Y / [ ] N | Tol: $\pm 0.1$ days |
| S6: City, Groups, 2016 | Room Nights Sold | 3,007 | | [ ] Y / [ ] N | Exact match (tol: 0) |
| S6: City, Groups, 2016 | Room Revenue | $251,936.50 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S6: City, Groups, 2016 | ADR | $83.78 | | [ ] Y / [ ] N | Tol: $\pm \$0.01$ |
| S6: City, Groups, 2016 | Occupancy % | 3.3% | | [ ] Y / [ ] N | Segment contribution to capacity |
| S6: City, Groups, 2016 | RevPAR | $2.75 | | [ ] Y / [ ] N | Segment contribution to RevPAR |
| S6: City, Groups, 2016 | Revenue Share % | 3.7% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ of City 2016 rev |
| S6: City, Groups, 2016 | Stay Conversion % | 25.3% | | [ ] Y / [ ] N | Tol: $\pm 0.1\%$ |

---

## 4. Scenario Breakdown & Instructions

### Scenario S1: Portfolio Baseline (No Filters)
- **Slicers**:
  - `Hotel`: `(All)`
  - `Year`: `(All)`
  - `Market Segment`: `(All)`
  - `Distribution Channel`: `(All)`
- **Verification Location**: Page 1 (Executive Overview) KPI Cards and Page 2 (Revenue Performance).
- **Core Insights to Confirm**:
  - Total Bookings = `119,388`, Cancel Rate = `37.0%`, Stay Conversion = `63.0%`.
  - Room Nights Sold = `248,261`, Room Revenue = `$25,187,186.16`, ADR = `$101.45`.
  - Occupancy % = `70.8%`, RevPAR = `$71.86`.

### Scenario S2: City Hotel Baseline
- **Slicers**:
  - `Hotel`: Select `City Hotel`
  - `Year`: `(All)`
  - `Market Segment`: `(All)`
  - `Distribution Channel`: `(All)`
- **Core Insights to Confirm**:
  - City Hotel cancellation rate is significantly higher at `41.7%` (vs Resort `27.8%`).
  - City Hotel ADR is `$106.72` and RevPAR is `$74.99` across 133,860 room-nights sold.
  - Occupancy % is `70.3%` based on City Hotel's 250 available rooms.

### Scenario S3: Resort Hotel in 2016
- **Slicers**:
  - `Hotel`: Select `Resort Hotel`
  - `Year`: Select `2016`
  - `Market Segment`: `(All)`
  - `Distribution Channel`: `(All)`
- **Core Insights to Confirm**:
  - Room Nights Sold = `54,037`, Room Revenue = `$4,822,927.67`.
  - ADR = `$89.25`, RevPAR = `$62.75`, Occupancy % = `70.3%`.
  - Cancellation rate is low at `26.6%` (Stay Conversion = `73.4%`).

### Scenario S4: Online Travel Agent (TA) Across Both Hotels
- **Slicers**:
  - `Hotel`: `(All)`
  - `Year`: `(All)`
  - `Market Segment`: Select `Online TA`
  - `Distribution Channel`: `(All)`
- **Core Insights to Confirm**:
  - Online TA generates `$13,395,128.51` in revenue, representing **53.2%** of total portfolio revenue.
  - Online TA has a healthy ADR of `$114.78` and lead time of `83.0` days.
  - Occupancy contribution is `33.3%` of property capacity (116,701 nights / 350,520 capacity).

### Scenario S5: Direct Channel in 2017
- **Slicers**:
  - `Hotel`: `(All)`
  - `Year`: Select `2017`
  - `Market Segment`: `(All)`
  - `Distribution Channel`: Select `Direct`
- **Core Insights to Confirm**:
  - Direct channel yields a premium ADR of `$129.90` and a remarkably low cancellation rate of `17.6%` (Stay Conversion = `82.4%`).
  - Represents `17.1%` of all 2017 revenue ($1,665,009.93).
  - Short booking lead time of `63.3` days.

### Scenario S6: Groups Segment at City Hotel in 2016
- **Slicers**:
  - `Hotel`: Select `City Hotel`
  - `Year`: Select `2016`
  - `Market Segment`: Select `Groups`
  - `Distribution Channel`: `(All)`
- **Core Insights to Confirm**:
  - Severe underperformance: Cancellation rate spikes to **74.7%** (Stay Conversion = `25.3%`).
  - Very long lead time of `240.8` days.
  - Sub-benchmark ADR of `$83.78` (vs City Hotel 2016 benchmark of `$104.23`).
  - `Underperformer Flag` evaluates to `1`.

---

## 5. Sign-off Criteria

- [ ] All 60 checklist cells verified against Power BI Desktop cards and visuals.
- [ ] No visual errors, broken relationship warnings, or blank cards observed.
- [ ] Cross-filtering between Page 1, Page 2, and Page 3 synchronizes correctly.
- [ ] Theme colors render properly: City Hotel (`#1A5276` Navy), Resort Hotel (`#D98880` Terracotta).
- [ ] Sign-off signature and date recorded in `docs/phase4_signoff.md`.
