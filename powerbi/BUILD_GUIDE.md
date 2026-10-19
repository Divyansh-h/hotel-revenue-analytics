# Power BI Desktop Step-by-Step Build Guide (`BUILD_GUIDE.md`)

> [!IMPORTANT]
> **Prerequisites & Environment**:
> - **Platform**: Power BI Desktop (Windows 64-bit).
> - **Source Data**: The 6 validated star schema CSVs located in `powerbi/data/`.
> - **Configuration Files**:
>   - Power Query Scripts: [`powerbi/power_query/*.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/)
>   - Data Model Specification: [`powerbi/MODEL_SPEC.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/MODEL_SPEC.md)
>   - Explicit DAX Measures: [`powerbi/measures.dax`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/measures.dax)
>   - Baseline Validation Benchmarks: [`powerbi/validation_expected.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/validation_expected.csv)
>   - Report Layout & Visual Specifications: [`powerbi/REPORT_SPEC.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/REPORT_SPEC.md)
>   - Visual Copy & Strategic Text: [`powerbi/DASHBOARD_TEXT.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/DASHBOARD_TEXT.md)
>   - Custom Theme: [`powerbi/theme/hotel_theme.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/theme/hotel_theme.json)

---

## Table of Contents
1. [Phase 1: Ingestion & Power Query Setup](#1-phase-1-ingestion--power-query-setup)
2. [Phase 2: Data Model, Relationships & Date Intelligence](#2-phase-2-data-model-relationships--date-intelligence)
3. [Phase 3: Dedicated Measures Table & Validation](#3-phase-3-dedicated-measures-table--validation)
4. [Phase 4: Import Custom Report Theme](#4-phase-4-import-custom-report-theme)
5. [Phase 5: Visual-by-Visual Canvas Construction](#5-phase-5-visual-by-visual-canvas-construction)
6. [Phase 6: Slicer Synchronization, Tooltips & Interactions](#6-phase-6-slicer-synchronization-tooltips--interactions)
7. [Phase 7: Final Polish, Accessibility & Saving](#7-phase-7-final-polish-accessibility--saving)
8. [Phase 8: PDF Export & Artifact Verification](#8-phase-8-pdf-export--artifact-verification)
9. [Troubleshooting: The 8 Most Common Issues](#9-troubleshooting-the-8-most-common-issues)

---

## 1. Phase 1: Ingestion & Power Query Setup
*Estimated Time: 15 minutes*

In this step, you will create a central file-path parameter (`DataFolder`) and import the 6 star schema tables via Power Query's Advanced Editor.

### Step 1.1: Launch Power Query Editor
1. Open **Power BI Desktop**.
2. If the start splash screen appears, close it.
3. On the **Home** ribbon, click **Transform data** (or press `Alt + H + T`). Power Query Editor opens in a new window.

### Step 1.2: Configure Privacy Settings (Prevents Formula.Firewall Errors)
1. In Power Query Editor, click **File > Options and settings > Options**.
2. Under **Current File** (left sidebar), click **Privacy**.
3. Select **Ignore the Privacy Levels and potentially improve performance**.
4. Click **OK**.

### Step 1.3: Create the `DataFolder` Parameter
1. In Power Query Editor, go to **Home > New Source > Blank Query**.
2. Click **View > Advanced Editor** (or **Home > Advanced Editor**).
3. Select and delete any code in the editor window.
4. Open [`powerbi/power_query/parameters.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/parameters.m) and paste its contents:
   ```powerquery
   "C:\path\to\hotel-revenue-analytics\powerbi\data\" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
   ```
5. Update the string to the exact full Windows path to your `powerbi\data\` folder. **Crucial**: Ensure the path ends with a trailing backslash `\`.
6. Click **Done**.
7. In the **Query Settings** pane on the right under **Properties**, change the **Name** to:
   ```text
   DataFolder
   ```
8. Press `Enter`.

### Step 1.4: Ingest the 6 Dimensional Tables
For each of the 6 tables below, repeat these sub-steps:
1. Click **Home > New Source > Blank Query**.
2. Click **Advanced Editor**.
3. Clear existing text, open the corresponding `.m` script file from [`powerbi/power_query/`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/), and paste the entire script:
   - For `dim_date`: use [`dim_date.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/dim_date.m)
   - For `dim_hotel`: use [`dim_hotel.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/dim_hotel.m)
   - For `dim_profile`: use [`dim_profile.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/dim_profile.m)
   - For `fact_bookings`: use [`fact_bookings.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/fact_bookings.m)
   - For `fact_stay_nights`: use [`fact_stay_nights.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/fact_stay_nights.m)
   - For `fact_capacity`: use [`fact_capacity.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/fact_capacity.m)
4. Click **Done**.
5. In the **Query Settings** pane on the right, rename the query to the exact table name: `dim_date`, `dim_hotel`, `dim_profile`, `fact_bookings`, `fact_stay_nights`, `fact_capacity`.

### Step 1.5: Close & Apply
1. On the **Home** ribbon, click **Close & Apply**.
2. Power BI loads all 6 tables into memory.

> [!CHECK]
> **You should now see**:
> Switch to the **Data view** (second icon on the far left rail). Click each table in the Data pane and confirm the row count displayed at the bottom left:
> - `dim_date`: **1,096 rows**
> - `dim_hotel`: **2 rows**
> - `dim_profile`: **101 rows**
> - `fact_bookings`: **119,388 rows**
> - `fact_stay_nights`: **248,261 rows**
> - `fact_capacity`: **1,524 rows**

---

## 2. Phase 2: Data Model, Relationships & Date Intelligence
*Estimated Time: 15 minutes*

In this step, you will configure relationships, eliminate hidden local date hierarchies, mark the calendar dimension, and set sort-by columns.

### Step 2.1: Disable Power BI Auto Date/Time
1. In Power BI Desktop, click **File > Options and settings > Options**.
2. Under **Current File** on the left menu, select **Data Load**.
3. Under **Time intelligence**, **uncheck** `Auto date/time`.
4. Click **OK**.

### Step 2.2: Establish Star Schema Relationships
1. Switch to **Model view** (third icon on the left rail).
2. If Power BI created automatic relationships, right-click and delete them.
3. Wire the following **8 active, 1-to-many (`1:*`), single-direction** relationships by dragging the primary key column from the dimension to the foreign key column in the fact table:
   1. `dim_date[date_key]` $\rightarrow$ `fact_bookings[arrival_date]`
   2. `dim_date[date_key]` $\rightarrow$ `fact_stay_nights[stay_date]`
   3. `dim_date[date_key]` $\rightarrow$ `fact_capacity[date_key]`
   4. `dim_hotel[hotel_key]` $\rightarrow$ `fact_bookings[hotel_key]`
   5. `dim_hotel[hotel_key]` $\rightarrow$ `fact_stay_nights[hotel_key]`
   6. `dim_hotel[hotel_key]` $\rightarrow$ `fact_capacity[hotel_key]`
   7. `dim_profile[profile_key]` $\rightarrow$ `fact_bookings[profile_key]`
   8. `dim_profile[profile_key]` $\rightarrow$ `fact_stay_nights[profile_key]`
4. Double-click each relationship line to verify:
   - **Cardinality**: `One to many (1:*)`
   - **Cross filter direction**: `Single`
   - **Make this relationship active**: Checked $\checkmark$

### Step 2.3: Mark `dim_date` as the Official Date Table
1. In the **Data** pane on the right, right-click `dim_date`.
2. Select **Mark as date table > Mark as date table**.
3. In the dialog, select **`date_key`** from the dropdown.
4. Verify the green validation checkmark ("Validated successfully") and click **OK**.

### Step 2.4: Set Sort-By Columns
In Data view, select each column listed below, click the **Column tools** tab on the top ribbon, click **Sort by column**, and choose the specified sort column:
1. Table `dim_date` $\rightarrow$ column `month_name` $\rightarrow$ Sort by: **`month_num`**
2. Table `dim_date` $\rightarrow$ column `month_short` $\rightarrow$ Sort by: **`month_num`**
3. Table `dim_date` $\rightarrow$ column `year_month` $\rightarrow$ Sort by: **`month_start`**
4. Table `fact_bookings` $\rightarrow$ column `lead_bucket` $\rightarrow$ Sort by: **`lead_bucket_order`**
5. Table `fact_bookings` $\rightarrow$ column `cancel_timing_bucket` $\rightarrow$ Sort by: **`cancel_timing_order`**

### Step 2.5: Hide Surrogate & Technical Keys from Report View
In Model view, multi-select (or right-click individually) and toggle **Is hidden** = `Yes` for:
- `dim_date`: `month_num`
- `dim_hotel`: `hotel_key`
- `dim_profile`: `profile_key`
- `fact_bookings`: `booking_id`, `hotel_key`, `profile_key`, `arrival_date`, `is_canceled`, `is_no_show`, `adr`, `room_revenue`, `lead_bucket_order`, `cancel_timing_order`
- `fact_stay_nights`: `booking_id`, `hotel_key`, `profile_key`, `stay_date`, `adr`
- `fact_capacity`: `hotel_key`, `date_key`, `rooms_available`

> [!CHECK]
> **You should now see**:
> In Model view, a clean star schema with 3 dimension tables on top pointing downward to 3 fact tables below with clear `1` (top) and `*` (bottom) arrows. No lines exist between fact tables.

---

## 3. Phase 3: Dedicated Measures Table & Validation
*Estimated Time: 25 minutes*

In this step, you will create a dedicated `Measures` table and add all 26 DAX measures folder by folder, verifying each against [`powerbi/validation_expected.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/validation_expected.csv).

### Step 3.1: Create the `Measures` Table
1. On the **Home** ribbon, click **Enter Data**.
2. In the dialog box:
   - Change the table name at the bottom to: `Measures`
   - Leave `Column1` blank.
3. Click **Load**.

### Step 3.2: Create Measures Folder by Folder
For each measure below, click on table `Measures` in the Data pane, click **New measure** on the ribbon (or right-click `Measures` > New measure), paste the DAX formula from [`powerbi/measures.dax`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/measures.dax), press Enter, set the **Format**, and in Model view set the **Display folder**:

#### Folder: **`Bookings`**
1. `Bookings = COUNTROWS(fact_bookings)` $\rightarrow$ Format: `#,##0` $\rightarrow$ Folder: `Bookings`
2. `Cancelled Bookings = CALCULATE([Bookings], fact_bookings[is_canceled] = 1)` $\rightarrow$ Format: `#,##0` $\rightarrow$ Folder: `Bookings`
3. `Cancellations (Canceled status) = CALCULATE([Bookings], fact_bookings[reservation_status] = "Canceled")` $\rightarrow$ Format: `#,##0` $\rightarrow$ Folder: `Bookings`
4. `No-Shows = CALCULATE([Bookings], fact_bookings[is_no_show] = 1)` $\rightarrow$ Format: `#,##0` $\rightarrow$ Folder: `Bookings`
5. `Cancel Rate % = DIVIDE([Cancelled Bookings], [Bookings])` $\rightarrow$ Format: `0.0%` $\rightarrow$ Folder: `Bookings`
6. `No-Show Rate % = DIVIDE([No-Shows], [Bookings])` $\rightarrow$ Format: `0.0%` $\rightarrow$ Folder: `Bookings`
7. `Stay Conversion % = DIVIDE(CALCULATE([Bookings], fact_bookings[is_canceled] = 0), [Bookings])` $\rightarrow$ Format: `0.0%` $\rightarrow$ Folder: `Bookings`
8. `Avg Lead Time = AVERAGE(fact_bookings[lead_time])` $\rightarrow$ Format: `0.0` $\rightarrow$ Folder: `Bookings`
9. `Avg Days Cancelled Before Arrival = AVERAGE(fact_bookings[days_cancelled_before_arrival])` $\rightarrow$ Format: `0.0` $\rightarrow$ Folder: `Bookings`
10. `Room Type Mismatch % = DIVIDE(CALCULATE([Bookings], fact_bookings[is_canceled] = 0, fact_bookings[room_type_mismatch] = 1), CALCULATE([Bookings], fact_bookings[is_canceled] = 0))` $\rightarrow$ Format: `0.0%` $\rightarrow$ Folder: `Bookings`

> [!CHECK]
> **Folder Validation Check (Bookings)**: Drop `[Bookings]`, `[Cancelled Bookings]`, `[Cancel Rate %]`, and `[Avg Lead Time]` onto a blank canvas card. Verify against [`powerbi/validation_expected.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/validation_expected.csv):
> - `[Bookings]`: **119,388**
> - `[Cancelled Bookings]`: **44,223**
> - `[Cancel Rate %]`: **37.0%**
> - `[Avg Lead Time]`: **104.0**

#### Folder: **`Stay-night KPIs`**
11. `Room Nights Sold = COUNTROWS(fact_stay_nights)` $\rightarrow$ Format: `#,##0` $\rightarrow$ Folder: `Stay-night KPIs`
12. `Room Revenue = SUM(fact_stay_nights[adr])` $\rightarrow$ Format: `#,##0.00` $\rightarrow$ Folder: `Stay-night KPIs`
13. `Room Nights Available = SUM(fact_capacity[rooms_available])` $\rightarrow$ Format: `#,##0` $\rightarrow$ Folder: `Stay-night KPIs`
14. `ADR = DIVIDE([Room Revenue], [Room Nights Sold])` $\rightarrow$ Format: `#,##0.00` $\rightarrow$ Folder: `Stay-night KPIs`
15. `Occupancy % = DIVIDE([Room Nights Sold], [Room Nights Available])` $\rightarrow$ Format: `0.0%` $\rightarrow$ Folder: `Stay-night KPIs`
16. `RevPAR = DIVIDE([Room Revenue], [Room Nights Available])` $\rightarrow$ Format: `#,##0.00` $\rightarrow$ Folder: `Stay-night KPIs`

> [!CHECK]
> **Folder Validation Check (Stay-night KPIs)**: Drop onto temporary cards and verify:
> - `[Room Nights Sold]`: **248,261**
> - `[Room Revenue]`: **$25,187,186.16**
> - `[ADR]`: **$101.45**
> - `[Occupancy %]`: **70.8%**
> - `[RevPAR]`: **$71.86**

#### Folder: **`Shares and trends`**
17. `Revenue Share % = DIVIDE([Room Revenue], CALCULATE([Room Revenue], ALLSELECTED(dim_profile)))` $\rightarrow$ Format: `0.0%` $\rightarrow$ Folder: `Shares and trends`
18. `Room Night Share % = DIVIDE([Room Nights Sold], CALCULATE([Room Nights Sold], ALLSELECTED(dim_profile)))` $\rightarrow$ Format: `0.0%` $\rightarrow$ Folder: `Shares and trends`
19. `Revenue Prior Month = CALCULATE([Room Revenue], DATEADD(dim_date[date_key], -1, MONTH))` $\rightarrow$ Format: `#,##0.00` $\rightarrow$ Folder: `Shares and trends`
20. `Revenue MoM % = DIVIDE([Room Revenue] - [Revenue Prior Month], [Revenue Prior Month])` $\rightarrow$ Format: `0.0%` $\rightarrow$ Folder: `Shares and trends`
21. `RevPAR Prior Year = CALCULATE([RevPAR], SAMEPERIODLASTYEAR(dim_date[date_key]))` $\rightarrow$ Format: `#,##0.00` $\rightarrow$ Folder: `Shares and trends`
22. `RevPAR YoY % = DIVIDE([RevPAR] - [RevPAR Prior Year], [RevPAR Prior Year])` $\rightarrow$ Format: `0.0%` $\rightarrow$ Folder: `Shares and trends`
23. `Underperformer Flag`: paste formula from [`measures.dax`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/measures.dax) $\rightarrow$ Format: `0` $\rightarrow$ Folder: `Shares and trends`

#### Folder: **`Assumptions`**
24. `Capacity Text = CONCATENATEX(dim_hotel, dim_hotel[hotel] & ": " & FORMAT(dim_hotel[rooms_capacity], "#,##0") & " rooms", " | ", dim_hotel[hotel], ASC)` $\rightarrow$ Format: `Text` $\rightarrow$ Folder: `Assumptions`
25. `Window Start = MIN(fact_capacity[date_key])` $\rightarrow$ Format: `yyyy-mm-dd` $\rightarrow$ Folder: `Assumptions`
26. `Window End = MAX(fact_capacity[date_key])` $\rightarrow$ Format: `yyyy-mm-dd` $\rightarrow$ Folder: `Assumptions`

### Step 3.3: Delete `Column1` from `Measures` Table
1. In the Data pane, right-click `Column1` in table `Measures` and select **Delete from model**.
2. Confirm the deletion.
3. Collapse and re-expand the Data pane: `Measures` now moves to the very top with a calculator icon ⊞.

---

## 4. Phase 4: Import Custom Report Theme
*Estimated Time: 5 minutes*

1. In Power BI Desktop, click the **View** tab on the top ribbon.
2. In the **Themes** section, click the dropdown arrow to expand the gallery.
3. Select **Browse for themes...**
4. Browse to [`powerbi/theme/hotel_theme.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/theme/hotel_theme.json) and click **Open**.
5. Power BI displays a confirmation dialog: *"Theme imported successfully"*.

> [!CHECK]
> **You should now see**:
> All default visual titles, font styles (Segoe UI), and colors update automatically. City Hotel defaults to Deep Navy (`#1A365D`) and Resort Hotel to Terracotta Amber (`#C05621`).

---

## 5. Phase 5: Visual-by-Visual Canvas Construction
*Estimated Time: 60 minutes*

Follow the exact visual layout and coordinates specified in [`powerbi/REPORT_SPEC.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/REPORT_SPEC.md).

For every visual:
- Click the specified visual icon in the **Visualizations** pane.
- Drag the required fields into the field wells.
- Go to **Format visual > General > Properties**:
  - Set **Width** and **Height**.
  - Expand **Position** and set **Horizontal (X)** and **Vertical (Y)**.
- Set title and formatting under **Format visual > General > Title**.

---

### Page 1: Executive Overview
Rename the first page tab to: `Executive Overview`.

#### Header Band & Slicers Strip
1. **Title Text Box**: `x: 20`, `y: 10`, `w: 1240`, `h: 60`.
   - Text: `Hotel Revenue & Operations Analytics | Executive Overview` (Font: Segoe UI, 20pt, Bold, `#1A365D`).
   - Subtitle: `Portfolio Performance & Diagnostic Intelligence` (11pt, `#718096`).
2. **Slicer S1 (Hotel)**: Dropdown Slicer $\rightarrow$ Field: `dim_hotel[hotel]` $\rightarrow$ `x: 20`, `y: 80`, `w: 220`, `h: 50`.
3. **Slicer S2 (Year)**: Tile Slicer $\rightarrow$ Field: `dim_date[year]` $\rightarrow$ `x: 260`, `y: 80`, `w: 320`, `h: 50`.
4. **Slicer S3 (Market Segment)**: Dropdown Slicer $\rightarrow$ Field: `dim_profile[market_segment]` $\rightarrow$ `x: 600`, `y: 80`, `w: 320`, `h: 50`.
5. **Slicer S4 (Distribution Channel)**: Dropdown Slicer $\rightarrow$ Field: `dim_profile[distribution_channel]` $\rightarrow$ `x: 940`, `y: 80`, `w: 320`, `h: 50`.

#### Headline KPI Cards (`y: 140`, `h: 90`, each `w: 195`)
6. **Card P1.1 (Occupancy %)**: Card visual $\rightarrow$ Field: `[Occupancy %]` $\rightarrow$ `x: 20`, `y: 140`, `w: 195`, `h: 90`. Title: "Occupancy % (Stay-night basis)".
7. **Card P1.2 (ADR)**: Card visual $\rightarrow$ Field: `[ADR]` $\rightarrow$ `x: 229`, `y: 140`, `w: 195`, `h: 90`. Title: "ADR (Stay-night basis)".
8. **Card P1.3 (RevPAR)**: Card visual $\rightarrow$ Field: `[RevPAR]` $\rightarrow$ `x: 438`, `y: 140`, `w: 195`, `h: 90`. Title: "RevPAR (Stay-night basis)".
9. **Card P1.4 (Cancel Rate %)**: Card visual $\rightarrow$ Field: `[Cancel Rate %]` $\rightarrow$ `x: 647`, `y: 140`, `w: 195`, `h: 90`. Title: "Cancel Rate % (Arrival cohort)".
10. **Card P1.5 (Avg Lead Time)**: Card visual $\rightarrow$ Field: `[Avg Lead Time]` $\rightarrow$ `x: 856`, `y: 140`, `w: 195`, `h: 90`. Title: "Avg Lead Time (Days)".
11. **Card P1.6 (Stay Conversion %)**: Card visual $\rightarrow$ Field: `[Stay Conversion %]` $\rightarrow$ `x: 1065`, `y: 140`, `w: 195`, `h: 90`. Title: "Stay Conversion % (Proxy)".

#### Charts & Assumption Banner
12. **Line Chart P1.7 (RevPAR Trend)**:
    - Click **Line chart** $\rightarrow$ `x: 20`, `y: 240`, `w: 610`, `h: 420`.
    - **X-axis**: `dim_date[year_month]`.
    - **Legend**: `dim_hotel[hotel]`.
    - **Y-axis**: `[RevPAR]`.
    - **Title**: "How does monthly RevPAR compare between City and Resort properties?"
13. **Combo Chart P1.8 (Bookings & Cancel Rate Pace)**:
    - Click **Line and clustered column chart** $\rightarrow$ `x: 650`, `y: 240`, `w: 610`, `h: 420`.
    - **Shared X-axis**: `dim_date[year_month]`.
    - **Column values**: `[Bookings]`.
    - **Line values**: `[Cancel Rate %]`.
    - **Title**: "How do monthly booking volume and cancellation rates correlate over time?"
14. **Banner Card P1.9**:
    - Multi-row Card $\rightarrow$ `x: 20`, `y: 670`, `w: 1240`, `h: 40`.
    - **Fields**: `[Capacity Text]`, `[Window Start]`, `[Window End]`.

---

### Page 2: Revenue and Segments
Create a new page and rename tab to: `Revenue and Segments`.

1. Copy the **Header Band** and the **Slicer Strip (S1–S4)** from Page 1 and paste onto Page 2. (Click "Sync" when prompted).
2. **Bar Chart P2.1 (ADR by Segment)**:
   - Click **Clustered bar chart** $\rightarrow$ `x: 20`, `y: 140`, `w: 610`, `h: 270`.
   - **Y-axis**: `dim_profile[market_segment]`.
   - **X-axis**: `[ADR]`.
   - **Title**: "Which market segments command the highest room rates?"
   - **Sort**: Click `...` on visual $\rightarrow$ Sort by `ADR` $\rightarrow$ Sort descending.
3. **Treemap P2.2 (Revenue Share %)**:
   - Click **Treemap** $\rightarrow$ `x: 650`, `y: 140`, `w: 610`, `h: 270`.
   - **Category**: `dim_profile[market_segment]`.
   - **Values**: `[Revenue Share %]`.
   - **Title**: "How is room revenue distributed across market segments?"
4. **Matrix P2.3 (Performance Matrix)**:
   - Click **Matrix** $\rightarrow$ `x: 20`, `y: 420`, `w: 740`, `h: 285`.
   - **Rows**: `dim_hotel[hotel]`, `dim_profile[market_segment]`.
   - **Values**: `[Bookings]`, `[Room Nights Sold]`, `[ADR]`, `[Revenue Share %]`, `[Cancel Rate %]`, `[Underperformer Flag]`.
   - **Title**: "Which property and segment combinations underperform commercial benchmarks?"
   - **Conditional Formatting**:
     - In Values well, click down arrow on `Cancel Rate %` $\rightarrow$ **Conditional formatting > Background color**.
     - Format style: **Rules**.
     - Based on field: `Measures[Underperformer Flag]`.
     - Rule: `If value = 1 (number) then #FED7D7 (Soft Red)`.
5. **Line Chart P2.4 (ADR Seasonality)**:
   - Click **Line chart** $\rightarrow$ `x: 780`, `y: 420`, `w: 480`, `h: 285`.
   - **X-axis**: `dim_date[month_short]`.
   - **Legend**: `dim_hotel[hotel]`.
   - **Y-axis**: `[ADR]`.
   - **Title**: "How do room rates fluctuate across calendar months?"

---

### Page 3: Cancellations Diagnostic
Create a new page and rename tab to: `Cancellation Diagnostic`.

1. Copy the **Header Band** and the **Slicer Strip (S1–S4)** from Page 1 and paste onto Page 3. (Click "Sync" when prompted).
2. **Column Chart P3.1 (Cancel Rate by Lead Bucket)**:
   - Click **Clustered column chart** $\rightarrow$ `x: 20`, `y: 140`, `w: 390`, `h: 270`.
   - **X-axis**: `fact_bookings[lead_bucket]`.
   - **Y-axis**: `[Cancel Rate %]`.
   - **Title**: "Which lead time windows carry the highest cancellation risk?"
3. **Column Chart P3.2 (Cancellations by Timing Bucket)**:
   - Click **Clustered column chart** $\rightarrow$ `x: 20`, `y: 420`, `w: 390`, `h: 285`.
   - **X-axis**: `fact_bookings[cancel_timing_bucket]`.
   - **Y-axis**: `[Cancelled Bookings]`.
   - **Title**: "How close to arrival do guests cancel their reservations?"
4. **Bar Charts P3.3 to P3.5 (Attribute Attrition)** (`x: 430`, `w: 380`):
   - **P3.3 (Deposit Type)** (`y: 140`, `h: 175`): Y = `dim_profile[deposit_type]`, X = `[Cancel Rate %]`. Title: "Deposit Policy Attrition".
   - **P3.4 (Market Segment)** (`y: 325`, `h: 185`): Y = `dim_profile[market_segment]`, X = `[Cancel Rate %]`. Title: "Market Segment Attrition".
   - **P3.5 (Customer Type)** (`y: 520`, `h: 185`): Y = `dim_profile[customer_type]`, X = `[Cancel Rate %]`. Title: "Customer Type Attrition".
5. **Decomposition Tree P3.6**:
   - Click **Decomposition tree** $\rightarrow$ `x: 830`, `y: 140`, `w: 430`, `h: 565`.
   - **Analyze**: `[Cancel Rate %]`.
   - **Explain by**: `fact_bookings[lead_bucket]`, `dim_profile[deposit_type]`, `dim_profile[market_segment]`, `dim_profile[customer_type]`, `fact_bookings[country]`, `dim_hotel[hotel]`.
   - **Title**: "What root factors explain our reservation cancellations?"

---

### Page 4: Insights and Assumptions
Create a new page and rename tab to: `Insights & Model Governance`.

1. **Header Scope Card P4.1**: `x: 20`, `y: 80`, `w: 1240`, `h: 45`. Fields: `[Capacity Text]`, `[Window Start]`, `[Window End]`.
2. **Text Box P4.2 (Key Findings)**: `x: 20`, `y: 135`, `w: 600`, `h: 340`. Paste Section 3 from [`powerbi/DASHBOARD_TEXT.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/DASHBOARD_TEXT.md).
3. **Text Box P4.3 (Core Definitions)**: `x: 640`, `y: 135`, `w: 620`, `h: 340`. Paste Section 4 from [`powerbi/DASHBOARD_TEXT.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/DASHBOARD_TEXT.md).
4. **Text Box P4.4 (Assumptions & Limitations)**: `x: 20`, `y: 485`, `w: 600`, `h: 220`. Paste Section 5 from [`powerbi/DASHBOARD_TEXT.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/DASHBOARD_TEXT.md).
5. **Text Box P4.5 (Architecture)**: `x: 640`, `y: 485`, `w: 620`, `h: 220`. Paste Section 6 from [`powerbi/DASHBOARD_TEXT.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/DASHBOARD_TEXT.md).

---

### Supporting Page A: Segment Detail (Drill-Through)
Create a new page and rename tab to: `Segment Detail`.

1. **Configure Drill-Through**:
   - In the Visualizations pane under **Drill-through filters**, drag **`dim_profile[market_segment]`** into **Add drill-through fields here**.
   - Power BI will automatically place a **Back button** ($\leftarrow$) in the top-left corner (`x: 20`, `y: 15`, `w: 40`, `h: 40`).
2. **KPI Cards Row (`y: 80`, `h: 90`, each `w: 295`)**:
   - `SA.1`: `[Bookings]` (`x: 20`)
   - `SA.2`: `[Cancel Rate %]` (`x: 335`)
   - `SA.3`: `[ADR]` (`x: 650`)
   - `SA.4`: `[Room Nights Sold]` (`x: 965`)
3. **Trend Chart SA.5**:
   - Line and clustered column chart $\rightarrow$ `x: 20`, `y: 185`, `w: 750`, `h: 515`.
   - **X-axis**: `dim_date[year_month]`.
   - **Column values**: `[Room Nights Sold]`.
   - **Line values**: `[ADR]`.
   - **Legend**: `dim_hotel[hotel]`.
4. **Top 10 Origin Countries Table SA.6**:
   - Table $\rightarrow$ `x: 790`, `y: 185`, `w: 470`, `h: 515`.
   - **Columns**: `fact_bookings[country]`, `[Bookings]`, `[Cancel Rate %]`, `[ADR]`, `[Room Revenue]`.
   - **Filters**: In Filters pane on visual $\rightarrow$ `country` $\rightarrow$ Filter type: **Top N** $\rightarrow$ Show items: **Top 10** $\rightarrow$ By value: `[Bookings]` $\rightarrow$ Click **Apply filter**.
   - **Sort**: Click header `Bookings` to sort descending.

---

### Supporting Page B: KPI Tooltip (Tooltip Canvas)
Create a new page and rename tab to: `KPI Tooltip`.

1. **Configure Canvas as Tooltip**:
   - Click on the empty canvas background.
   - In Visualizations pane, go to **Format page > Page information**:
     - Turn **Allow use as tooltip** = **On** $\checkmark$.
   - Go to **Format page > Canvas settings**:
     - Type: **Custom**
     - Width: **320 px**
     - Height: **240 px**
2. **Build Tooltip Cards**:
   - **Card SB.1**: Card $\rightarrow$ Field: `dim_profile[market_segment]` (or category) $\rightarrow$ `x: 10`, `y: 10`, `w: 300`, `h: 35`.
   - **Card SB.2**: Card $\rightarrow$ Field: `[Bookings]` $\rightarrow$ `x: 10`, `y: 50`, `w: 300`, `h: 55`.
   - **Card SB.3**: Card $\rightarrow$ Field: `[Cancel Rate %]` $\rightarrow$ `x: 10`, `y: 110`, `w: 300`, `h: 55`.
   - **Card SB.4**: Card $\rightarrow$ Field: `[ADR]` $\rightarrow$ `x: 10`, `y: 170`, `w: 300`, `h: 55`.
3. **Link Tooltip to Visuals**:
   - Return to Page 2. Select visual P2.1 (ADR Bar Chart).
   - In Visualizations pane, go to **Format visual > General > Tooltips**.
   - Type: **Report page** $\rightarrow$ Page: **`KPI Tooltip`**.

---

## 6. Phase 6: Slicer Synchronization, Tooltips & Interactions
*Estimated Time: 10 minutes*

### Step 6.1: Verify Slicer Syncing Across Pages 1 to 3
1. Click **View > Sync slicers** to open the Sync Slicers pane.
2. Select Slicer `S1 (Hotel)` on Page 1.
3. In the Sync Slicers pane, ensure the checkboxes for **Sync** ($\checkmark$) and **Visible** ($\checkmark$) are checked for:
   - `Executive Overview`
   - `Revenue and Segments`
   - `Cancellation Diagnostic`
4. Repeat for slicers `S2 (Year)`, `S3 (Market Segment)`, and `S4 (Distribution Channel)`.

### Step 6.2: Disable Cross-Filtering from Decomposition Tree
1. Navigate to **Page 3 (Cancellation Diagnostic)**.
2. Click on the Decomposition Tree visual (`P3.6`).
3. On the top ribbon, click **Format > Edit interactions**.
4. Power BI displays interaction icons (filter vs none $\oslash$) above every other visual on Page 3.
5. Above visuals **P3.1, P3.2, P3.3, P3.4, and P3.5**, click the **None** icon ($\oslash$).
6. Click **Format > Edit interactions** again to turn off interaction editing.

---

## 7. Phase 7: Final Polish, Accessibility & Saving
*Estimated Time: 10 minutes*

### Step 7.1: Verify Tab Order for Keyboard Accessibility
1. On each page, go to **View > Selection**.
2. At the top of the Selection pane, click **Tab order**.
3. Verify that the tab sequence flows logically from top to bottom:
   - Slicers (`S1`, `S2`, `S3`, `S4`) first.
   - Headline KPI cards (`P1.1` to `P1.6`) second.
   - Charts and matrices (`P1.7`, `P1.8`) third.
   - Footnote banner (`P1.9`) last.

### Step 7.2: Set Alt Text on Visuals
1. For every visual, select the visual, navigate to **Format visual > General > Alt text**, and paste the descriptive sentence from Section 2 of [`powerbi/DASHBOARD_TEXT.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/DASHBOARD_TEXT.md).

### Step 7.3: Set Default Opening View & Save
1. Navigate to tab **`Executive Overview`** (ensuring no slicers are filtered, showing total portfolio baseline).
2. Click **File > Save As**.
3. Browse to the repository's `powerbi/` directory and save as:
   ```text
   powerbi/hotel_dashboard.pbix
   ```

---

## 8. Phase 8: PDF Export & Artifact Verification
*Estimated Time: 5 minutes*

1. With `hotel_dashboard.pbix` open, click **File > Export > Export to PDF**.
2. Save the resulting PDF file as:
   ```text
   powerbi/hotel_dashboard.pdf
   ```
3. Capture high-resolution screenshots of each page:
   - `reports/figures/pbi_01_executive_overview.png`
   - `reports/figures/pbi_02_revenue_segments.png`
   - `reports/figures/pbi_03_cancellations.png`
   - `reports/figures/pbi_04_insights.png`
   - `reports/figures/pbi_05_segment_drillthrough.png`

---

## 9. Troubleshooting: The 8 Most Common Issues

| # | Symptom | Root Cause | Exact Click-by-Click Resolution |
| :-: | :--- | :--- | :--- |
| **1** | **Blank Cards or `(Blank)` displayed on KPI cards** | Missing relationship between dimension and fact table, or active slicer filters out all rows. | In Model view, verify that active relationships exist between `dim_date[date_key]` and fact tables, and `dim_hotel[hotel_key]` and fact tables. Clear all canvas slicers by clicking the "Clear selections" eraser icon. |
| **2** | **Occupancy % is blank or displays above 100% (e.g. 300%)** | `dim_date[date_key]` was erroneously linked to `arrival_date` instead of `stay_date` on `fact_stay_nights`, or capacity dates are misaligned. | In Model view, double-click the relationship between `dim_date` and `fact_stay_nights`. Ensure the target column is strictly **`stay_date`** (not `booking_id` or `arrival_date`). Verify `fact_capacity` connects on **`date_key`**. |
| **3** | **Month axis sorted alphabetically (April, August, December...)** | The display column `month_name` or `month_short` lacks a Sort By Column assignment. | In Data view, click table `dim_date`, select column `month_name`, click ribbon tab **Column tools > Sort by column**, and select **`month_num`**. Repeat for `month_short`. |
| **4** | **Cancel Rate % displays as `0.37` instead of `37.0%`** | Measure formatting was omitted in DAX or defaulted to General Number. | In Data pane, click measure `[Cancel Rate %]`. On the **Measure tools** ribbon, click the percentage symbol `%` and set decimal places to `1`. Repeat for `Occupancy %` and `Stay Conversion %`. |
| **5** | **A slicer on Page 1 does not filter visuals on Page 2 or Page 3** | Slicer synchronization was not configured. | Click **View > Sync slicers**. Select the slicer on Page 1. In the Sync slicers pane, check both the **Sync** and **Visible** checkboxes for Pages 1, 2, and 3. |
| **6** | **Duplicated Years or Year hierarchies in date axis** | Power BI Auto Date/Time created a local date hierarchy, or a date hierarchy field was dragged instead of the raw date key. | Follow Step 2.1 to uncheck **File > Options > Current File > Data Load > Auto date/time**. On the visual axis well, click the field dropdown and switch from "Date Hierarchy" to the explicit column name `year_month`. |
| **7** | **`DataFormat.Error: We couldn't convert to Number` on load** | Regional Windows settings use comma decimals, causing Power Query to fail on period-decimal CSVs, or CSV has empty text tokens. | Every query in [`powerbi/power_query/`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/) explicitly declares `"en-US"`. Ensure you copied the exact `.m` code. Run `python src/validate_powerbi_model.py` to confirm CSV integrity. |
| **8** | **Every row in a visual displays the exact same grand-total number** | Cross-filter direction is set incorrectly, or relationship direction flows from Fact to Dimension. | In Model view, check the relationship line between the dimension and fact table. The arrow **must point from the Dimension (1) to the Fact (*)**. Double-click the line and set **Cross filter direction** = `Single`. |
