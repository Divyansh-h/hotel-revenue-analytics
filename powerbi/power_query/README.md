# Power BI Power Query M Scripts: Star Schema Ingestion

> [!NOTE]
> **Environment Disclaimer**: Power Query M cannot be executed directly in this non-desktop environment. All M scripts in this directory were generated dynamically from the real CSV headers in `powerbi/data/` via [`src/make_pbi_m_scripts.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/src/make_pbi_m_scripts.py) and validated for syntax, balanced delimiters, culture, and complete column typing via [`powerbi/power_query/test_m_scripts.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/test_m_scripts.py).

---

## 1. Architecture & Design Principles

1. **Centralized Parameterization**:
   All 6 star schema queries consume a single text parameter, `DataFolder`, defining the directory path containing the CSV files. Moving the project to another machine or folder only requires updating this single parameter.

2. **Zero-Drift Ingestion**:
   Every column in every CSV header is explicitly typed using `Table.TransformColumnTypes(..., "en-US")`. No columns are left untyped, and no columns are omitted.

3. **DAX Separation of Concerns**:
   No calculated columns, filters, or aggregations exist in Power Query. Power Query functions purely as an extraction and typing layer; all business measures, rates, and KPIs (e.g., Occupancy %, RevPAR, ADR, Cancel Rate) belong in DAX.

---

## 2. Query Inventory

| Query Name | M Script File | Source CSV File | Columns | Primary Key / Grain |
| :--- | :--- | :--- | :---: | :--- |
| `DataFolder` | [`parameters.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/parameters.m) | *N/A (Parameter)* | — | Directory path ending with `/` or `\` |
| `dim_date` | [`dim_date.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/dim_date.m) | `dim_date.csv` | 8 | `date_key` (Daily calendar 2015–2017) |
| `dim_hotel` | [`dim_hotel.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/dim_hotel.m) | `dim_hotel.csv` | 3 | `hotel_key` (City Hotel, Resort Hotel) |
| `dim_profile` | [`dim_profile.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/dim_profile.m) | `dim_profile.csv` | 5 | `profile_key` (Junk dimension combinations) |
| `fact_bookings` | [`fact_bookings.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/fact_bookings.m) | `fact_bookings.csv` | 24 | `booking_id` (1 row per booking) |
| `fact_stay_nights` | [`fact_stay_nights.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/fact_stay_nights.m) | `fact_stay_nights.csv` | 5 | `(booking_id, stay_date)` (1 row per stay-night) |
| `fact_capacity` | [`fact_capacity.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/fact_capacity.m) | `fact_capacity.csv` | 3 | `(hotel_key, date_key)` (Daily available rooms) |

---

## 3. Step-by-Step Setup Guide in Power BI Desktop

Follow these exact steps to assemble the data model in Power BI Desktop:

### Step 1: Open Power Query Editor
1. Launch **Power BI Desktop**.
2. On the **Home** ribbon, click **Transform Data** (opens Power Query Editor).

### Step 2: Create the `DataFolder` Parameter
1. In Power Query Editor, go to **Home > New Source > Blank Query**.
2. Click **Home > Advanced Editor** (or **View > Advanced Editor**).
3. Select all text in the editor window and replace it with the contents of [`parameters.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/parameters.m):
   ```powerquery
   "/Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/data/" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
   ```
