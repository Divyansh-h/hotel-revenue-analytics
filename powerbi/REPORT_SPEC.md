# Power BI Report & Visual Specification (`REPORT_SPEC.md`)

> [!IMPORTANT]
> **Specification Governance**:
> - **Canvas Resolution**: 16:9 Standard Widescreen (1280 x 720 pixels).
> - **Field & Measure Integrity**: Uses exclusively columns defined in [`powerbi/MODEL_SPEC.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/MODEL_SPEC.md) and explicit DAX measures defined in [`powerbi/measures.dax`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/measures.dax). No implicit measures are permitted.
> - **Rule K7 Compliance**: Any visual displaying `[Occupancy %]` or `[RevPAR]` sliced by `dim_profile` attributes must be explicitly labeled as **"Contribution to Hotel Total"**.

---

## 1. Global Report Standards & Layout Architecture

### 1.1 Color Palette & Visual Semantics (`hotel_theme.json`)

All visual styling adheres to the custom enterprise theme [`powerbi/theme/hotel_theme.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/theme/hotel_theme.json), which has been mathematically validated for WCAG 2.1 compliance via [`src/validate_powerbi_theme.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/src/validate_powerbi_theme.py).

#### The 8 Theme Data Colors (`dataColors`)
| Index | Color Hex | Color Swatch | Semantic Assignment | Contrast vs White | WCAG Status |
| :-: | :-: | :-: | :--- | :-: | :-: |
| **1** | `#1A365D` | Deep Navy | **City Hotel (Primary Series) / Table Accent** | **12.14:1** | PASS (>= 3.0:1) |
| **2** | `#C05621` | Terracotta Amber | **Resort Hotel (Secondary Series)** | **4.57:1** | PASS (>= 3.0:1) |
| **3** | `#0D7680` | Teal Slate | Tertiary Series (Transient, Direct) | **5.36:1** | PASS (>= 3.0:1) |
| **4** | `#6B21A8` | Deep Purple | Quaternary Series (Online TA) | **8.72:1** | PASS (>= 3.0:1) |
| **5** | `#334155` | Slate Steel | 5th Series (Offline TA/TO) | **10.35:1** | PASS (>= 3.0:1) |
| **6** | `#854D0E` | Bronze Olive | 6th Series (Corporate) | **6.85:1** | PASS (>= 3.0:1) |
| **7** | `#9F1239` | Rose Burgundy | 7th Series (Groups) | **8.02:1** | PASS (>= 3.0:1) |
| **8** | `#3730A3` | Deep Indigo | 8th Series (Complementary, Aviation) | **9.93:1** | PASS (>= 3.0:1) |

#### Strict Color Usage Rules
1. **Hotel Property Consistency Rule**:
   - **City Hotel** must **always** be displayed in `#1A365D` (Deep Navy) across every chart, line, bar, legend, and matrix accent.
   - **Resort Hotel** must **always** be displayed in `#C05621` (Terracotta Amber) across every chart, line, bar, legend, and matrix accent.
   - Never invert these assignments or allow default random color assignment across pages.
2. **Alert Red Reservation Rule**:
   - Crimson Red (`#C62828` / `#E53E3E`) is **reserved strictly for underperformer alerts**, elevated cancellation risk, and negative KPI flags.
   - **Never** use red as an arbitrary categorical slice in pie/donut charts, treemaps, or bar charts.
3. **KPI & Diverging Thresholds**:
   - **Good / High Performance**: `#2E7D32` (Forest Green).
   - **Neutral / Benchmark**: `#F9A825` (Amber Gold).
   - **Bad / Underperformer**: `#C62828` (Crimson Red).
4. **UI Shell & Neutral Elements**:
   - Visual container backgrounds: `#FFFFFF` (100% opaque, no drop shadow).
   - Card and container borders: `#E2E8F0` (subtle 1px border, 4px corner radius).
   - Primary typography: `#252423` (15.49:1 AAA contrast against `#FFFFFF`).
   - Secondary labels, captions, and tick marks: `#718096` (Slate Gray).


---

### 1.2 Global Grid & Layout Bands (Pages 1, 2, 3)

```
0px   +-------------------------------------------------------------------------------+
      | HEADER BAND: Report Title, Category Badge, Global Status (y: 0 to 70, h: 70)  |
70px  +-------------------------------------------------------------------------------+
80px  +-------------------------------------------------------------------------------+
      | SLICER STRIP: Hotel | Year | Market Segment | Distribution Channel (h: 50)    |
130px +-------------------------------------------------------------------------------+
140px +-------------------------------------------------------------------------------+
      |                                                                               |
      | MAIN CONTENT WORKSPACE: KPI Cards, Charts, Matrices, Trees (y: 140 to 710)    |
      |                                                                               |
710px +-------------------------------------------------------------------------------+
720px
      0px                                                                           1280px
```

#### Shared Slicer Strip (Pages 1, 2, 3 - Synced Slicers)
The slicer strip occupies `y: 80` to `y: 130` (`h: 50`) and is **synced across Pages 1 to 3**:

| # | Visual Name / Slicer | Visual Type | X | Y | W | H | Source Field | Control Type | Selection Rules | Synced Pages |
| :-: | :--- | :--- | :-: | :-: | :-: | :-: | :--- | :--- | :--- | :-: |
| **S1** | Slicer: Hotel | Slicer | 20 | 80 | 220 | 50 | `dim_hotel[hotel]` | Dropdown | Multi-select with "Select All" | Pages 1, 2, 3 |
| **S2** | Slicer: Year | Slicer | 260 | 80 | 320 | 50 | `dim_date[year]` | Tile / Buttons | Single select or multi (2015, 2016, 2017) | Pages 1, 2, 3 |
| **S3** | Slicer: Market Segment | Slicer | 600 | 80 | 320 | 50 | `dim_profile[market_segment]` | Dropdown | Multi-select with search | Pages 1, 2, 3 |
| **S4** | Slicer: Distribution Channel | Slicer | 940 | 80 | 320 | 50 | `dim_profile[distribution_channel]` | Dropdown | Multi-select with search | Pages 1, 2, 3 |

---

## 2. Page 1: Executive Overview

- **Target Audience**: Chief Commercial Officer, VP Revenue Management, General Managers.
- **Core Purpose**: High-level portfolio health check across stay-night operational efficiency and booking-pace conversion.

### Visual Inventory & Coordinates

```
y: 140  +---------+---------+---------+---------+---------+---------+
        | Card P1 | Card P2 | Card P3 | Card P4 | Card P5 | Card P6 | (h: 90)
y: 230  +---------+---------+---------+---------+---------+---------+
y: 240  +-----------------------------+-----------------------------+
        |                             |                             |
        | Visual P1.7: RevPAR Trend   | Visual P1.8: Booking &      | (h: 420)
        | Line Chart by Hotel         | Cancellation Combo Chart    |
        |                             |                             |
y: 660  +-----------------------------+-----------------------------+
y: 670  +-----------------------------------------------------------+
        | Visual P1.9: Capacity & Reliable Window Assumption Banner | (h: 40)
y: 710  +-----------------------------------------------------------+
```

#### Visual P1.1 to P1.6: Headline KPI Cards Row (`y: 140`, `h: 90`)
| ID | Title / Measure | X | Y | W | H | Display Measure | Subtitle (Basis) | Format | Alt Text |
| :-: | :--- | :-: | :-: | :-: | :-: | :--- | :--- | :-: | :--- |
| **P1.1** | Occupancy % | 20 | 140 | 195 | 90 | `[Occupancy %]` | Stay-night basis (Rule K4) | `0.0%` | Portfolio room occupancy rate across stay dates in the reliable window. |
| **P1.2** | ADR | 229 | 140 | 195 | 90 | `[ADR]` | Stay-night basis (Rule K3) | `#,##0.00` | Average Daily Rate per room night sold across stayed nights. |
| **P1.3** | RevPAR | 438 | 140 | 195 | 90 | `[RevPAR]` | Stay-night basis (Rule K4) | `#,##0.00` | Revenue per available room night across hotel room inventory. |
| **P1.4** | Cancel Rate % | 647 | 140 | 195 | 90 | `[Cancel Rate %]` | Booking arrival cohort (Rule K5) | `0.0%` | Share of total bookings canceled or marked as no-show by arrival cohort. |
| **P1.5** | Avg Lead Time | 856 | 140 | 195 | 90 | `[Avg Lead Time]` | Booking arrival cohort (Days) | `0.0` | Average booking lead time in days prior to arrival date. |
| **P1.6** | Stay Conversion % | 1065 | 140 | 195 | 90 | `[Stay Conversion %]` | Booking cohort (Proxy: 1 - Cancel) | `0.0%` | Realized check-out conversion rate proxy (1 minus cancel rate). |

#### Visual P1.7: Monthly RevPAR Trend by Hotel Property
- **Visual Type**: Line Chart
- **Placement**: `x: 20`, `y: 240`, `w: 610`, `h: 420`
- **Title**: Monthly RevPAR Performance by Property (Stay-Night Basis)
- **Fields**:
  - **X-Axis**: `dim_date[year_month]` (Continuous calendar sort)
  - **Legend**: `dim_hotel[hotel]` (Colors: City Hotel = `#1A365D`, Resort Hotel = `#D97706`)
  - **Y-Axis**: `[RevPAR]` (Format: `#,##0.00`, Title: "RevPAR ($)")
  - **Tooltips**: `[Occupancy %]`, `[ADR]`, `[Room Nights Sold]`, `[Room Revenue]`
- **Interactions**: Cross-highlights combo chart P1.8 and filters tooltip page B.
- **Alt Text**: Monthly RevPAR trend from August 2015 to August 2017 comparing City Hotel and Resort Hotel. Highlights seasonal summer peaks in the Algarve Resort and steady urban performance in Lisbon.

#### Visual P1.8: Booking Pace & Cancellation Rate Combo Chart
- **Visual Type**: Line and Clustered Column Chart
- **Placement**: `x: 650`, `y: 240`, `w: 610`, `h: 420`
- **Title**: Booking Volume and Cancellation Rate Pace by Arrival Month
- **Fields**:
  - **Shared X-Axis**: `dim_date[year_month]`
  - **Column Values (Y-Axis 1)**: `[Bookings]` (Fill: `#4A5568`, Format: `#,##0`, Title: "Bookings")
  - **Line Values (Y-Axis 2)**: `[Cancel Rate %]` (Stroke: `#E53E3E`, Stroke Width: 3px, Format: `0.0%`, Title: "Cancel Rate %")
  - **Tooltips**: `[Cancelled Bookings]`, `[No-Shows]`, `[Stay Conversion %]`
- **Interactions**: Cross-filters P1.7 upon month selection.
- **Alt Text**: Combo chart displaying total arrival bookings as dark gray vertical bars and cohort cancellation rate as a red trendline by arrival year-month.

#### Visual P1.9: Capacity & Reliable Window Assumption Banner
- **Visual Type**: Multi-row Card / Single-line Text Card
- **Placement**: `x: 20`, `y: 670`, `w: 1240`, `h: 40`
- **Title**: (Hidden / In-card header: "Model Assumptions & Scope")
- **Fields**: `[Capacity Text]`, `[Window Start]`, `[Window End]`
- **Display Template**: "Derived Capacity (Rule W2): City Hotel: 250 rooms | Resort Hotel: 210 rooms  •  Reliable Window (Rule W1): 2015-08-01 to 2017-08-31"
- **Alt Text**: Footnote banner stating derived room capacities and reliable observation window dates.

---

## 3. Page 2: Revenue and Segments

- **Target Audience**: Director of Revenue Management, Distribution Managers, Sales Directors.
- **Core Purpose**: Evaluate commercial channel profitability, rate premium, and volume contribution; identify underperforming market segments.

### Visual Inventory & Coordinates

```
y: 140  +-----------------------------+-----------------------------+
        | Visual P2.1: ADR by Segment | Visual P2.2: Revenue Share  | (h: 270)
        | Bar Chart (sorted desc)     | Treemap / Donut by Segment  |
y: 410  +-----------------------------+-----------------------------+
y: 420  +-----------------------------------------+-----------------+
        | Visual P2.3: Segment & Property Matrix  | Visual P2.4:    | (h: 285)
        | with Underperformer Flag Highlight      | ADR Seasonality |
y: 705  +-----------------------------------------+-----------------+
```

#### Visual P2.1: ADR by Market Segment
- **Visual Type**: Clustered Bar Chart (Horizontal)
- **Placement**: `x: 20`, `y: 140`, `w: 610`, `h: 270`
- **Title**: Average Daily Rate (ADR) by Market Segment ($)
- **Fields**:
  - **Y-Axis**: `dim_profile[market_segment]`
  - **X-Axis**: `[ADR]` (Format: `#,##0.00`)
  - **Tooltips**: `[Room Nights Sold]`, `[Room Revenue]`, `[Revenue Share %]`
- **Sort Order**: Sorted descending by `[ADR]`.
- **Interactions**: Filters matrix P2.3 and treemap P2.2. Enables **Drill-through** to Page A (Segment Detail).
- **Alt Text**: Horizontal bar chart of ADR by market segment sorted descending, showing Direct and Online TA commanding highest rates, with Corporate and Groups trailing.

#### Visual P2.2: Revenue Share % by Market Segment
- **Visual Type**: Treemap (or Donut Chart)
- **Placement**: `x: 650`, `y: 140`, `w: 610`, `h: 270`
- **Title**: Room Revenue Contribution Share by Market Segment (%)
- **Fields**:
  - **Category / Group**: `dim_profile[market_segment]`
  - **Values**: `[Revenue Share %]` (Format: `0.0%`)
  - **Tooltips**: `[Room Revenue]`, `[Room Nights Sold]`, `[Room Night Share %]`
- **Interactions**: Cross-highlights P2.1 and P2.3.
- **Alt Text**: Treemap showing market segment revenue share, highlighting Online TA as the dominant revenue driver (>55%).

#### Visual P2.3: Hotel & Market Segment Performance Matrix
- **Visual Type**: Matrix
- **Placement**: `x: 20`, `y: 420`, `w: 740`, `h: 285`
- **Title**: Commercial Performance Matrix (Hotel Property > Market Segment)
- **Fields**:
  - **Rows**: `dim_hotel[hotel]`, `dim_profile[market_segment]`
  - **Values**:
    1. `[Bookings]` (`#,##0`)
    2. `[Room Nights Sold]` (`#,##0`)
    3. `[ADR]` (`#,##0.00`)
    4. `[Revenue Share %]` (`0.0%`)
    5. `[Cancel Rate %]` (`0.0%`)
    6. `[Underperformer Flag]` (`0`, Hidden numeric / used for rule)
- **Conditional Formatting**:
  - **Background Color** applied to `[Cancel Rate %]` and `[ADR]`:
    - Rule: Based on field `[Underperformer Flag]`.
    - If value = 1 then background color = `#FED7D7` (Soft Light Red), font color = `#9B2C2C` (Dark Red).
- **Context Menu**: Right-click on any `market_segment` row -> **Drill-through > Segment Detail**.
- **Alt Text**: Hierarchical matrix breaking down volume, nights, rate, share, and cancellation rate by hotel and segment, highlighting underperforming segments in red.

#### Visual P2.4: ADR Seasonality by Calendar Month
- **Visual Type**: Line Chart
- **Placement**: `x: 780`, `y: 420`, `w: 480`, `h: 285`
- **Title**: ADR Seasonality Curve by Month (Jan to Dec)
- **Fields**:
  - **X-Axis**: `dim_date[month_short]` (Sorted by `month_num` ASC)
  - **Legend**: `dim_hotel[hotel]` (City Hotel = `#1A365D`, Resort Hotel = `#D97706`)
  - **Y-Axis**: `[ADR]` (Format: `#,##0.00`, Title: "ADR ($)")
  - **Tooltips**: `[Room Nights Sold]`, `[Room Revenue]`
- **Interactions**: Slices P2.3 upon month click.
- **Alt Text**: Annual 12-month seasonality curves of ADR showing steep summer surge for Resort Hotel and autumn peak for City Hotel.

---

## 4. Page 3: Cancellations Diagnostic

- **Target Audience**: Revenue Managers, Reservations Managers, Distribution Policy Officers.
- **Core Purpose**: Deep-dive into root drivers of reservation attrition across lead times, deposit structures, timing, and customer profiles.

### Visual Inventory & Coordinates

```
y: 140  +-------------------+--------------------+------------------------+
        | Visual P3.1:      | Visual P3.3:       |                        |
        | Cancel Rate by    | Deposit Type Bar   |                        |
        | Lead Bucket       +--------------------+ Visual P3.6:           | (h: 565)
        | (h: 270)          | Visual P3.4:       | Root Cause             |
        |                   | Segment Bar        | Decomposition Tree     |
y: 410  +-------------------+--------------------+ (Analyze: Cancel Rate %|
y: 420  +-------------------+ Visual P3.5:       | Explain: lead, deposit,|
        | Visual P3.2:      | Customer Type Bar  | segment, customer,     |
        | Cancellations by  |                    | country, hotel)        |
        | Timing Bucket     |                    |                        |
y: 705  +-------------------+--------------------+------------------------+
```

#### Visual P3.1: Cancel Rate % by Lead Time Bucket
- **Visual Type**: Clustered Column Chart
- **Placement**: `x: 20`, `y: 140`, `w: 390`, `h: 270`
- **Title**: Cancellation Rate % by Advance Lead Bucket
- **Fields**:
  - **X-Axis**: `fact_bookings[lead_bucket]` (Sorted by `lead_bucket_order`: '0-7', '8-30', '31-90', '91-180', '181+')
  - **Y-Axis**: `[Cancel Rate %]` (Format: `0.0%`, Title: "Cancel Rate %")
  - **Tooltips**: `[Bookings]`, `[Cancelled Bookings]`, `[Stay Conversion %]`
- **Alt Text**: Column chart showing cancellation rate escalating sharply from under 15% for lead times 0-7 days to over 55% for bookings made 181+ days in advance.

#### Visual P3.2: Cancelled Bookings by Cancellation Timing Bucket
- **Visual Type**: Clustered Column Chart
- **Placement**: `x: 20`, `y: 420`, `w: 390`, `h: 285`
- **Title**: Cancellation Volume by Days Prior to Arrival
- **Fields**:
  - **X-Axis**: `fact_bookings[cancel_timing_bucket]` (Sorted by `cancel_timing_order`: '0-3 days', '4-7 days', '8-14 days', '15-30 days', '31-60 days', '61-90 days', '91+ days')
  - **Y-Axis**: `[Cancelled Bookings]` (Format: `#,##0`, Title: "Cancelled Bookings")
  - **Tooltips**: `[Avg Days Cancelled Before Arrival]`
- **Alt Text**: Column chart showing cancellation distribution by advance notice window, highlighting high concentration of last-minute cancellations within 0-7 days.

#### Visual P3.3 to P3.5: Attribute Cancel Rate Bar Charts (Middle Column)
- **Placement**: `x: 430`, `w: 380`
1. **Visual P3.3: Cancel Rate % by Deposit Type** (`y: 140`, `h: 175`):
   - **Y-Axis**: `dim_profile[deposit_type]`, **X-Axis**: `[Cancel Rate %]` (`0.0%`).
   - Sorted descending by `[Cancel Rate %]`. Note: highlights the non-refundable deposit anomaly (>99% cancel rate on group allocations).
2. **Visual P3.4: Cancel Rate % by Market Segment** (`y: 325`, `h: 185`):
   - **Y-Axis**: `dim_profile[market_segment]`, **X-Axis**: `[Cancel Rate %]` (`0.0%`).
   - Sorted descending by `[Cancel Rate %]`.
3. **Visual P3.5: Cancel Rate % by Customer Type** (`y: 520`, `h: 185`):
   - **Y-Axis**: `dim_profile[customer_type]`, **X-Axis**: `[Cancel Rate %]` (`0.0%`).
   - Sorted descending by `[Cancel Rate %]`.

#### Visual P3.6: AI Root-Cause Decomposition Tree
- **Visual Type**: Decomposition Tree
- **Placement**: `x: 830`, `y: 140`, `w: 430`, `h: 565`
- **Title**: Interactive Cancellation Root-Cause Decomposition
- **Fields**:
  - **Analyze**: `[Cancel Rate %]`
  - **Explain By** (Hierarchical Exploration):
    1. `fact_bookings[lead_bucket]`
    2. `dim_profile[deposit_type]`
    3. `dim_profile[market_segment]`
    4. `dim_profile[customer_type]`
    5. `fact_bookings[country]`
    6. `dim_hotel[hotel]`
- **Interaction Setting**: **Turn off cross-filtering from the decomposition tree to other visuals**. The tree operates strictly as an exploratory diagnostic sandbox without disrupting the rest of Page 3.
- **Alt Text**: Interactive AI decomposition tree breaking down overall cancellation rate into branches of deposit type, lead time bucket, customer segment, and country of origin.

---

## 5. Page 4: Insights and Assumptions

- **Target Audience**: Executive Leadership, Auditors, BI Technical Administrators.
- **Core Purpose**: Authoritative reference documenting analytical findings, KPI definitions, methodological assumptions, and operational constraints.

### Visual Inventory & Coordinates

```
y: 80   +-----------------------------------------------------------+
        | Visual P4.1: Capacity & Window Header Card                | (h: 45)
y: 125  +-----------------------------------------------------------+
y: 135  +-----------------------------+-----------------------------+
        | Visual P4.2:                | Visual P4.3:                | (h: 340)
        | Key Strategic Insights &    | Core Analytical Definitions |
        | Commercial Takeaways        | (Rules K1 to K7)            |
y: 475  +-----------------------------+-----------------------------+
y: 485  +-----------------------------+-----------------------------+
        | Visual P4.4:                | Visual P4.5:                | (h: 220)
        | Methodological Assumptions  | Technical Architecture &    |
        | & Operational Limitations   | Refresh Protocol            |
y: 705  +-----------------------------+-----------------------------+
```

#### Visual P4.1: Capacity & Window Header Card
- **Visual Type**: Card
- **Placement**: `x: 20`, `y: 80`, `w: 1240`, `h: 45`
- **Fields**: `[Capacity Text]`, `[Window Start]`, `[Window End]`
- **Format**: `Text`
- **Display**: "Derived Capacity (Rule W2): City Hotel: 250 rooms | Resort Hotel: 210 rooms  •  Reliable Window (Rule W1): 2015-08-01 to 2017-08-31"

#### Visual P4.2: Executive Key Strategic Insights
- **Visual Type**: Rich Text Box
- **Placement**: `x: 20`, `y: 135`, `w: 600`, `h: 340`
- **Content** (derived from `powerbi/DASHBOARD_TEXT.md`):
  - **1. Cancellation Volume & Attrition**: 44,223 bookings (37.0%) canceled across the portfolio, driven by extreme lead times (>180 days cancel at >55%) and wholesale group deposit structures.
  - **2. The Non-Refundable Deposit Paradox**: Non-refundable bookings exhibit a ~99% cancellation rate in City Hotel due to rigid tour operator allocation blocks booked far in advance without flexible release windows.
  - **3. Seasonal Yield Divergence**: Resort Hotel commands a peak August ADR of $186+ (driving summer RevPAR of $145+), but suffers severe off-peak contraction ($48 ADR in winter). City Hotel maintains steady urban year-round occupancy (~70-80%) with corporate and transient demand.
  - **4. Commercial Underperformers**: Groups and Offline TA/TO represent significant room-night volume but suffer sub-benchmark ADR and elevated cancellation rates.

#### Visual P4.3: Core Analytical Definitions (Rules K1–K7)
- **Visual Type**: Rich Text Box
- **Placement**: `x: 640`, `y: 135`, `w: 620`, `h: 340`
- **Content**:
  - **K1. Room-Night Sold**: Exactly one non-cancelled booking stayed for one night across calendar dates (`arrival_date` to `checkout_date - 1`). Zero-night stays produce 0 room nights.
  - **K2. Room Revenue**: Sum of individual stay-night ADR values (`fact_stay_nights[adr]`). Cancelled bookings yield 0 revenue.
  - **K3. ADR**: $\frac{\text{Room Revenue}}{\text{Room Nights Sold}}$. Never use unweighted average of booking rates.
  - **K4. Occupancy % & RevPAR**: $\text{Occupancy} = \frac{\text{Room Nights Sold}}{\text{Available Rooms}}$, $\text{RevPAR} = \frac{\text{Room Revenue}}{\text{Available Rooms}} = \text{ADR} \times \text{Occupancy}$.
  - **K5. Cancellation Rate**: $\frac{\text{Cancelled Bookings}}{\text{Total Bookings}}$, attributed to arrival cohort.
  - **K6. Stay Conversion**: $\frac{\text{Check-Out Bookings}}{\text{Total Bookings}} = 1 - \text{Cancel Rate}$. (Proxy measure: dataset lacks website enquiry funnel).
  - **K7. Segment Slicing Constraint**: Occupancy and RevPAR exist strictly at hotel level. Slicing them by segment calculates **contribution to hotel total**, not internal segment occupancy.

#### Visual P4.4: Methodological Assumptions & Limitations
- **Visual Type**: Rich Text Box
- **Placement**: `x: 20`, `y: 485`, `w: 600`, `h: 220`
- **Content**:
  - **W1. Reliable Window**: Stay-night KPIs restricted to 2015-08-01 through 2017-08-31 (762 days). Stays commencing prior to 2015-07-01 and departures after 2017-08-31 are absent from source data.
  - **W2. Capacity Derivation**: The raw dataset contains no room inventory. Capacity is derived from peak observed rooms sold during the reliable window plus a 10% buffer rounded up to the nearest 10: City Hotel = 250 rooms, Resort Hotel = 210 rooms.
  - **D5. Excluded Records**: Exactly 2 ADR outlier records ($ADR < 0$ and $ADR > 1000$) excluded and isolated in `data/processed/excluded_rows.csv`.

#### Visual P4.5: Architecture & Refresh Protocol
- **Visual Type**: Rich Text Box
- **Placement**: `x: 640`, `y: 485`, `w: 620`, `h: 220`
- **Content**:
  - **Star Schema Ingestion**: Star schema generated via `src/export_powerbi_model.py` and validated via `src/validate_powerbi_model.py` (16/16 checks PASS).
  - **Zero-Drift Typing**: 6 M queries loaded using single `DataFolder` parameter with explicit `"en-US"` cultural conversion.
  - **Model Integrity**: Strict 1-to-many single direction filtering. Auto date/time disabled.

---

## 6. Supporting Page A: Segment Detail (Drill-Through Page)

- **Page Configuration**:
  - **Page Type**: Standard canvas (1280 x 720).
  - **Drill-Through Target**: `dim_profile[market_segment]`.
  - **Cross-Report Drill-Through**: Enabled.

### Visual Inventory & Coordinates
```
y: 10   +-----------------------------------------------------------+
        | Back Button (x: 20, y: 15) | Header: Segment Drill-Through| (h: 60)
y: 70   +-----------------------------------------------------------+
y: 80   +-------------+-------------+-------------+-------------+
        | Card SA.1   | Card SA.2   | Card SA.3   | Card SA.4   | (h: 90)
        | Bookings    | Cancel Rate | ADR         | Nights Sold |
y: 170  +-------------+-------------+-------------+-------------+
y: 185  +------------------------------------+----------------------+
        | Visual SA.5:                       | Visual SA.6:         | (h: 515)
        | Monthly ADR & Cancel Rate Trend    | Top 10 Guest Origin  |
        | for Selected Segment               | Countries Table      |
y: 700  +------------------------------------+----------------------+
```

#### Visual SA.1 to SA.4: Segment KPI Cards Row (`y: 80`, `h: 90`)
| ID | Title / Measure | X | Y | W | H | Display Measure | Format | Alt Text |
| :-: | :--- | :-: | :-: | :-: | :-: | :--- | :---: | :--- |
| **SA.1** | Bookings | 20 | 80 | 295 | 90 | `[Bookings]` | `#,##0` | Total reservations in filtered segment. |
| **SA.2** | Cancel Rate % | 335 | 80 | 295 | 90 | `[Cancel Rate %]` | `0.0%` | Cancellation rate in filtered segment. |
| **SA.3** | ADR | 650 | 80 | 295 | 90 | `[ADR]` | `#,##0.00` | Realized ADR in filtered segment. |
| **SA.4** | Room Nights Sold | 965 | 80 | 295 | 90 | `[Room Nights Sold]` | `#,##0` | Total stayed nights in filtered segment. |

#### Visual SA.5: Monthly Segment Trend Line Chart
- **Visual Type**: Line and Clustered Column Chart
- **Placement**: `x: 20`, `y: 185`, `w: 750`, `h: 515`
- **Title**: Monthly Performance Pace: Room Nights Sold & ADR
- **Fields**:
  - **Shared X-Axis**: `dim_date[year_month]`
  - **Column Values (Y-Axis 1)**: `[Room Nights Sold]` (Fill: `#4A5568`, Title: "Nights Sold")
  - **Line Values (Y-Axis 2)**: `[ADR]` (Stroke: `#D97706`, Title: "ADR ($)")
  - **Legend**: `dim_hotel[hotel]`
- **Alt Text**: Monthly pace of room-nights sold and realized ADR for the drill-through market segment.

#### Visual SA.6: Top 10 Guest Countries Matrix/Table
- **Visual Type**: Table
- **Placement**: `x: 790`, `y: 185`, `w: 470`, `h: 515`
- **Title**: Top 10 Guest Origin Countries
- **Fields**:
  - `fact_bookings[country]`
  - `[Bookings]` (`#,##0`)
  - `[Cancel Rate %]` (`0.0%`)
  - `[ADR]` (`#,##0.00`)
  - `[Room Revenue]` (`#,##0.00`)
- **Filters**: Top N Filter on visual: Top 10 by `[Bookings]`.
- **Sort**: Sorted descending by `[Bookings]`.
- **Alt Text**: Table listing the top 10 source countries by reservation volume for this segment.

---

## 7. Supporting Page B: KPI Tooltip (Tooltip Canvas)

- **Page Configuration**:
  - **Page Type**: Tooltip Page.
  - **Canvas Size**: **Custom: 320 x 240 pixels**.
  - **Tooltip Target**: Hover tooltip for visuals across Pages 1 and 2 (e.g. segment bars, monthly trends).

### Visual Layout & Coordinates
```
y: 10   +-----------------------------------------------------------+
        | Visual SB.1: Dynamic Context Badge Header (h: 35)         |
y: 45   +-----------------------------------------------------------+
y: 50   +-----------------------------------------------------------+
        | Visual SB.2: [Bookings] Card (h: 55)                      |
y: 105  +-----------------------------------------------------------+
y: 110  +-----------------------------------------------------------+
        | Visual SB.3: [Cancel Rate %] Card (h: 55)                 |
y: 165  +-----------------------------------------------------------+
y: 170  +-----------------------------------------------------------+
        | Visual SB.4: [ADR] Card (h: 55)                           |
y: 225  +-----------------------------------------------------------+
```

| ID | Visual Element | X | Y | W | H | Display Measure / Field | Format |
| :-: | :--- | :-: | :-: | :-: | :-: | :--- | :---: |
| **SB.1** | Context Title Card | 10 | 10 | 300 | 35 | Category Name (Auto from hover context) | Text |
| **SB.2** | Bookings Card | 10 | 50 | 300 | 55 | `[Bookings]` | `#,##0` |
| **SB.3** | Cancel Rate % Card | 10 | 110 | 300 | 55 | `[Cancel Rate %]` | `0.0%` |
| **SB.4** | ADR Card | 10 | 170 | 300 | 55 | `[ADR]` | `#,##0.00` |

---

## 8. Keyboard Tab Order & Accessibility Compliance

Ensure proper visual focus navigation for keyboard and screen-reader users (`View > Selection > Tab order`):

### Page 1 (Executive Overview) Tab Order:
1. Slicer: Hotel (`S1`)
2. Slicer: Year (`S2`)
3. Slicer: Market Segment (`S3`)
4. Slicer: Distribution Channel (`S4`)
5. Card: Occupancy % (`P1.1`)
6. Card: ADR (`P1.2`)
7. Card: RevPAR (`P1.3`)
8. Card: Cancel Rate % (`P1.4`)
9. Card: Avg Lead Time (`P1.5`)
10. Card: Stay Conversion % (`P1.6`)
11. Chart: Monthly RevPAR (`P1.7`)
12. Chart: Booking & Cancellation Pace (`P1.8`)
13. Banner: Assumption Footnote (`P1.9`)

### Page 2 (Revenue and Segments) Tab Order:
1. Slicer Strip (`S1`, `S2`, `S3`, `S4`)
2. Chart: ADR by Market Segment (`P2.1`)
3. Chart: Revenue Share % Treemap (`P2.2`)
4. Matrix: Performance by Hotel and Segment (`P2.3`)
5. Chart: ADR Seasonality Curve (`P2.4`)

### Page 3 (Cancellations) Tab Order:
1. Slicer Strip (`S1`, `S2`, `S3`, `S4`)
2. Chart: Cancel Rate by Lead Bucket (`P3.1`)
3. Chart: Cancelled Bookings by Timing (`P3.2`)
4. Chart: Deposit Type Cancel Rate (`P3.3`)
5. Chart: Market Segment Cancel Rate (`P3.4`)
6. Chart: Customer Type Cancel Rate (`P3.5`)
7. Tree: Cancellation Decomposition Tree (`P3.6`)

---

## 9. Rule K7 Compliance: Segment Metric Labelling Requirement

> [!CAUTION]
> **Authoritative Compliance Rule**:
> In accordance with **Rule K7**, property room capacity exists **only at the hotel level** (`fact_capacity`). There is no concept of room capacity per market segment or channel.
>
> Whenever a visual, card, or matrix displays `[Occupancy %]` or `[RevPAR]` while grouped or filtered by `dim_profile[market_segment]` or `dim_profile[distribution_channel]`, the report author **MUST**:
> 1. Explicitly title or rename the field header to:
>    - **"Contribution to Hotel Occupancy %"**
>    - **"Contribution to Hotel RevPAR"**
> 2. Add visual subtitle or tooltip note:
>    *"Calculated as segment room nights sold (or revenue) divided by total property available room capacity per Rule K7."*
