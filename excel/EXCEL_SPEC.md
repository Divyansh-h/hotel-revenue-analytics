# Technical Specification: Hotel Revenue & Occupancy Analytics Workbook

- **Target Artifact**: `excel/hotel_kpi_summary.xlsx`
- **Generation Engine**: Python `XlsxWriter` (`src/build_excel_workbook.py`)
- **Authoritative Data Sources**: PostgreSQL `hotel_analytics` schema `hotel`, `config/assumptions.yml`, and exported data marts in `data/outputs/*.csv`
- **Workbook Structure**: 15 Worksheets (10 Functional Modules)
- **Status**: Phase 3 Specification (Frozen Baseline)

---

## 1. Global Workbook Standards & Aesthetics

### 1.1 Color Palette & Visual Hierarchy
To deliver an institutional-grade financial and operational model, the workbook adheres to classic corporate modeling guidelines:
- **Primary Header Dark**: `#1B365D` (Dark Navy) with White (`#FFFFFF`) Bold Text
- **Secondary Header**: `#2F5597` (Medium Navy) with White Bold Text
- **Table Accent / Subtotals**: `#D9E1F2` (Muted Ice Blue) with Dark Text
- **Table Row Striping**: Alternating `#FFFFFF` and `#F2F4F8` (Very Soft Cool Gray)
- **Input Cells (Non-formula Parameters)**: Classic Financial Modeling Standard — Light Yellow Fill (`#FFF2CC`) with Deep Blue Font (`#002060`) and thin border (`#D9D9D9`)
- **Formula / Output Cells**: Automatic Black Font (`#000000`) on Transparent / White fill
- **Status / Health Positive (Pass / OK)**: Soft Mint Green Fill (`#E2EFDA`) with Dark Green Font (`#375623`)
- **Status / Health Alert (Fail / Diff)**: Soft Rose Red Fill (`#FCE4D6`) with Dark Red Font (`#C00000`)
- **Borders**: Thin gray (`#D9D9D9`) on standard cells; Top thin border (`#000000`) and double bottom border (`#000000`) on Total / Summary rows

### 1.2 Typography & Sizing
- **Font Family**: `Segoe UI` (fallback: `Calibri`) across all sheets
- **Workbook Title**: 16pt, Bold, `#1B365D`
- **Section Headers**: 13pt, Bold, `#1B365D`
- **Table Column Headers**: 10pt or 11pt, Bold, `#FFFFFF`
- **Data Rows**: 10pt, Regular
- **Totals / Summaries**: 10pt or 11pt, Bold

### 1.3 Number Formats
- **Currency**: `$#,##0.00` (zero as `$0.00`)
- **Room Nights / Booking Counts**: `#,##0` (thousands separator, no decimals)
- **Percentages**: `0.0%` (1 decimal place) or `0.00%` (2 decimal places for financial KPI checks)
- **ADR / RevPAR / Averages**: `$#,##0.00`
- **Lead Time (Days)**: `0.0` or `#,##0`
- **Calendar Dates**: `YYYY-MM-DD`
- **Month Start Dates**: `YYYY-MM` or `YYYY-MM-DD`

### 1.4 Workbook Layout & Navigation
- **Gridlines**: Explicitly enabled on every sheet.
- **Freeze Panes**:
  - `Data`: Freeze Header Row (Row 1)
  - `Monthly_KPIs`: Freeze Header Row (Row 1)
  - `Assumptions`, `Lookups`, `KPI_Summary`, `Checks`, `Notes`: Freeze below section titles / navigation rows
- **Auto-fit Columns**: All columns padded with a minimum 3-character safety margin to guarantee zero numeric truncation (`###`).

---

## 2. Master Sheet Architecture & Tab Order

The workbook consists of 15 worksheets arranged in exact logical sequence across 10 functional groups:

| Tab Index | Sheet Name | Tab Color | Type / Classification | Purpose & Contents |
| :---: | :--- | :---: | :--- | :--- |
| **1** | `README` | `#1B365D` (Dark Navy) | Documentation | Executive purpose, sheet map, refresh procedure, capacity assumption & caveats |
| **2** | `Assumptions` | `#ED7D31` (Orange) | Parameters / Inputs | Table `tblCapacity` and Named Cells `WindowStart`, `WindowEnd` |
| **3** | `Lookups` | `#70AD47` (Green) | Reference / Dimensional | Table `tblCountry` mapping 178 ISO3 country codes to English names |
| **4** | `Data` | `#4472C4` (Blue) | Analytical Fact Mart | Table `tblBookings` (119,388 rows, 22 base columns + 3 formula columns) |
| **5** | `Monthly_KPIs` | `#2F5597` (Steel Blue) | Stay-Night Mart | Table `tblMonthlyKPI` (50 rows: 7 SQL static columns + 8 formula columns) |
| **6** | `KPI_Summary` | `#7030A0` (Purple) | Executive Reporting | Dynamic summary tables (COUNTIFS/SUMIFS), variance analysis, and embedded charts |
| **7** | `PT_Monthly` | `#A6A6A6` (Gray) | PivotTable Staging | Placeholder tab for manual PivotTable: Monthly Booking Trends & Cancellation Pace |
| **8** | `PT_Segment` | `#A6A6A6` (Gray) | PivotTable Staging | Placeholder tab for manual PivotTable: Market Segment Contribution & ADR |
| **9** | `PT_LeadTime` | `#A6A6A6` (Gray) | PivotTable Staging | Placeholder tab for manual PivotTable: Lead Time Buckets vs Cancellation Rates |
| **10** | `PT_Channel` | `#A6A6A6` (Gray) | PivotTable Staging | Placeholder tab for manual PivotTable: Distribution Channel Performance |
| **11** | `PQ_Monthly` | `#7F7F7F` (Slate) | Power Query Staging | Placeholder tab for Power Query connection to `v_monthly_kpis.csv` |
| **12** | `PQ_Segments` | `#7F7F7F` (Slate) | Power Query Staging | Placeholder tab for Power Query connection to `v_segment_performance.csv` |
| **13** | `PQ_Cancel` | `#7F7F7F` (Slate) | Power Query Staging | Placeholder tab for Power Query connection to `v_cancellation_drivers.csv` |
| **14** | `Checks` | `#C00000` (Red) | Model Governance | Automated reconciliation engine comparing Excel formulas against SQL database |
| **15** | `Notes` | `#595959` (Charcoal) | Audit Trail | Data quality log, decisions D1-D12, KPI formulas K1-K7, and operational notes |

---

## 3. Detailed Worksheet Specifications

---

### Sheet 1: `README`

#### 1. Purpose
Provides executive leadership and auditing analysts with immediate clarity regarding workbook governance, architectural scope, refresh procedures, and modeling boundaries.

