# Step-by-Step Manual PivotTable Construction Guide

- **Target Workbook**: `excel/hotel_kpi_summary.xlsx`
- **Data Source**: Excel Table `tblBookings` (located on sheet `Data`, 119,388 rows, 25 columns)
- **Target Sheets**: `PT_Monthly`, `PT_Segment`, `PT_LeadTime`, `PT_Channel` (inserted at Cell `A3`)
- **Authoritative Benchmarks**: Computed in PostgreSQL and recorded in `excel/inputs/pivot_expected_values.csv`

---

## 1. Foundational Mathematical & Operational Principles

### 1.1 Why `Average of is_canceled` Exactly Equals Cancellation Rate
In standard spreadsheet modeling, cancellation rates are often computed via calculated fields or helper ratios. However, in `tblBookings`, the cancellation indicator `is_canceled` is strictly stored as a binary integer:
- `1` = Canceled or No-Show
- `0` = Stayed (Check-Out)

Mathematically, the sample average (arithmetic mean) of any binary indicator variable $x_i \in \{0, 1\}$ over a subset of size $N$ is:
$$\bar{x} = \frac{1}{N} \sum_{i=1}^N x_i = \frac{1 \times (\text{Count of } 1\text{s}) + 0 \times (\text{Count of } 0\text{s})}{N} = \frac{\text{Total Cancellations}}{\text{Total Bookings}} = \text{Cancellation Rate}$$

This equality holds **strictly because the column contains exclusively integer 0 and 1** (enforced by cleaning decisions D8 and D12). Summarizing `is_canceled` by **Average** in a PivotTable and applying the percentage number format (`0.0%`) produces the exact, mathematically flawless cancellation rate without requiring complex custom DAX or calculated items.

### 1.2 Shared Pivot Cache Architecture
Because all 4 PivotTables are built from the single master table `tblBookings`, Excel automatically creates a shared memory **Pivot Cache**. This ensures:
1. Minimal file size footprint (no duplicated data structures).
2. Universal synchronization when refreshing data via **Data > Refresh All** (`Ctrl+Alt+F5`).
3. Single-slicer multi-pivot cross-filtering across all 4 analytical sheets.

---

## 2. Standard Insertion & Layout Workflow

Follow these 5 setup steps for **every** PivotTable before customizing fields:

1. **Initiate PivotTable**:
   - Go to sheet `Data`, click any cell inside table `tblBookings` (e.g., cell `A2`).
   - On the Excel Ribbon, select **Insert > PivotTable** (or press `Alt + N + V + T`).
2. **Select Destination**:
   - In the *Create PivotTable* dialog, verify Table/Range is `tblBookings`.
   - Select **Existing Worksheet**.
   - In the *Location* box, navigate to the target tab (`PT_Monthly`, `PT_Segment`, `PT_LeadTime`, or `PT_Channel`), click cell **`A3`**, and click **OK**.
3. **Assign PivotTable Name**:
   - Click anywhere inside the new PivotTable.
   - On the ribbon, select **PivotTable Analyze** (or **PivotTable Tools > Analyze**).
   - On the far left, in the **PivotTable Name** text box, enter the designated name (e.g. `pvtMonthlyTrends`).
4. **Apply Institutional Design Standards**:
   - On the ribbon, go to **Design**:
     - **Report Layout**: Select **Show in Tabular Form**.
     - **Report Layout**: Select **Repeat All Item Labels** (optional, recommended for tabular slicing).
     - **Subtotals**: Select **Do Not Show Subtotals**.
     - **Grand Totals**: Select **On for Rows and Columns**.
     - **PivotTable Style**: Select **Pivot Style Medium 9** (Navy Blue) or **Pivot Style Medium 2**.
5. **Configure Value Field Settings**:
   - In the *PivotTable Fields* pane (right sidebar), click the small drop-down arrow next to a field in the **Values** quadrant > choose **Value Field Settings...**
   - Set the **Custom Name** and click **Number Format** to set currency, count, or percentage formats.

---

## 3. PivotTable 1: Monthly Booking Trends (`PT_Monthly`)

### 3.1 Specifications & Configuration
- **Target Sheet**: `PT_Monthly`
- **Starting Cell**: `A3`
- **PivotTable Name**: `pvtMonthlyTrends`
- **Source**: `tblBookings`

