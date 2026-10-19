# Phase 4 Sign-off Document: Power BI Star Schema, DAX Suite & Dashboard Specifications

## 1. Phase 4 Deliverables Inventory

Phase 4 delivers the complete, self-contained architecture required to assemble, validate, and maintain the enterprise Power BI reporting application (`hotel_revenue_analytics.pbix`).

### A. Data Mart & Star Schema Layer
| File | Description | Metrics / Grain |
| :--- | :--- | :--- |
| [`sql/70_powerbi_model.sql`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/sql/70_powerbi_model.sql) | DDL & ETL script in schema `hotel` constructing star schema tables. | 6 relational tables (`dim_date`, `dim_hotel`, `dim_profile`, `fact_bookings`, `fact_stay_nights`, `fact_capacity`). |
| [`src/export_powerbi_model.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/src/export_powerbi_model.py) | Python exporter generating UTF-8 CSV extracts with ISO dates and integer flags. | Exports all 6 tables to `powerbi/data/`. |
| [`powerbi/data/dim_date.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/data/dim_date.csv) | Calendar dimension covering 2015-01-01 to 2017-12-31. | 1,096 rows, 8 columns (`date_key` PK). |
| [`powerbi/data/dim_hotel.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/data/dim_hotel.csv) | Property dimension with physical capacity (City: 250, Resort: 210). | 2 rows, 3 columns (`hotel_key` PK). |
| [`powerbi/data/dim_profile.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/data/dim_profile.csv) | Conforming guest profile junk dimension (segment, channel, customer type, deposit). | 101 rows, 5 columns (`profile_key` PK). |
| [`powerbi/data/fact_bookings.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/data/fact_bookings.csv) | Transactional booking cohort fact table (evaluated on arrival date). | 119,388 rows, 24 columns (`booking_id` PK). |
| [`powerbi/data/fact_stay_nights.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/data/fact_stay_nights.csv) | Realized operational stay-night fact table (evaluated on stay date within reliable window). | 248,261 rows, 5 columns (`booking_id, stay_date` composite PK). |
| [`powerbi/data/fact_capacity.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/data/fact_capacity.csv) | Daily property capacity fact table (evaluated within reliable window). | 1,524 rows, 3 columns (`hotel_key, date_key` composite PK). |

### B. Power Query Ingestion & Validation
| File | Description | Checks / Rules Enforced |
| :--- | :--- | :--- |
| [`powerbi/power_query/parameters.m`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/parameters.m) | M parameter query defining `DataFolder` file path. | Single point of configuration for local CSV paths. |
| `powerbi/power_query/*.m` (6 files) | Pure M ingestion scripts typing all 48 columns explicitly with culture `en-US`. | Zero calculated columns in Power Query; strict pushdown to DAX. |
| [`src/make_pbi_m_scripts.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/src/make_pbi_m_scripts.py) | Dynamic generator inspecting actual CSV headers to emit M queries. | Automated code generation ensuring zero typo drift. |
| [`powerbi/power_query/test_m_scripts.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/power_query/test_m_scripts.py) | Python test suite verifying syntax, column coverage, and culture. | **7/7 M scripts PASS**. |
| [`src/validate_powerbi_model.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/src/validate_powerbi_model.py) | 16-point automated data model verification script. | **16/16 checks PASS** (keys, referential integrity, data types, reconciliation). |

### C. Data Model Blueprint & DAX Measure Architecture
| File | Description | Standard / Coverage |
| :--- | :--- | :--- |
| [`powerbi/MODEL_SPEC.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/MODEL_SPEC.md) | Exhaustive data model blueprint: columns, relationships, summarization, hiding, sort-by. | 48 columns documented, 8 active `1:*` single-direction joins, Rule K7 documented. |
| [`powerbi/measures.dax`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/measures.dax) | 26 production-ready DAX measures organized across 4 display folders. | Folder, purpose, and format string for every measure. |
| [`src/check_dax_refs.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/src/check_dax_refs.py) | Static parser checking DAX delimiter balance, column references, and measure dependencies. | **PASS**: 12/12 physical column refs exist, 25/25 measure dependencies resolved. |

### D. Visual Theme, Narrative Copy & Layout Specs
| File | Description | Compliance / Scope |
| :--- | :--- | :--- |
| [`powerbi/theme/hotel_theme.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/theme/hotel_theme.json) | Custom Power BI JSON report theme. | 8 color-blind-safe colors, Segoe UI typography, card/visual defaults. |
| [`src/validate_powerbi_theme.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/src/validate_powerbi_theme.py) | Automated WCAG contrast ratio validator. | **PASS**: Foreground 15.5:1 ($\ge 7:1$), all data colors $\ge 3:1$ against white. |
| [`powerbi/theme/README.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/theme/README.md) | Theme documentation and contrast reference tables. | Accessible design reference. |
| [`src/make_dashboard_text.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/src/make_dashboard_text.py) | Dynamic text generator reading real numbers from data marts. | Zero hardcoded numbers; full traceability to CSV sources. |
| [`powerbi/DASHBOARD_TEXT.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/DASHBOARD_TEXT.md) | Narrative copy, titles, alt text, and 6 real key findings. | Page titles, questions, alt text, and source-tagged findings. |
| [`powerbi/REPORT_SPEC.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/REPORT_SPEC.md) | Visual-by-visual layout spec for 4 core pages + 2 supporting pages (1280x720). | Coordinates ($x, y, w, h$), field bindings, sort orders, and interactions. |

### E. Manual Assembly Guide & Validation Checklist
| File | Description | Purpose |
| :--- | :--- | :--- |
| [`powerbi/BUILD_GUIDE.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/BUILD_GUIDE.md) | Click-by-click instructions for assembling the `.pbix` in Power BI Desktop. | 8 numbered phases with time estimates and checkpoints. |
| [`src/make_pbi_validation.py`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/src/make_pbi_validation.py) | Benchmark generator computing expected measure values via pandas star schema. | Multi-scenario benchmark engine across 6 slicer scenarios. |
| [`powerbi/validation_expected.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/validation_expected.csv) | 138 benchmark expected values covering all 23 numeric measures across S1–S6. | Baseline reference for automated and visual QA. |
| [`powerbi/VALIDATION_CHECKLIST.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/VALIDATION_CHECKLIST.md) | QA checklist table covering 6 scenarios across 10 critical measures. | Interactive scorecard for human verification. |
| [`powerbi/README.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/README.md) | Asset catalog, usage order, refresh procedures, model summary, screenshot list. | Primary entry point for Phase 4 assets. |

---

## 2. Automated Validation Test Results

All three primary validation test suites executed cleanly and returned exit code 0:

### 1. Star Schema Validation (`src/validate_powerbi_model.py`)
```
==============================================================================================================
POWER BI STAR SCHEMA MODEL VALIDATION: powerbi/data/*.csv
==============================================================================================================
PASS   | C1.1  | dim_date.date_key uniqueness and non-null               | Rows: 1096, Unique keys: 1096, Nulls: 0
PASS   | C1.2  | dim_hotel.hotel_key uniqueness and non-null             | Rows: 2, Unique keys: 2, Nulls: 0
PASS   | C1.3  | dim_profile.profile_key uniqueness and non-null         | Rows: 101, Unique keys: 101, Nulls: 0
PASS   | C1.4  | fact_bookings.booking_id uniqueness and non-null        | Rows: 119388, Unique keys: 119388, Nulls: 0
PASS   | C1.5  | fact_capacity (hotel_key, date_key) uniqueness and non-null | Rows: 1524, Unique pairs: 1524, Nulls: 0
PASS   | C1.6  | fact_stay_nights (booking_id, stay_date) uniqueness and non-null | Rows: 248261, Unique pairs: 248261, Nulls: 0
PASS   | C2.1  | hotel_key referential integrity (dim_hotel)             | Unmatched keys: fact_bookings=0, fact_stay_nights=0, fact_capacity=0
PASS   | C2.2  | profile_key referential integrity (dim_profile)         | Unmatched keys: fact_bookings=0, fact_stay_nights=0
PASS   | C2.3  | date_key referential integrity (dim_date)               | Unmatched dates: fact_bookings=0, fact_stay_nights=0, fact_capacity=0
PASS   | C3.1  | Dates parse strictly as ISO YYYY-MM-DD                  | 5 date columns validated across dim_date, fact_bookings, fact_stay_nights, fact_capacity
PASS   | C3.2  | Flags hold strictly integer values in {0, 1}            | All 5 flag columns strictly hold 0 and 1
PASS   | C3.3  | No literal 'nan', 'null', or 'none' string tokens in CSVs | Total literal nan/null strings across 6 CSVs: 0
PASS   | C4.1  | Total bookings and cancellations equal v_booking_trends | Bookings: 119388 vs 119388 (diff=0); Cancellations: 44223 vs 44223 (diff=0)
PASS   | C4.2  | Per hotel-month reconciliation against v_monthly_kpis (50 months) | Months: 50/50, Sold diffs: 0, Avail diffs: 0, Rev diffs: 0, Occ diffs: 0, RevPAR diffs: 0
PASS   | C5.1  | Model simulation (Resort Hotel, 2016: Sold, Rev, Avail, ADR, Occ, RevPAR) | Sold: 54037 vs 54037; Rev: $4822927.67 vs $4822927.67; Avail: 76860 vs 76860; ADR: $89.25 vs $89.25; Occ: 70.31% vs 70.31%; RevPAR: $62.75 vs $62.75
PASS   | C6.1  | dim_profile has 0 duplicate attribute combinations      | Total profiles: 101, Duplicate combinations: 0
--------------------------------------------------------------------------------------------------------------
POWER BI STAR SCHEMA VALIDATION SUMMARY: ALL 16 CHECKS PASSED [PASS]
==============================================================================================================
```

### 2. DAX Reference Verification (`src/check_dax_refs.py`)
```
====================================================================================================
POWER BI DAX REFERENCE & SYNTAX VERIFICATION: powerbi/measures.dax
====================================================================================================
[PASS] Delimiter Balance Check: All delimiters balanced () [] {} ""
[INFO] Discovered 26 measures in measures.dax across 4 display folders.
[PASS] Metadata Completeness: All 26 measures have Purpose, Folder, and Format.
[PASS] Physical Column References: All 12 table[column] references exist in CSV headers.
[PASS] Measure Dependency References: All 25 internal [Measure] references exist.
----------------------------------------------------------------------------------------------------
POWER BI DAX REFERENCE CHECK: ALL CHECKS PASSED [PASS]
====================================================================================================
```

### 3. Power Query M Script Validation (`powerbi/power_query/test_m_scripts.py`)
```
====================================================================================================
TESTING POWER BI POWER QUERY M SCRIPTS: powerbi/power_query/*.m
====================================================================================================
[PASS] dim_date.m           -> Source: dim_date.csv           (8 cols, pure ingest, en-US)
[PASS] dim_hotel.m          -> Source: dim_hotel.csv          (3 cols, pure ingest, en-US)
[PASS] dim_profile.m        -> Source: dim_profile.csv        (5 cols, pure ingest, en-US)
[PASS] fact_bookings.m      -> Source: fact_bookings.csv      (24 cols, pure ingest, en-US)
[PASS] fact_stay_nights.m   -> Source: fact_stay_nights.csv   (5 cols, pure ingest, en-US)
[PASS] fact_capacity.m      -> Source: fact_capacity.csv      (3 cols, pure ingest, en-US)
[PASS] parameters.m         -> Parameter definition for DataFolder (IsParameterQuery=true)
----------------------------------------------------------------------------------------------------
POWER BI POWER QUERY VERIFICATION: ALL 7 M SCRIPTS PASSED [PASS]
====================================================================================================
```

---

## 3. Manual Steps Assigned to Report Author

Because Power BI Desktop cannot execute directly in headless Linux/macOS environments, the final assembly and visual sign-off steps belong to the report author:

1. **Build the Report in Power BI Desktop**:
   - Open Power BI Desktop on Windows.
   - Follow [`powerbi/BUILD_GUIDE.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/BUILD_GUIDE.md) step-by-step:
     1. Create parameter `DataFolder` and import the 6 queries.
     2. Set up the 8 active relationships in Model View; mark date table; hide surrogate keys.
     3. Create table `Measures` and paste all 26 measures from [`powerbi/measures.dax`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/measures.dax).
     4. Import [`powerbi/theme/hotel_theme.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/theme/hotel_theme.json).
     5. Assemble the canvas visuals using coordinates and bindings from [`powerbi/REPORT_SPEC.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/REPORT_SPEC.md) and text from [`powerbi/DASHBOARD_TEXT.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/DASHBOARD_TEXT.md).
2. **Execute Validation Checklist**:
   - Work through [`powerbi/VALIDATION_CHECKLIST.md`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/powerbi/VALIDATION_CHECKLIST.md).
   - Test each of the 6 slicer scenarios (`S1` to `S6`).
   - Confirm that the 10 core measures match within stated tolerances (0.1 pp for percentages, $0.01 for currency, exact for counts).
3. **Capture Report Screenshots**:
   - Capture full-page PNG screenshots of all completed pages:
     - `powerbi/screenshots/page1_executive.png`
     - `powerbi/screenshots/page2_revenue.png`
     - `powerbi/screenshots/page3_cancellations.png`
     - `powerbi/screenshots/page4_insights.png`
     - `powerbi/screenshots/page5_drillthrough.png`
     - `powerbi/screenshots/page6_model.png`
4. **Save `.pbix` File**:
   - Save the finalized application to `powerbi/hotel_revenue_analytics.pbix`.