#### 2. Layout & Sections
- **Row 1**: Sheet Title: `Hotel Booking Revenue & Occupancy Analytics Summary` (16pt Bold, Navy)
- **Row 2**: Subtitle: `Executive & Operational KPI Reporting Model | PostgreSQL Data Pipeline Integration` (11pt Italic, Muted Gray)
- **Rows 4-10**: **Project Context & Scope**
  - Dataset: 119,388 cleaned reservation records across two properties: City Hotel (Lisbon) and Resort Hotel (Algarve).
  - Arrival dates: July 1, 2015 to August 31, 2017 (26 calendar months).
  - Primary Objectives: Track booking volume, cancellation behavior, room revenue realization, channel distribution, and stay-night KPIs (Occupancy, ADR, RevPAR).
- **Rows 12-25**: **Sheet Directory & Navigation Map**
  - Formatted table listing all 15 sheets, their tab colors, functional classification, and analytical contents.
- **Rows 27-37**: **How to Refresh the Workbook**
  1. *Database ETL*: Execute SQL marts in PostgreSQL via `python src/run_sql.py`.
  2. *Export CSVs*: Run `python src/export_sql_outputs.py` to regenerate CSV files in `data/outputs/`.
  3. *Workbook Rebuild*: Execute `python src/build_excel_workbook.py` to generate `excel/hotel_kpi_summary.xlsx`.
  4. *Power Query / PivotTables*: Open Excel, select **Data > Refresh All** to refresh Power Query connections, and right-click PivotTables to refresh cached pivot caches.
- **Rows 39-55**: **Core Assumptions & Analytical Caveats**
  - **Capacity Derivation Assumption (W2)**:
    > "The raw dataset contains no physical room inventory or physical room counts. Physical capacity is derived per hotel using observed stay-night demand within the reliable window: `Peak_Rooms_Sold` on any single calendar date multiplied by a 1.10 buffer, rounded up to the next ten (`CEIL(Peak * 1.10 / 10) * 10`). City Hotel: Peak 226 rooms (on 2016-08-13) -> 250 rooms capacity. Resort Hotel: Peak 187 rooms (on 2016-03-25) -> 210 rooms capacity. Total portfolio capacity = 460 rooms. Stored in `config/assumptions.yml` and `tblCapacity`. This is an analytical assumption and must accompany all published reports."
  - **Reliable Reporting Window (W1)**:
    > "Stay-night metrics (Occupancy %, ADR, RevPAR) are strictly valid only for stay dates between **2015-08-01** and **2017-08-31** (762 calendar days / 25 full months). Stays that began before 2015-07-01 and arrivals after 2017-08-31 are absent from the dataset, causing partial-month distortion in July 2015 and September 2017. Booking-grain KPIs (total bookings, cancellation rates, lead time) utilize all 26 arrival months."
  - **Stay Conversion Proxy (K6)**:
    > "The dataset contains no website visitor traffic or booking engine enquiry funnel. Stay conversion is defined as `Check-Out Bookings / Total Bookings`, which is mathematically equivalent to `1 - Cancellation Rate`."
  - **Deposit Accounting (K2)**:
    > "No deposit transaction amounts or refund logs exist in the data. Cancelled bookings generate $0 realised room revenue."

---

### Sheet 2: `Assumptions`

#### 1. Purpose
Central parameter store containing the physical capacity inputs and date boundaries. Provides dynamic reference points for lookup formulas in `Monthly_KPIs` and `KPI_Summary`.

#### 2. Layout & Cell Placement
- **Cell A1**: Section Header: `Model Parameters & Physical Inventory Assumptions` (14pt Bold, Navy)
- **Cell A3:D3**: Named Cells Table / Parameter Grid
  - Cell A3: Label `Reliable Window Start` | Cell B3: `2015-08-01` (Named Cell: `WindowStart`)
  - Cell A4: Label `Reliable Window End`   | Cell B4: `2017-08-31` (Named Cell: `WindowEnd`)
  - Cell A5: Label `Reliable Window Days`  | Cell B5: `=DATEDIF(WindowStart, WindowEnd, "d") + 1` (Evaluates to `762`)
  - Cell A6: Label `Capacity Buffer`       | Cell B6: `1.10` (Format: `0.0%` or `0.00`)
- **Row 8**: Table Title: `Table tblCapacity: Hotel Physical Room Inventory`
- **Rows 9-12**: Excel Table `tblCapacity`

#### 3. Table: `tblCapacity`
- **Table Name**: `tblCapacity`
- **Headers**: `Hotel`, `Peak_Rooms_Sold`, `Buffer`, `Rooms`
- **Rows**: 2 data rows (City Hotel, Resort Hotel) + 1 Total Row

| Column Name | Excel Column | Data Type | Data Source | Number Format | Display & Styling Rules | Formula / Rule |
| :--- | :---: | :--- | :--- | :---: | :--- | :--- |
| `Hotel` | A | Text | `hotel.capacity` | General | Left-aligned, Bold | Static Text (`City Hotel`, `Resort Hotel`) |
| `Peak_Rooms_Sold` | B | Integer | `hotel.capacity_derivation` | `#,##0` | Right-aligned | Static: City = `226`, Resort = `187` |
| `Buffer` | C | Decimal | `hotel.capacity_derivation` | `0.0%` | Right-aligned | Static: `1.10` (displayed as `110.0%` or `1.10`) |
| `Rooms` | D | Integer | `hotel.capacity` | `#,##0` | **INPUT STYLE**: Blue font (`#002060`), Light Yellow Fill (`#FFF2CC`), Bold, Thin Border | Static Input Value copied from DB (`250` and `210`). **NOT A FORMULA**. |

- **Total Row**:
  - `Hotel`: `"Total Portfolio"`
  - `Peak_Rooms_Sold`: `=SUM([Peak_Rooms_Sold])` (`413`)
  - `Buffer`: `"-"`
  - `Rooms`: `=SUM([Rooms])` (`460`, Bold, Double Bottom Border)

#### 4. Named Cells
- `WindowStart`: `='Assumptions'!$B$3` (Value: `2015-08-01`, Format: `YYYY-MM-DD`, Scope: `Workbook`)
- `WindowEnd`: `='Assumptions'!$B$4` (Value: `2017-08-31`, Format: `YYYY-MM-DD`, Scope: `Workbook`)

---

### Sheet 3: `Lookups`

#### 1. Purpose
Provides reference dimension mapping tables for decoding raw transactional codes into standardized, human-readable labels.

#### 2. Table: `tblCountry`
- **Table Name**: `tblCountry`
- **Header Range**: `A3:B3`
- **Data Range**: `A4:B181` (178 distinct country codes present in `bookings_clean.csv`)
- **Headers**: `Code`, `Country_Name`

| Column Name | Excel Column | Data Type | Data Source | Number Format | Display & Styling Rules | Description |
| :--- | :---: | :--- | :--- | :---: | :--- | :--- |
| `Code` | A | Text | Distinct `country` in `hotel.bookings` | General | Centered, Bold, Fixed Width | ISO 3166-1 alpha-3 code (e.g. `PRT`, `GBR`, `FRA`, `ESP`, `DEU`, `USA`, plus `Unknown`) |
| `Country_Name` | B | Text | ISO Country Master / Standard Mapping | General | Left-aligned | Full English Country Name (e.g. `Portugal`, `United Kingdom`, `France`, `Spain`, `Germany`, `United States`, plus `Unknown`) |