4. Click **Done**.
5. In the **Query Settings** pane on the right, under **Properties**, change the **Name** to:
   ```text
   DataFolder
   ```
   > [!IMPORTANT]
   > Update the string value to match the exact local folder path where your CSV files are saved. Always ensure there is a **trailing path separator** (`/` on macOS/Linux or `\` on Windows).

### Step 3: Create the 6 Star Schema Table Queries
For each of the 6 tables below, repeat these steps:
1. Click **Home > New Source > Blank Query**.
2. Click **Advanced Editor**.
3. Replace the entire code block with the contents of the corresponding `.m` script file.
4. Click **Done**.
5. In the **Query Settings** pane on the right, rename the query to the exact **Query Name** specified below:

| # | Script File | Target Query Name |
| :-: | :--- | :--- |
| 1 | [`dim_date.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/dim_date.m) | `dim_date` |
| 2 | [`dim_hotel.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/dim_hotel.m) | `dim_hotel` |
| 3 | [`dim_profile.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/dim_profile.m) | `dim_profile` |
| 4 | [`fact_bookings.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/fact_bookings.m) | `fact_bookings` |
| 5 | [`fact_stay_nights.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/fact_stay_nights.m) | `fact_stay_nights` |
| 6 | [`fact_capacity.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/fact_capacity.m) | `fact_capacity` |

### Step 4: Load Data into the Model
1. Check that each table preview shows the headers and populated data rows.
2. Click **Home > Close & Apply**.
3. Power BI will read the CSV files and load the 6 tables into memory.

---

## 4. Star Schema Relationship Wiring

Once loaded, navigate to the **Model View** in Power BI Desktop and confirm or wire the following 1-to-many (`1:*`), single-direction cross-filter relationships:

```mermaid
erDiagram
    dim_hotel ||--o{ fact_bookings : "hotel_key"
    dim_hotel ||--o{ fact_stay_nights : "hotel_key"
    dim_hotel ||--o{ fact_capacity : "hotel_key"
    dim_profile ||--o{ fact_bookings : "profile_key"
    dim_profile ||--o{ fact_stay_nights : "profile_key"
    dim_date ||--o{ fact_bookings : "date_key = arrival_date"
    dim_date ||--o{ fact_stay_nights : "date_key = stay_date"
    dim_date ||--o{ fact_capacity : "date_key = date_key"
```

---

## 5. Troubleshooting Guide

### 1. Wrong Folder Path / File Not Found
- **Symptom**: `DataSource.Error: Could not find a part of the path...` or `File.Contents` error.
- **Cause**: The `DataFolder` parameter value does not point to the actual folder containing the CSV files, or the trailing path separator was omitted.
- **Resolution**:
  1. Select the `DataFolder` query in the left-hand Queries list.
  2. In the formula bar or current value box, enter the full path to `powerbi/data/`.
  3. Ensure it ends with `/` (macOS/Linux) or `\` (Windows), for example:
     `C:\Projects\hotel-revenue-analytics\powerbi\data\`

### 2. Culture / Regional Format Issues
- **Symptom**: Decimals parsed as whole numbers (e.g. `100.50` becomes `10050` in comma-decimal locales) or date conversion errors.
- **Cause**: Windows or Power BI Desktop locale uses European/comma decimal separators.
- **Resolution**:
  All M scripts in this project explicitly pass `"en-US"` to `Table.TransformColumnTypes(..., "en-US")`. This forces Power Query to interpret `.` as the decimal separator and parse ISO `YYYY-MM-DD` strings into valid calendar dates regardless of the machine's locale. **Do not remove the `"en-US"` argument.**

### 3. DataFormat.Error on Type Transformation
- **Symptom**: `DataFormat.Error: We couldn't convert to Number` or `DataFormat.Error: We couldn't parse the input provided as a Date value`.
- **Cause**: Corrupted CSV export, text tokens (e.g., `'nan'` or `'null'`), or drift in CSV headers.
- **Resolution**:
  1. In the repository root, run the authoritative validator:
     ```bash
     python src/validate_powerbi_model.py
     ```
  2. If any check fails, re-export the CSVs directly from PostgreSQL:
     ```bash
     python src/export_powerbi_model.py
     python src/validate_powerbi_model.py
     ```
  3. Empty cells (`""`) in integer columns like `days_cancelled_before_arrival` automatically transform to native Power Query `null` values without error.

### 4. Formula Firewall / Privacy Levels Warning
- **Symptom**: `Formula.Firewall: Query references other queries or steps, so it may not access a data source directly...`
- **Cause**: Power BI checking privacy boundaries between the `DataFolder` parameter and the `File.Contents` connector.
- **Resolution**:
  In Power BI Desktop:
  1. Go to **File > Options and settings > Options**.
  2. Under **Current File**, select **Privacy**.
  3. Check **Ignore the Privacy Levels and potentially improve performance**.
  4. Click **OK** and click **Refresh**.