| Quadrant | Field Name | Grouping / Aggregation | Custom Caption | Number Format | Show Values As |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Filters** | *(None)* | — | — | — | — |
| **Columns** | `hotel` | Default (`City Hotel`, `Resort Hotel`) | `Hotel Property` | Text | Normal |
| **Rows** | `arrival_month_start` | Grouped by **Years & Months** | `Arrival Month` | `YYYY-MM` | Normal |
| **Values (1)** | `booking_id` | **Count** | `Bookings` | `#,##0` | No Calculation |
| **Values (2)** | `is_canceled` | **Average** | `Cancel Rate %` | `0.0%` | No Calculation |
| **Values (3)** | `Revenue_Realised` | **Sum** | `Realised Revenue` | `$#,##0` | No Calculation |

### 3.2 Step-by-Step Build Instructions
1. Navigate to sheet `PT_Monthly`, click cell `A3`, and insert PivotTable from `tblBookings`. Name it `pvtMonthlyTrends`.
2. Drag `hotel` to the **Columns** quadrant.
3. Drag `arrival_month_start` to the **Rows** quadrant.
   - *Date Grouping & Preventing Duplication*:
     - Excel automatically detects dates and frequently introduces synthetic fields named `Years` and `Quarters`.
     - Right-click any date in Column A > select **Group...**
     - In the Grouping dialog, ensure only **Months** and **Years** are highlighted in blue. Deselect *Quarters* and *Days*. Click **OK**.
     - If Excel adds an unwanted outer `Years` column header that separates the months, right-click the date > select **Ungroup**, and use the raw ISO dates (`2015-07-01`, `2015-08-01`, etc.) which already sort chronologically in tabular form.
4. Drag `booking_id` into **Values**:
   - Value Field Settings > Summarize by: **Count**.
   - Custom Name: `Bookings`. Number Format: `#,##0`.
5. Drag `is_canceled` into **Values**:
   - Value Field Settings > Summarize by: **Average**.
   - Custom Name: `Cancel Rate %`. Number Format: `0.0%`.
6. Drag `Revenue_Realised` into **Values**:
   - Value Field Settings > Summarize by: **Sum**.
   - Custom Name: `Realised Revenue`. Number Format: `$#,##0`.

### 3.3 Authoritative Verification Benchmarks (First 3 Months)
Cross-reference your generated PivotTable against `excel/inputs/pivot_expected_values.csv`:

```text
Arrival Month | Metric            | City Hotel   | Resort Hotel | Total Portfolio
---------------------------------------------------------------------------------
2015-07       | Bookings          | 1,398        | 1,378        | 2,776
2015-07       | Cancel Rate %     | 67.2%        | 23.2%        | 45.4%
2015-07       | Realised Revenue  | $79,646      | $678,694     | $758,340
---------------------------------------------------------------------------------
2015-08       | Bookings          | 2,480        | 1,409        | 3,889
2015-08       | Cancel Rate %     | 49.7%        | 26.0%        | 41.1%
2015-08       | Realised Revenue  | $285,197     | $852,455     | $1,137,653
---------------------------------------------------------------------------------
2015-09       | Bookings          | 3,529        | 1,585        | 5,114
2015-09       | Cancel Rate %     | 43.7%        | 34.8%        | 41.0%
2015-09       | Realised Revenue  | $588,545     | $466,076     | $1,054,621
```

---

## 4. PivotTable 2: Market Segment Performance (`PT_Segment`)

### 4.1 Specifications & Configuration
- **Target Sheet**: `PT_Segment`
- **Starting Cell**: `A3`
- **PivotTable Name**: `pvtMarketSegments`
- **Source**: `tblBookings`

| Quadrant | Field Name | Grouping / Aggregation | Custom Caption | Number Format | Show Values As |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Filters** | *(None)* | — | — | — | — |
| **Columns** | `hotel` | Default (`City Hotel`, `Resort Hotel`) | `Hotel Property` | Text | Normal |
| **Rows** | `market_segment` | Default (8 segments) | `Market Segment` | Text | Normal |
| **Values (1)** | `booking_id` | **Count** | `Bookings` | `#,##0` | No Calculation |
| **Values (2)** | `is_canceled` | **Average** | `Cancel Rate %` | `0.0%` | No Calculation |
| **Values (3)** | `Revenue_Realised` | **Sum** | `Realised Revenue` | `$#,##0` | No Calculation |
| **Values (4)** | `Revenue_Realised` *(2nd copy)* | **Sum** | `Revenue Share %` | `0.0%` | **% of Column Total** |