- **Lookup Coverage**: Guarantees 100% resolution for all 119,388 booking records without unhandled `#N/A` errors.

---

### Sheet 4: `Data`

#### 1. Purpose
Contains the core analytical transactional dataset extracted from `hotel.bookings` (119,388 clean rows). Enriched with calculated columns for downstream PivotTable slicing and formula aggregation.

#### 2. Table: `tblBookings`
- **Table Name**: `tblBookings`
- **Header Range**: `A1:Y1` (25 columns)
- **Data Range**: `A2:Y119389` (119,388 rows)
- **Freeze Panes**: Freeze Row 1 (Header row locked)

#### 3. Column Data Dictionary & Specifications

| # | Column Name | Excel Col | Data Type | Source | Number Format | Display / Alignment | Formula / Logic |
| :---: | :--- | :---: | :--- | :--- | :---: | :--- | :--- |
| 1 | `booking_id` | A | Integer | `hotel.bookings.booking_id` | `0` | Right-aligned | Primary Key (1 to 119,390) |
| 2 | `hotel` | B | Text | `hotel.bookings.hotel` | General | Left-aligned | Property name (`City Hotel` or `Resort Hotel`) |
| 3 | `is_canceled` | C | Integer | `hotel.bookings.is_canceled` | `0` | Centered | Cancellation flag (`1` = Canceled/No-Show, `0` = Stayed) |
| 4 | `reservation_status` | D | Text | `hotel.bookings.reservation_status` | General | Left-aligned | Status (`Check-Out`, `Canceled`, `No-Show`) |
| 5 | `lead_time` | E | Integer | `hotel.bookings.lead_time` | `#,##0` | Right-aligned | Days between booking and arrival |
| 6 | `lead_bucket` | F | Text | `hotel.bookings.lead_bucket` | General | Centered | Grouping: `0-7`, `8-30`, `31-90`, `91-180`, `181+` |
| 7 | `lead_bucket_order` | G | Integer | `hotel.bookings.lead_bucket_order` | `0` | Centered | Sort order (1 to 5) |
| 8 | `arrival_date` | H | Date | `hotel.bookings.arrival_date` | `YYYY-MM-DD` | Centered | Exact arrival date |
| 9 | `arrival_month_start` | I | Date | `hotel.bookings.arrival_month_start` | `YYYY-MM-DD` | Centered | First day of arrival month (`YYYY-MM-01`) |
| 10 | `total_nights` | J | Integer | `hotel.bookings.total_nights` | `#,##0` | Right-aligned | Weekend nights + week nights |
| 11 | `adults` | K | Integer | `hotel.bookings.adults` | `#,##0` | Right-aligned | Number of adult guests |
| 12 | `children` | L | Integer | `hotel.bookings.children` | `#,##0` | Right-aligned | Number of children |
| 13 | `babies` | M | Integer | `hotel.bookings.babies` | `#,##0` | Right-aligned | Number of babies |
| 14 | `country` | N | Text | `hotel.bookings.country` | General | Centered | ISO3 country code (imputed `Unknown` if missing) |
| 15 | `market_segment` | O | Text | `hotel.bookings.market_segment` | General | Left-aligned | Booking channel segment (`Online TA`, `Direct`, etc.) |
| 16 | `distribution_channel` | P | Text | `hotel.bookings.distribution_channel` | General | Left-aligned | Channel mechanism (`TA/TO`, `Direct`, `Corporate`, etc.) |
| 17 | `customer_type` | Q | Text | `hotel.bookings.customer_type` | General | Left-aligned | Customer classification (`Transient`, `Group`, etc.) |
| 18 | `deposit_type` | R | Text | `hotel.bookings.deposit_type` | General | Left-aligned | Policy (`No Deposit`, `Non Refund`, `Refundable`) |
| 19 | `adr` | S | Currency | `hotel.bookings.adr` | `$#,##0.00` | Right-aligned | Average Daily Rate |
| 20 | `room_revenue` | T | Currency | `hotel.bookings.room_revenue` | `$#,##0.00` | Right-aligned | Booked gross revenue (`adr * total_nights`) |
| 21 | `room_type_mismatch` | U | Integer | `hotel.bookings.room_type_mismatch` | `0` | Centered | Operational upgrade / shift flag (`1` / `0`) |
| 22 | `is_duplicate_row` | V | Integer | `hotel.bookings.is_duplicate_row` | `0` | Centered | Duplicate record flag (`1` / `0`) |
| 23 | `Country_Name` | W | Text | **Calculated Column** | General | Left-aligned | `=XLOOKUP([@country], tblCountry[Code], tblCountry[Country_Name], "Unknown")` |
| 24 | `Revenue_Realised` | X | Currency | **Calculated Column** | `$#,##0.00` | Right-aligned | `=IF([@is_canceled]=0, [@room_revenue], 0)` |
| 25 | `Nights_Realised` | Y | Integer | **Calculated Column** | `#,##0` | Right-aligned | `=IF([@is_canceled]=0, [@total_nights], 0)` |

---

### Sheet 5: `Monthly_KPIs`

#### 1. Purpose
Monthly stay-night performance reporting mart covering the reliable window (August 2015 to August 2017; 50 rows = 25 months x 2 hotels). Reconciles SQL database metrics against native Excel spreadsheet formulas to guarantee absolute mathematical fidelity.

#### 2. Table: `tblMonthlyKPI`
- **Table Name**: `tblMonthlyKPI`
- **Header Range**: `A1:O1` (15 columns)
- **Data Range**: `A2:O51` (50 rows)
- **Total Row**: Row 52 (Summary totals for volume and weighted averages for ratios)

#### 3. Column Data Dictionary & Specifications

| # | Column Name | Excel Col | Type | Source | Number Format | Display / Alignment | Formula / Definition |
| :---: | :--- | :---: | :--- | :--- | :---: | :--- | :--- |
| 1 | `Hotel` | A | Text | `v_monthly_kpis.csv` | General | Left-aligned, Bold | Property Name (`City Hotel` or `Resort Hotel`) |
| 2 | `Month_Start` | B | Date | `v_monthly_kpis.csv` | `YYYY-MM-DD` | Centered | First day of stay month (`YYYY-MM-01`) |
| 3 | `Room_Nights_Sold` | C | Integer | `v_monthly_kpis.csv` | `#,##0` | Right-aligned | SQL static room-nights sold |
| 4 | `Room_Revenue` | D | Currency | `v_monthly_kpis.csv` | `$#,##0.00` | Right-aligned | SQL static room revenue ($) |
| 5 | `SQL_Occupancy_Pct` | E | Decimal | `v_monthly_kpis.csv` | `0.00%` | Right-aligned | SQL benchmark occupancy (e.g. `44.39` or `0.4439`) |
| 6 | `SQL_ADR` | F | Currency | `v_monthly_kpis.csv` | `$#,##0.00` | Right-aligned | SQL benchmark ADR |
| 7 | `SQL_RevPAR` | G | Currency | `v_monthly_kpis.csv` | `$#,##0.00` | Right-aligned | SQL benchmark RevPAR |
| 8 | `Days_In_Month` | H | Integer | **Calculated** | `0` | Centered | `=DAY(EOMONTH([@[Month_Start]], 0))` |
| 9 | `Rooms` | I | Integer | **Calculated** | `#,##0` | Right-aligned | `=XLOOKUP([@[Hotel]], tblCapacity[Hotel], tblCapacity[Rooms])` |
| 10 | `Rooms_Available_Nights` | J | Integer | **Calculated** | `#,##0` | Right-aligned | `=[@[Days_In_Month]] * [@[Rooms]]` |
| 11 | `Occupancy_Pct` | K | Decimal | **Calculated** | `0.00%` | Right-aligned | `=[@[Room_Nights_Sold]] / [@[Rooms_Available_Nights]]` |
| 12 | `ADR` | L | Currency | **Calculated** | `$#,##0.00` | Right-aligned | `=[@[Room_Revenue]] / [@[Room_Nights_Sold]]` |
| 13 | `RevPAR` | M | Currency | **Calculated** | `$#,##0.00` | Right-aligned | `=[@[Room_Revenue]] / [@[Rooms_Available_Nights]]` |
| 14 | `Check_Occupancy` | N | Text | **Validation** | General | Centered, Bold | `=IF(ABS([@[Occupancy_Pct]] - [@[SQL_Occupancy_Pct]]/100) < 0.001, "OK", "DIFF")` |
| 15 | `Check_RevPAR` | O | Text | **Validation** | General | Centered, Bold | `=IF(ABS([@[RevPAR]] - [@[SQL_RevPAR]]) < 0.05, "OK", "DIFF")` |

#### 4. Total Row Formulas (Row 52)
- `Hotel`: `"Total / Portfolio Average"`
- `Month_Start`: `"-"`
- `Room_Nights_Sold`: `=SUM([Room_Nights_Sold])` (`248,261`)
- `Room_Revenue`: `=SUM([Room_Revenue])` (`$25,187,186.16`)
- `SQL_Occupancy_Pct`: `"-"`
- `SQL_ADR`: `"-"`
- `SQL_RevPAR`: `"-"`
- `Days_In_Month`: `"-"`
- `Rooms`: `=SUM(tblCapacity[Rooms])` (`460`)
- `Rooms_Available_Nights`: `=SUM([Rooms_Available_Nights])` (`350,520`)
- `Occupancy_Pct`: `=[@[Room_Nights_Sold]] / [@[Rooms_Available_Nights]]` (`70.83%`)
- `ADR`: `=[@[Room_Revenue]] / [@[Room_Nights_Sold]]` (`$101.45`)
- `RevPAR`: `=[@[Room_Revenue]] / [@[Rooms_Available_Nights]]` (`$71.86`)
- `Check_Occupancy`: `=IF(COUNTIF([Check_Occupancy], "DIFF")=0, "ALL OK", "CHECK DIFF")`
- `Check_RevPAR`: `=IF(COUNTIF([Check_RevPAR], "DIFF")=0, "ALL OK", "CHECK DIFF")`

#### 5. Conditional Formatting Rules
- **Columns N & O (`Check_Occupancy`, `Check_RevPAR`)**:
  - Cell Value equal to `"OK"`: Soft Green Fill (`#E2EFDA`), Dark Green Text (`#375623`)
  - Cell Value equal to `"DIFF"`: Soft Red Fill (`#FCE4D6`), Dark Red Text (`#C00000`), Bold
- **Column K (`Occupancy_Pct`)**:
  - Soft 3-color scale (50th percentile `#F8696B`, 75th percentile `#FFEB84`, 90th percentile `#63BE7B`) or Data Bars (Muted Blue `#4472C4`)

---

### Sheet 6: `KPI_Summary`

#### 1. Purpose
Executive C-suite performance dashboard summarizing operational volume, revenue realization, cancellation risk, and stay-night KPIs across both properties. Fully formula-driven from `tblBookings` and `tblMonthlyKPI` with integrated executive charts.

#### 2. Layout Structure & Grid
- **Rows 1-2**: Executive Header Block
  - Title: `HOTEL GROUP EXECUTIVE KPI DASHBOARD` (16pt Bold, Navy `#1B365D`)
  - Subtitle: `Portfolio Performance, Revenue Realisation & Stay-Night Analytics` (10pt Regular, Gray `#595959`)
- **Rows 4-13**: **Section 1: Portfolio Booking & Cancellation Overview (All Arrival Dates)**
  - Summary comparison table driven exclusively by `COUNTIFS` and `SUMIFS` on `tblBookings`.
- **Rows 15-24**: **Section 2: Reliable Window Stay-Night KPIs (2015-08-01 to 2017-08-31)**
  - Stay performance table aggregating room nights, physical capacity, occupancy %, ADR, and RevPAR from `tblMonthlyKPI`.
- **Rows 26-48**: **Section 3: Executive Visualizations (Embedded XlsxWriter Charts)**
  - Chart 1: Monthly Occupancy Trend (City Hotel vs Resort Hotel)
  - Chart 2: Monthly RevPAR & ADR Pace
  - Chart 3: Booking Volume & Cancellation Distribution

#### 3. Section 1: Portfolio Booking & Cancellation Table Specification

Table Range: `A4:M7`
- Column Headers (Row 4):
  - A: `Hotel Property`
  - B: `Total Bookings`
  - C: `Cancellations`
  - D: `No-Shows`
  - E: `Check-Out Stays`
  - F: `Cancellation Rate %`
  - G: `No-Show Rate %`
  - H: `Stay Conversion %`
  - I: `Total Booked Revenue`
  - J: `Realised Revenue`
  - K: `Lost Revenue (Cancelled)`
  - L: `Realised Room Nights`
  - M: `Realised ADR`