### 4.2 Step-by-Step Build Instructions
1. Navigate to sheet `PT_Segment`, click cell `A3`, and insert PivotTable from `tblBookings`. Name it `pvtMarketSegments`.
2. Drag `hotel` to **Columns**.
3. Drag `market_segment` to **Rows**.
4. Configure Values 1, 2, and 3:
   - `booking_id` $\rightarrow$ Count $\rightarrow$ Caption `Bookings`, Format `#,##0`.
   - `is_canceled` $\rightarrow$ Average $\rightarrow$ Caption `Cancel Rate %`, Format `0.0%`.
   - `Revenue_Realised` $\rightarrow$ Sum $\rightarrow$ Caption `Realised Revenue`, Format `$#,##0`.
5. **Add Revenue Share (% of Column Total)**:
   - Drag `Revenue_Realised` from the field list into the **Values** area a second time (placed below the first copy).
   - Click its drop-down > **Value Field Settings...**
   - In the *Summarize value field by* tab, confirm **Sum**.
   - In the **Custom Name** box, type `Revenue Share %`.
   - Click the **Show Values As** tab (second tab).
   - In the drop-down menu, select **% of Column Total**.
   - Click **Number Format** > select **Percentage** (`0.0%` or `0.00%`). Click **OK** twice.
6. Sort rows by `Bookings` descending: Right-click any cell in the `Bookings` column > **Sort > Sort Largest to Smallest**.

### 4.3 Authoritative Verification Benchmarks (Top 3 Segments)

```text
Market Segment | Metric           | City Hotel     | Resort Hotel   | Total Portfolio
-------------------------------------------------------------------------------------
Online TA      | Bookings         | 38,748         | 17,729         | 56,477
Online TA      | Cancel Rate %    | 37.4%          | 35.2%          | 36.7%
Online TA      | Realised Revenue | $8,762,544     | $4,951,858     | $13,714,401
Online TA      | Revenue Share %  | 60.9%          | 42.7%          | 52.8%
-------------------------------------------------------------------------------------
Offline TA/TO  | Bookings         | 16,746         | 7,472          | 24,218
Offline TA/TO  | Cancel Rate %    | 42.8%          | 15.2%          | 34.3%
Offline TA/TO  | Realised Revenue | $2,554,041     | $3,105,513     | $5,659,555
Offline TA/TO  | Revenue Share %  | 17.7%          | 26.8%          | 21.8%
-------------------------------------------------------------------------------------
Groups         | Bookings         | 13,975         | 5,835          | 19,810
Groups         | Cancel Rate %    | 68.9%          | 42.4%          | 61.1%
Groups         | Realised Revenue | $980,789       | $888,368       | $1,869,157
Groups         | Revenue Share %  | 6.8%           | 7.7%           | 7.2%
```

---

## 5. PivotTable 3: Lead Time Buckets (`PT_LeadTime`)

### 5.1 Specifications & Configuration
- **Target Sheet**: `PT_LeadTime`
- **Starting Cell**: `A3`
- **PivotTable Name**: `pvtLeadTime`
- **Source**: `tblBookings`

| Quadrant | Field Name | Grouping / Aggregation | Custom Caption | Number Format | Show Values As |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Filters** | *(None)* | — | — | — | — |
| **Columns** | `hotel` | Default (`City Hotel`, `Resort Hotel`) | `Hotel Property` | Text | Normal |
| **Rows** | `lead_bucket` | Ordered: `0-7`, `8-30`, `31-90`, `91-180`, `181+` | `Lead Time Bucket` | Text | Normal |
| **Values (1)** | `booking_id` | **Count** | `Bookings` | `#,##0` | No Calculation |
| **Values (2)** | `is_canceled` | **Average** | `Cancel Rate %` | `0.0%` | No Calculation |