Table Data Rows & Exact Formulas:
- **Row 5 (City Hotel)**:
  - `Hotel Property`: `"City Hotel"`
  - `Total Bookings`: `=COUNTIFS(tblBookings[hotel], $A5)` (`79,329`)
  - `Cancellations`: `=COUNTIFS(tblBookings[hotel], $A5, tblBookings[is_canceled], 1)` (`33,101`)
  - `No-Shows`: `=COUNTIFS(tblBookings[hotel], $A5, tblBookings[reservation_status], "No-Show")` (`916`)
  - `Check-Out Stays`: `=COUNTIFS(tblBookings[hotel], $A5, tblBookings[reservation_status], "Check-Out")` (`46,228`)
  - `Cancellation Rate %`: `=$C5 / $B5` (`41.7%`, Format: `0.0%`)
  - `No-Show Rate %`: `=$D5 / $B5` (`1.2%`, Format: `0.0%`)
  - `Stay Conversion %`: `=$E5 / $B5` (`58.3%`, Format: `0.0%`)
  - `Total Booked Revenue`: `=SUMIFS(tblBookings[room_revenue], tblBookings[hotel], $A5)` (`$25,487,034.40`, Format: `$#,##0.00`)
  - `Realised Revenue`: `=SUMIFS(tblBookings[Revenue_Realised], tblBookings[hotel], $A5)` (`$14,394,410.18`, Format: `$#,##0.00`)
  - `Lost Revenue (Cancelled)`: `=$I5 - $J5` (`$11,092,624.22`, Format: `$#,##0.00`)
  - `Realised Room Nights`: `=SUMIFS(tblBookings[Nights_Realised], tblBookings[hotel], $A5)` (`135,153`, Format: `#,##0`)
  - `Realised ADR`: `=$J5 / $L5` (`$106.50`, Format: `$#,##0.00`)
- **Row 6 (Resort Hotel)**:
  - `Hotel Property`: `"Resort Hotel"`
  - `Total Bookings`: `=COUNTIFS(tblBookings[hotel], $A6)` (`40,059`)
  - `Cancellations`: `=COUNTIFS(tblBookings[hotel], $A6, tblBookings[is_canceled], 1)` (`11,122`)
  - `No-Shows`: `=COUNTIFS(tblBookings[hotel], $A6, tblBookings[reservation_status], "No-Show")` (`291`)
  - `Check-Out Stays`: `=COUNTIFS(tblBookings[hotel], $A6, tblBookings[reservation_status], "Check-Out")` (`28,937`)
  - `Cancellation Rate %`: `=$C6 / $B6` (`27.8%`, Format: `0.0%`)
  - `No-Show Rate %`: `=$D6 / $B6` (`0.7%`, Format: `0.0%`)
  - `Stay Conversion %`: `=$E6 / $B6` (`72.2%`, Format: `0.0%`)
  - `Total Booked Revenue`: `=SUMIFS(tblBookings[room_revenue], tblBookings[hotel], $A6)` (`$15,660,119.64`, Format: `$#,##0.00`)
  - `Realised Revenue`: `=SUMIFS(tblBookings[Revenue_Realised], tblBookings[hotel], $A6)` (`$11,601,914.03`, Format: `$#,##0.00`)
  - `Lost Revenue (Cancelled)`: `=$I6 - $J6` (`$4,058,205.61`, Format: `$#,##0.00`)
  - `Realised Room Nights`: `=SUMIFS(tblBookings[Nights_Realised], tblBookings[hotel], $A6)` (`119,877`, Format: `#,##0`)
  - `Realised ADR`: `=$J6 / $L6` (`$96.78`, Format: `$#,##0.00`)
- **Row 7 (Total Portfolio / Combined)**:
  - `Hotel Property`: `"Total Portfolio"` (Bold)
  - `Total Bookings`: `=SUM($B5:$B6)` (`119,388`)
  - `Cancellations`: `=SUM($C5:$C6)` (`44,223`)
  - `No-Shows`: `=SUM($D5:$D6)` (`1,207`)
  - `Check-Out Stays`: `=SUM($E5:$E6)` (`75,165`)
  - `Cancellation Rate %`: `=$C7 / $B7` (`37.0%`, Format: `0.0%`)
  - `No-Show Rate %`: `=$D7 / $B7` (`1.0%`, Format: `0.0%`)
  - `Stay Conversion %`: `=$E7 / $B7` (`63.0%`, Format: `0.0%`)
  - `Total Booked Revenue`: `=SUM($I5:$I6)` (`$41,147,154.04`, Format: `$#,##0.00`)
  - `Realised Revenue`: `=SUM($J5:$J6)` (`$25,996,324.21`, Format: `$#,##0.00`)
  - `Lost Revenue (Cancelled)`: `=$I7 - $J7` (`$15,150,829.83`, Format: `$#,##0.00`)
  - `Realised Room Nights`: `=SUM($L5:$L6)` (`255,030`, Format: `#,##0`)
  - `Realised ADR`: `=$J7 / $L7` (`$101.93`, Format: `$#,##0.00`)

#### 4. Section 2: Stay-Night Performance Table (Reliable Window)

Table Range: `A15:H18`
- Column Headers (Row 15):
  - A: `Hotel Property`
  - B: `Physical Capacity (Rooms)`
  - C: `Available Room Nights`
  - D: `Room Nights Sold`
  - E: `Room Revenue ($)`
  - F: `Occupancy Rate %`
  - G: `Average Daily Rate (ADR)`
  - H: `Revenue Per Avail Room (RevPAR)`

Table Data Rows & Exact Formulas:
- **Row 16 (City Hotel)**:
  - `Hotel Property`: `"City Hotel"`
  - `Physical Capacity`: `=XLOOKUP($A16, tblCapacity[Hotel], tblCapacity[Rooms])` (`250`)
  - `Available Room Nights`: `=SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], $A16)` (`190,500`)
  - `Room Nights Sold`: `=SUMIFS(tblMonthlyKPI[Room_Nights_Sold], tblMonthlyKPI[Hotel], $A16)` (`133,860`)
  - `Room Revenue`: `=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], $A16)` (`$14,285,466.42`)
  - `Occupancy Rate %`: `=$D16 / $C16` (`70.27%`, Format: `0.00%`)
  - `ADR`: `=$E16 / $D16` (`$106.72`, Format: `$#,##0.00`)
  - `RevPAR`: `=$E16 / $C16` (`$74.99`, Format: `$#,##0.00`)
- **Row 17 (Resort Hotel)**:
  - `Hotel Property`: `"Resort Hotel"`
  - `Physical Capacity`: `=XLOOKUP($A17, tblCapacity[Hotel], tblCapacity[Rooms])` (`210`)
  - `Available Room Nights`: `=SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], $A17)` (`160,020`)
  - `Room Nights Sold`: `=SUMIFS(tblMonthlyKPI[Room_Nights_Sold], tblMonthlyKPI[Hotel], $A17)` (`114,401`)
  - `Room Revenue`: `=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], $A17)` (`$10,901,719.74`)
  - `Occupancy Rate %`: `=$D17 / $C17` (`71.49%`, Format: `0.00%`)
  - `ADR`: `=$E17 / $D17` (`$95.29`, Format: `$#,##0.00`)
  - `RevPAR`: `=$E17 / $C17` (`$68.13`, Format: `$#,##0.00`)
- **Row 18 (Total Portfolio / Combined)**:
  - `Hotel Property`: `"Total Portfolio"` (Bold)
  - `Physical Capacity`: `=SUM($B16:$B17)` (`460`)
  - `Available Room Nights`: `=SUM($C16:$C17)` (`350,520`)
  - `Room Nights Sold`: `=SUM($D16:$D17)` (`248,261`)
  - `Room Revenue`: `=SUM($E16:$E17)` (`$25,187,186.16`)
  - `Occupancy Rate %`: `=$D18 / $C18` (`70.83%`, Format: `0.00%`)
  - `ADR`: `=$E18 / $D18` (`$101.45`, Format: `$#,##0.00`)
  - `RevPAR`: `=$E18 / $C18` (`$71.86`, Format: `$#,##0.00`)

#### 5. Section 3: Visualizations & Embedded Charts
Generated natively using XlsxWriter chart objects:
1. **Chart 1: Monthly Occupancy Pace (City vs Resort Hotel)**
   - Type: `line` with smooth markers
   - Categories (X-axis): `=Monthly_KPIs!$B$2:$B$26` (25 stay months)
   - Series 1: Name: `City Hotel Occupancy`, Values: `=Monthly_KPIs!$K$2:$K$26` (Color: `#1B365D`, Dark Navy)
   - Series 2: Name: `Resort Hotel Occupancy`, Values: `=Monthly_KPIs!$K$27:$K$51` (Color: `#ED7D31`, Orange)
   - Formatting: Y-axis formatted as `0%` (bounds: 0.20 to 1.00), major gridlines light gray
   - Location: Positioned at cell `B26:G42`
2. **Chart 2: Monthly RevPAR & ADR Trends**
   - Type: `line`
   - Categories (X-axis): `=Monthly_KPIs!$B$2:$B$26`
   - Series 1: Name: `City Hotel ADR`, Values: `=Monthly_KPIs!$L$2:$L$26` (Dashed Navy)
   - Series 2: Name: `City Hotel RevPAR`, Values: `=Monthly_KPIs!$M$2:$M$26` (Solid Navy)
   - Series 3: Name: `Resort Hotel ADR`, Values: `=Monthly_KPIs!$L$27:$L$51` (Dashed Orange)
   - Series 4: Name: `Resort Hotel RevPAR`, Values: `=Monthly_KPIs!$M$27:$M$51` (Solid Orange)
   - Formatting: Y-axis formatted as Currency `$#,##0`
   - Location: Positioned at cell `I26:N42`

---

### Sheet 7: `PT_Monthly`

#### 1. Purpose
Staging worksheet reserved for manual creation of PivotTable 1.

#### 2. Layout & Instructions
- **Cell A1 Content**:
  `"PivotTable Placeholder: Monthly Booking Trends & Cancellation Analysis. Source: tblBookings. Follow instructions in docs/excel_pivottables_guide.md to build PivotTable (Rows: arrival_month_start; Columns: hotel; Values: Count of booking_id, Sum of is_canceled, Calculated Field for Cancel Rate %)."`
- **Cell Styling**: 11pt, Italic, Deep Navy Font (`#1B365D`), Soft Gray Background Fill (`#F2F4F8`), Thin Gray Border around `A1:K1`.

---

### Sheet 8: `PT_Segment`

#### 1. Purpose
Staging worksheet reserved for manual creation of PivotTable 2.

#### 2. Layout & Instructions
- **Cell A1 Content**:
  `"PivotTable Placeholder: Market Segment Performance & Revenue Contribution. Source: tblBookings. Follow instructions in docs/excel_pivottables_guide.md to build PivotTable (Rows: market_segment; Columns: hotel; Values: Total Bookings, Cancel Rate %, Realised Revenue, Realised Nights, Realised ADR)."`
- **Cell Styling**: 11pt, Italic, Deep Navy Font (`#1B365D`), Soft Gray Background Fill (`#F2F4F8`), Thin Gray Border around `A1:K1`.

---

### Sheet 9: `PT_LeadTime`

#### 1. Purpose
Staging worksheet reserved for manual creation of PivotTable 3.

#### 2. Layout & Instructions
- **Cell A1 Content**:
  `"PivotTable Placeholder: Lead Time Bucket & Cancellation Risk Analysis. Source: tblBookings. Follow instructions in docs/excel_pivottables_guide.md to build PivotTable (Rows: lead_bucket ordered by lead_bucket_order; Columns: hotel; Values: Bookings, Cancellations, Cancel Rate %, Realised Revenue)."`
- **Cell Styling**: 11pt, Italic, Deep Navy Font (`#1B365D`), Soft Gray Background Fill (`#F2F4F8`), Thin Gray Border around `A1:K1`.

---

### Sheet 10: `PT_Channel`

#### 1. Purpose
Staging worksheet reserved for manual creation of PivotTable 4.

#### 2. Layout & Instructions
- **Cell A1 Content**:
  `"PivotTable Placeholder: Distribution Channel Breakdown & Sourcing Mix. Source: tblBookings. Follow instructions in docs/excel_pivottables_guide.md to build PivotTable (Rows: distribution_channel; Columns: hotel; Values: Bookings, Booking Share %, Cancel Rate %, Realised Revenue, ADR)."`
- **Cell Styling**: 11pt, Italic, Deep Navy Font (`#1B365D`), Soft Gray Background Fill (`#F2F4F8`), Thin Gray Border around `A1:K1`.

---

### Sheet 11: `PQ_Monthly`

#### 1. Purpose
Staging worksheet reserved for Power Query Ingestion 1.

#### 2. Layout & Instructions
- **Cell A1 Content**:
  `"Power Query Destination Placeholder: Ingest and load data/outputs/v_monthly_kpis.csv into an Excel Table here. Follow step-by-step instructions in docs/excel_powerquery_guide.md."`
- **Cell Styling**: 11pt, Italic, Slate Gray Font (`#595959`), Soft Muted Blue Fill (`#D9E1F2`), Thin Border around `A1:K1`.

---

### Sheet 12: `PQ_Segments`

#### 1. Purpose
Staging worksheet reserved for Power Query Ingestion 2.

#### 2. Layout & Instructions
- **Cell A1 Content**:
  `"Power Query Destination Placeholder: Ingest and load data/outputs/v_segment_performance.csv into an Excel Table here. Follow step-by-step instructions in docs/excel_powerquery_guide.md."`
- **Cell Styling**: 11pt, Italic, Slate Gray Font (`#595959`), Soft Muted Blue Fill (`#D9E1F2`), Thin Border around `A1:K1`.

---

### Sheet 13: `PQ_Cancel`

#### 1. Purpose
Staging worksheet reserved for Power Query Ingestion 3.

#### 2. Layout & Instructions
- **Cell A1 Content**:
  `"Power Query Destination Placeholder: Ingest and load data/outputs/v_cancellation_drivers.csv into an Excel Table here. Follow step-by-step instructions in docs/excel_powerquery_guide.md."`
- **Cell Styling**: 11pt, Italic, Slate Gray Font (`#595959`), Soft Muted Blue Fill (`#D9E1F2`), Thin Border around `A1:K1`.

---

### Sheet 14: `Checks`