### 5.2 Step-by-Step Build Instructions & Bucket Sorting
1. Navigate to sheet `PT_LeadTime`, click cell `A3`, and insert PivotTable from `tblBookings`. Name it `pvtLeadTime`.
2. Drag `hotel` to **Columns**.
3. Drag `lead_bucket` to **Rows**.
4. Configure Values:
   - `booking_id` $\rightarrow$ Count $\rightarrow$ Caption `Bookings`, Format `#,##0`.
   - `is_canceled` $\rightarrow$ Average $\rightarrow$ Caption `Cancel Rate %`, Format `0.0%`.
5. **Enforce Exact Chronological Bucket Order**:
   - By default, alphabetical sorting places `181+` before `31-90` (`0-7`, `181+`, `31-90`, `8-30`, `91-180`).
   - **Method A (Manual Drag & Drop - Recommended)**:
     1. Click on the cell labeled **`181+`** in Column A.
     2. Hover your mouse over the cell border until the cursor turns into a four-way arrow (`+` icon).
     3. Click and drag the cell downwards below `91-180`. Release the mouse.
     4. Click on the cell labeled **`8-30`**, hover over the border, and drag it upwards between `0-7` and `31-90`.
     5. Verify final sequence: **`0-7`**, **`8-30`**, **`31-90`**, **`91-180`**, **`181+`**.
   - **Method B (Using `lead_bucket_order`)**:
     1. Drag `lead_bucket_order` into Rows *above* `lead_bucket`.
     2. In **Design > Report Layout**, select **Tabular Form**.
     3. In **Design > Subtotals**, select **Do Not Show Subtotals**.
     4. The rows will sort 1 to 5 perfectly.

### 5.3 Authoritative Verification Benchmarks (First 3 Buckets)

```text
Lead Time Bucket | Metric        | City Hotel   | Resort Hotel | Total Portfolio
--------------------------------------------------------------------------------
0-7 days         | Bookings      | 10,808       | 8,938        | 19,746
0-7 days         | Cancel Rate % | 12.2%        | 6.5%         | 9.6%
--------------------------------------------------------------------------------
8-30 days        | Bookings      | 12,554       | 6,406        | 18,960
8-30 days        | Cancel Rate % | 30.9%        | 21.9%        | 27.9%
--------------------------------------------------------------------------------
31-90 days       | Bookings      | 20,796       | 8,756        | 29,552
31-90 days       | Cancel Rate % | 39.9%        | 32.5%        | 37.7%
```

---

## 6. PivotTable 4: Channel & Deposit Matrix (`PT_Channel`)

### 6.1 Specifications & Configuration
- **Target Sheet**: `PT_Channel`
- **Starting Cell**: `A3`
- **PivotTable Name**: `pvtDistributionChannels`
- **Source**: `tblBookings`

| Quadrant | Field Name | Grouping / Aggregation | Custom Caption | Number Format | Show Values As |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Filters** | *(None)* | — | — | — | — |
| **Columns** | `deposit_type` | Default (`No Deposit`, `Non Refund`, `Refundable`) | `Deposit Policy` | Text | Normal |
| **Rows** | `distribution_channel` | Default (`TA/TO`, `Direct`, `Corporate`, `GDS`, `Undefined`) | `Distribution Channel` | Text | Normal |
| **Values (1)** | `is_canceled` | **Average** | `Cancel Rate %` | `0.0%` | No Calculation |
| **Values (2)** | `booking_id` | **Count** | `Bookings` | `#,##0` | No Calculation |

### 6.2 Step-by-Step Build Instructions
1. Navigate to sheet `PT_Channel`, click cell `A3`, and insert PivotTable from `tblBookings`. Name it `pvtDistributionChannels`.
2. Drag `deposit_type` to **Columns**.
3. Drag `distribution_channel` to **Rows**.
4. Drag `is_canceled` into **Values**:
   - Value Field Settings > Summarize by: **Average**.
   - Custom Name: `Cancel Rate %`. Number Format: `0.0%`.
5. Drag `booking_id` into **Values**:
   - Value Field Settings > Summarize by: **Count**.
   - Custom Name: `Bookings`. Number Format: `#,##0`.

### 6.3 Authoritative Verification Benchmarks (Top 3 Channels)