#### 1. Purpose
Automated audit and model governance sheet executing dynamic formula-based assertions comparing Excel calculations against authoritative PostgreSQL data warehouse totals. Guarantees 0 silent data drift.

#### 2. Layout Structure & Summary Banner
- **Row 1**: Sheet Header: `Model Integrity & Database Reconciliation Audit` (16pt Bold, Navy)
- **Row 3**: Summary Audit Card / Banner:
  - Cell A3: Label: `OVERALL RECONCILIATION AUDIT STATUS` (11pt Bold)
  - Cell B3: `=IF(COUNTIF(tblChecks[Status], "FAIL")=0, "ALL CHECKS PASS", "AUDIT ALERT: CHECKS FAILED")`
  - Conditional Formatting on B3:
    - If `"ALL CHECKS PASS"`: Bold White Font on Dark Green (`#375623`), Size 12pt
    - If `"AUDIT ALERT: CHECKS FAILED"`: Bold White Font on Dark Red (`#C00000`), Size 12pt
- **Row 5**: Table Title: `Table tblChecks: Automated Financial & Transactional Assertions`
- **Rows 6-24**: Table `tblChecks`

#### 3. Table: `tblChecks`
- **Table Name**: `tblChecks`
- **Headers**: `Check_ID`, `Metric_Description`, `Scope_Grain`, `Expected_DB_Value`, `Excel_Formula_Value`, `Variance`, `Tolerance`, `Status`

| Check ID | Metric Description | Scope / Grain | Expected DB Value | Excel Formula Value | Variance Formula | Tolerance | Status Formula | Expected Result |
| :---: | :--- | :--- | :---: | :--- | :---: | :---: | :--- | :---: |
| **C01** | Total Cleaned Bookings Count | Full Dataset | `119388` | `=COUNTA(tblBookings[booking_id])` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C02** | City Hotel Total Bookings | Property Grain | `79329` | `=COUNTIFS(tblBookings[hotel], "City Hotel")` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C03** | Resort Hotel Total Bookings | Property Grain | `40059` | `=COUNTIFS(tblBookings[hotel], "Resort Hotel")` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C04** | Total Cancellations Count (`is_canceled=1`) | Full Dataset | `44223` | `=COUNTIFS(tblBookings[is_canceled], 1)` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C05** | Total Check-Out Stays Count | Full Dataset | `75165` | `=COUNTIFS(tblBookings[reservation_status], "Check-Out")` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C06** | Total No-Show Reservations Count | Full Dataset | `1207` | `=COUNTIFS(tblBookings[reservation_status], "No-Show")` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C07** | Overall Cancellation Rate % | Portfolio | `0.3704` | `=COUNTIFS(tblBookings[is_canceled], 1) / COUNTA(tblBookings[booking_id])` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0.0001` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C08** | Total Realised Revenue ($) | Check-Outs | `25996324.21` | `=SUM(tblBookings[Revenue_Realised])` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0.01` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C09** | Total Realised Room Nights | Check-Outs | `255030` | `=SUM(tblBookings[Nights_Realised])` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C10** | Window Room Nights Sold | Reliable Window | `248261` | `=SUM(tblMonthlyKPI[Room_Nights_Sold])` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C11** | Window Available Room Nights | Reliable Window | `350520` | `=SUM(tblMonthlyKPI[Rooms_Available_Nights])` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C12** | Window Total Room Revenue ($) | Reliable Window | `25187186.16` | `=SUM(tblMonthlyKPI[Room_Revenue])` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0.01` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C13** | Window Portfolio Occupancy % | Reliable Window | `0.7083` | `=SUM(tblMonthlyKPI[Room_Nights_Sold]) / SUM(tblMonthlyKPI[Rooms_Available_Nights])` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0.0001` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C14** | Window Portfolio ADR ($) | Reliable Window | `101.45` | `=SUM(tblMonthlyKPI[Room_Revenue]) / SUM(tblMonthlyKPI[Room_Nights_Sold])` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0.01` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C15** | Window Portfolio RevPAR ($) | Reliable Window | `71.86` | `=SUM(tblMonthlyKPI[Room_Revenue]) / SUM(tblMonthlyKPI[Rooms_Available_Nights])` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0.01` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C16** | RevPAR Identity Equality ($) | Portfolio | `0.00` | `=ABS(([@[Excel_Formula_Value C14]] * [@[Excel_Formula_Value C13]]) - [@[Excel_Formula_Value C15]])` | `=[@[Excel_Formula_Value]] - 0` | `0.05` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C17** | Duplicate Bookings Flagged | Quality Flag | `31994` | `=COUNTIFS(tblBookings[is_duplicate_row], 1)` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |
| **C18** | Room Type Mismatches Flagged | Quality Flag | `14916` | `=COUNTIFS(tblBookings[room_type_mismatch], 1)` | `=[@[Excel_Formula_Value]] - [@[Expected_DB_Value]]` | `0` | `=IF(ABS([@Variance])<=[@Tolerance], "PASS", "FAIL")` | **PASS** |

#### 4. Conditional Formatting on `tblChecks[Status]`
- Value equal to `"PASS"`: Soft Green Fill (`#E2EFDA`), Dark Green Bold Font (`#375623`)
- Value equal to `"FAIL"`: Soft Red Fill (`#FCE4D6`), Dark Red Bold Font (`#C00000`)

---

### Sheet 15: `Notes`

#### 1. Purpose
Comprehensive data quality audit trail, cleaning decision log, and analytical assumptions summary mirroring `docs/data_quality_log.md` and `docs/decision_log.md`.

#### 2. Layout & Sections
- **Row 1**: Sheet Header: `Data Governance, Cleaning Log & Analytical Decisions` (16pt Bold, Navy)
- **Rows 4-18**: **Section 1: Data Cleaning Decisions (D1 to D12)**
  - Table summarizing every formal decision, rule definition, and implementation impact.
- **Rows 20-36**: **Section 2: Data Quality Profile & Outlier Audit**
  - Table replicating `docs/data_quality_log.md` with affected rows, percentages, actions, and post-clean verification counts.
- **Rows 38-50**: **Section 3: Revenue & Occupancy Key Principles (K1 to K7)**
  - Definitional guide explaining room night attribution, ADR formulas, RevPAR identities, cancellation attribution, and room capacity limits.

---

## 4. Manual PivotTables Specification (User Guide Summary)

The following 4 PivotTables will be manually inserted by the analyst using `tblBookings` as the Data Source:

### PivotTable 1: Monthly Booking Trends & Cancellation Pace (`PT_Monthly`)
- **Target Sheet & Location**: Sheet `PT_Monthly`, Cell `A3`
- **Data Source**: `tblBookings`
- **Rows**: `arrival_month_start` (Grouped / formatted as `YYYY-MM`)
- **Columns**: `hotel` (`City Hotel`, `Resort Hotel`)
- **Values Area**:
  1. `booking_id` -> Summarize by: `Count`, Label: `Bookings` (Format: `#,##0`)
  2. `is_canceled` -> Summarize by: `Sum`, Label: `Cancellations` (Format: `#,##0`)
  3. Calculated Field `Cancel_Rate_Pct` -> Formula: `='is_canceled' / 'booking_id'`, Label: `Cancel Rate %` (Format: `0.0%`)
  4. `Revenue_Realised` -> Summarize by: `Sum`, Label: `Realised Revenue` (Format: `$#,##0`)
- **Layout & Style**: Tabular Form, Show Subtotals at Top/Bottom disabled, Grand Totals enabled for rows and columns. Style: `PivotStyleMedium9` (Blue).

### PivotTable 2: Market Segment Performance & ADR Analysis (`PT_Segment`)
- **Target Sheet & Location**: Sheet `PT_Segment`, Cell `A3`
- **Data Source**: `tblBookings`
- **Rows**: `market_segment`
- **Columns**: `hotel`
- **Values Area**:
  1. `booking_id` -> Summarize by: `Count`, Label: `Bookings` (Format: `#,##0`)
  2. Calculated Field `Cancel_Rate_Pct` -> Formula: `='is_canceled' / 'booking_id'`, Label: `Cancel %` (Format: `0.0%`)
  3. `Nights_Realised` -> Summarize by: `Sum`, Label: `Realised Nights` (Format: `#,##0`)
  4. `Revenue_Realised` -> Summarize by: `Sum`, Label: `Realised Revenue` (Format: `$#,##0`)
  5. Calculated Field `Realised_ADR` -> Formula: `='Revenue_Realised' / 'Nights_Realised'`, Label: `Realised ADR` (Format: `$#,##0.00`)
- **Sort**: `Bookings` descending. Style: `PivotStyleMedium2`.

### PivotTable 3: Lead Time Bucket & Cancellation Risk (`PT_LeadTime`)
- **Target Sheet & Location**: Sheet `PT_LeadTime`, Cell `A3`
- **Data Source**: `tblBookings`
- **Rows**: `lead_bucket` (Sorted by `lead_bucket_order`: `0-7`, `8-30`, `31-90`, `91-180`, `181+`)
- **Columns**: `hotel`
- **Values Area**:
  1. `booking_id` -> Summarize by: `Count`, Label: `Bookings` (Format: `#,##0`)
  2. `is_canceled` -> Summarize by: `Sum`, Label: `Cancellations` (Format: `#,##0`)
  3. Calculated Field `Cancel_Rate_Pct` -> Formula: `='is_canceled' / 'booking_id'`, Label: `Cancel %` (Format: `0.0%`)
  4. `Revenue_Realised` -> Summarize by: `Sum`, Label: `Realised Revenue` (Format: `$#,##0`)
- **Style**: `PivotStyleMedium10`.

### PivotTable 4: Distribution Channel Breakdown (`PT_Channel`)
- **Target Sheet & Location**: Sheet `PT_Channel`, Cell `A3`
- **Data Source**: `tblBookings`
- **Rows**: `distribution_channel`
- **Columns**: `hotel`
- **Values Area**:
  1. `booking_id` -> Summarize by: `Count`, Label: `Bookings` (Format: `#,##0`)
  2. `booking_id` (second instance) -> Show Values As: `% of Column Total`, Label: `Share %` (Format: `0.0%`)
  3. Calculated Field `Cancel_Rate_Pct` -> Formula: `='is_canceled' / 'booking_id'`, Label: `Cancel %` (Format: `0.0%`)
  4. `Revenue_Realised` -> Summarize by: `Sum`, Label: `Realised Revenue` (Format: `$#,##0`)
- **Sort**: `Bookings` descending. Style: `PivotStyleMedium9`.

---

## 5. Manual Power Query Queries Specification (User Guide Summary)

The following 3 Power Query M queries will be manually set up by the analyst to link the exported CSV marts:

### Power Query 1: Monthly KPIs Mart (`PQ_Monthly`)
- **Source File**: `data/outputs/v_monthly_kpis.csv`
- **Target Load Sheet & Cell**: Sheet `PQ_Monthly`, Cell `A1` (Loaded as Excel Table `tblPQMonthly`)
- **Transformations**:
  1. Load CSV via `Csv.Document(File.Contents(".../data/outputs/v_monthly_kpis.csv"), [Delimiter=",", Encoding=65001])`
  2. Promote Headers (`Table.PromoteHeaders`)
  3. Enforce Types:
     - `hotel`: `type text`
     - `month_start`: `type date`
     - `room_nights_sold`: `Int64.Type`
     - `room_nights_available`: `Int64.Type`
     - `room_revenue`: `type number`
     - `occupancy_pct`: `type number`
     - `adr`: `type number`
     - `revpar`: `type number`

### Power Query 2: Segment Performance Mart (`PQ_Segments`)
- **Source File**: `data/outputs/v_segment_performance.csv`
- **Target Load Sheet & Cell**: Sheet `PQ_Segments`, Cell `A1` (Loaded as Excel Table `tblPQSegments`)
- **Transformations**:
  1. Load CSV via `Csv.Document(File.Contents(".../data/outputs/v_segment_performance.csv"), [Delimiter=",", Encoding=65001])`
  2. Promote Headers
  3. Enforce Types:
     - `hotel`: `type text`
     - `market_segment`: `type text`
     - `bookings`: `Int64.Type`
     - `cancellations`: `Int64.Type`
     - `cancel_rate_pct`: `type number`
     - `room_nights_sold`: `Int64.Type`
     - `room_revenue`: `type number`
     - `adr`: `type number`
     - `room_night_share_pct`: `type number`
     - `revenue_share_pct`: `type number`

### Power Query 3: Cancellation Drivers Mart (`PQ_Cancel`)
- **Source File**: `data/outputs/v_cancellation_drivers.csv`
- **Target Load Sheet & Cell**: Sheet `PQ_Cancel`, Cell `A1` (Loaded as Excel Table `tblPQCancel`)
- **Transformations**:
  1. Load CSV via `Csv.Document(File.Contents(".../data/outputs/v_cancellation_drivers.csv"), [Delimiter=",", Encoding=65001])`
  2. Promote Headers
  3. Enforce Types:
     - `hotel`: `type text`
     - `dimension`: `type text`
     - `category`: `type text`
     - `sort_order`: `Int64.Type` (nullable)
     - `bookings`: `Int64.Type`
     - `cancellations`: `Int64.Type`
     - `no_shows`: `Int64.Type`
     - `cancel_rate_pct`: `type number`
     - `share_of_bookings_pct`: `type number`
     - `cancel_rate_vs_hotel_avg_pp`: `type number`

---

## 6. Verification & Frozen Sign-off Gate

Prior to workbook generation in subsequent prompts, the following must hold true:
1. `excel/EXCEL_SPEC.md` exists and is authoritative.
2. All sheet names, table names, named ranges, and column headers are frozen.
3. No Python workbook generation script (`build_excel_workbook.py`) is executed during this specification phase.