```text
Distribution Channel | Deposit Type | Bookings | Cancel Rate %
--------------------------------------------------------------
TA/TO                | No Deposit   | 84,159   | 31.5%
TA/TO                | Non Refund   | 13,650   | 99.6%
TA/TO                | Refundable   | 60       | 41.7%
TA/TO                | Total        | 97,869   | 41.0%
--------------------------------------------------------------
Direct               | No Deposit   | 14,148   | 15.3%
Direct               | Non Refund   | 398      | 97.5%
Direct               | Refundable   | 98       | 10.2%
Direct               | Total        | 14,644   | 17.5%
--------------------------------------------------------------
Corporate            | No Deposit   | 6,135    | 15.7%
Corporate            | Non Refund   | 538      | 94.4%
Corporate            | Refundable   | 4        | 25.0%
Corporate            | Total        | 6,677    | 22.1%
```

---

## 7. Universal Slicer on `hotel` & Slicer Connections

To provide interactive executive filtering across all four PivotTables simultaneously from a single UI control:

### 7.1 Insert the Slicer
1. Click anywhere inside the first PivotTable on sheet `PT_Monthly`.
2. On the ribbon, go to **PivotTable Analyze > Insert Slicer** (or press `Alt + N + S + F`).
3. In the *Insert Slicers* dialog box, locate and check the checkbox for **`hotel`**.
4. Click **OK**.
5. A floating slicer card titled **hotel** will appear on the sheet with two buttons: `City Hotel` and `Resort Hotel`.

### 7.2 Connect the Slicer to All 4 PivotTables (Report Connections)
1. Right-click the header of the newly created `hotel` slicer.
2. Select **Report Connections...** (or click the slicer, go to ribbon tab **Slicer**, and click **Report Connections**).
3. The dialog displays all PivotTables sharing the `tblBookings` pivot cache. Check the boxes for all 4 tables:
   - [x] **`pvtMonthlyTrends`** (`PT_Monthly`)
   - [x] **`pvtMarketSegments`** (`PT_Segment`)
   - [x] **`pvtLeadTime`** (`PT_LeadTime`)
   - [x] **`pvtDistributionChannels`** (`PT_Channel`)
4. Click **OK**.

### 7.3 Operational Testing
- Click **`City Hotel`**:
  - `PT_Monthly` filters to City Hotel's 79,329 bookings and 41.7% cancel rate.
  - `PT_Segment` displays City Hotel's segment breakdown ($14.39M realized revenue).
  - `PT_LeadTime` updates to City Hotel's cancellation curve.
  - `PT_Channel` filters to City Hotel's distribution channels.
- Click **`Resort Hotel`**:
  - All 4 PivotTables instantly update to Resort Hotel's 40,059 bookings and 27.8% cancel rate.
- Click **Clear Filter** (icon in top right of slicer or `Alt + C`):
  - All 4 PivotTables instantly return to full portfolio totals (119,388 bookings, 37.0% cancel rate, $26.00M realized revenue).
- Copy the Slicer (`Ctrl+C`) and paste it (`Ctrl+V`) onto `PT_Segment`, `PT_LeadTime`, and `PT_Channel` so executive users have instant property toggles on every tab.

---

## 8. Master Reconciliation Audit Table

Confirm that your manual PivotTables reconcile to these database benchmark totals (from `excel/inputs/pivot_expected_values.csv`):

| Property Slice | Metric | Expected Benchmark | Excel Number Format |
| :--- | :--- | :---: | :---: |
| **City Hotel** | Total Bookings | `79,329` | `#,##0` |
| **City Hotel** | Overall Cancellation Rate | `41.73%` | `0.0%` / `0.00%` |
| **City Hotel** | Total Realised Revenue | `$14,394,410.18` | `$#,##0.00` |
| **Resort Hotel** | Total Bookings | `40,059` | `#,##0` |
| **Resort Hotel** | Overall Cancellation Rate | `27.76%` | `0.0%` / `0.00%` |
| **Resort Hotel** | Total Realised Revenue | `$11,601,914.03` | `$#,##0.00` |
| **Total Portfolio** | Total Bookings | `119,388` | `#,##0` |
| **Total Portfolio** | Overall Cancellation Rate | `37.04%` | `0.0%` / `0.00%` |
| **Total Portfolio** | Total Realised Revenue | `$25,996,324.21` | `$#,##0.00` |
