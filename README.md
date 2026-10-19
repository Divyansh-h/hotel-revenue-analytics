# Hotel Revenue Analytics

## Project goal
Act as the analyst for a hotel group's revenue team. Pipeline: clean (Python) -> analyse (PostgreSQL) -> summarise (Excel) -> visualise (Power BI) -> recommend (written insights). Provide revenue, cancellation, occupancy, and distribution channel analytics for City Hotel (Lisbon) and Resort Hotel (Algarve).

## Dataset
Hotel Booking Demand dataset: 119,390 rows, 32 columns. Covers City Hotel (Lisbon) and Resort Hotel (Algarve) with arrival dates from 2015-07-01 to 2017-08-31. Raw file `data/raw/hotel_bookings.csv` is strictly read-only and preserved untouched. The raw data lacks explicit booking identifiers and hotel room capacity.

## Folder structure
```
hotel-revenue-analytics/
├── config/             # Environment and analytical assumption configs
├── data/
│   ├── raw/            # Read-only source datasets (hotel_bookings.csv)
│   ├── processed/      # Cleaned and excluded datasets (bookings_clean.csv, excluded_rows.csv)
│   └── outputs/        # Analytical extracts and exports
├── docs/               # Data dictionary, data quality log, decision log, sign-offs
├── excel/              # Excel financial summaries and workbooks
├── notebooks/          # Exploratory and analytical Jupyter notebooks
├── powerbi/            # Power BI reports and dashboard templates
├── reports/
│   ├── figures/        # Exported charts and visual figures
│   └── tables/         # Summary CSV reports and profiling tables
├── sql/                # Schema definitions and analytical SQL queries
├── src/                # Pipeline scripts (cleaning, db, ingestion, checks)
└── tests/              # Pytest verification suites
```

## How to reproduce Phase 1 (exact commands in order)
Execute the following commands from the repository root:

```bash
# 1. Environment Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Database Environment Setup
# Ensure PostgreSQL is running and .env contains PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE=hotel_analytics
cp .env.example .env  # if not already configured

# 3. Verify Raw Dataset
python src/verify_raw.py

# 4. Profile Raw Dataset (generates reports/tables/profile_*.csv)
python src/profile_raw.py

# 5. Clean Dataset and Generate Clean/Excluded CSVs (D1-D12)
python src/clean_data.py

# 6. Run Test Suite
pytest tests/test_clean.py -v

# 7. Execute EDA Notebook and Export Figures
jupyter nbconvert --to notebook --execute --inplace notebooks/01_cleaning_eda.ipynb

# 8. Create Database, Schema, and Ingest Data into PostgreSQL
python src/create_database.py
python src/run_sql.py sql/01_schema.sql
python src/load_to_postgres.py

# 9. Run Phase 1 SQL Checks and Cross-Engine Reconciliation
python src/run_sql.py sql/02_phase1_checks.sql
python src/check_phase1.py
```

## How to reproduce Phase 2 (exact commands in order)
Execute the following commands from the repository root:

```bash
# 1. Date Dimension Table (2015-01-01 to 2017-12-31)
python src/run_sql.py sql/10_dim_date.sql

# 2. Stay-Nights Expansion Table (K1)
python src/run_sql.py sql/20_stay_nights.sql

# 3. Capacity Derivation, Reliable Window (W1, W2), and Daily Performance Mart
python src/run_sql.py sql/21_capacity_daily.sql
python src/write_assumptions.py

# 4. Monthly, Yearly, and Overall Stay-Night KPI Views (K1-K4)
python src/run_sql.py sql/30_monthly_kpis.sql

# 5. Booking Trends & Pace View Across 26 Arrival Months (K5, K6)
python src/run_sql.py sql/31_booking_trends.sql

# 6. Cancellation Drivers Analysis Across 12 Dimensions
python src/run_sql.py sql/40_cancellation_drivers.sql

# 7. Cancellation Timing, Deposit Interaction, and Late Cancellation Risk
python src/run_sql.py sql/41_cancel_timing.sql

# 8. Market Segment & Distribution Channel Performance Views (K7)
python src/run_sql.py sql/50_segment_channel.sql

# 9. Seasonality Tiers, Overbooking Buffers, and Room Mismatch Views
python src/run_sql.py sql/60_seasonality_overbooking.sql

# 10. Executive Summary Query
python src/run_sql.py sql/99_phase2_summary.sql

# 11. Export All 17 Analytical Objects to CSV (data/outputs/*.csv)
python src/export_sql_outputs.py

# 12. Run Independent Pandas vs SQL Cross-Check
python src/crosscheck_sql_vs_pandas.py
```

## How to reproduce Phase 4 (exact commands in order)
Execute the following commands from the repository root:

```bash
# 1. Build Star Schema Tables in PostgreSQL (hotel.dim_*, hotel.fact_*)
python src/run_sql.py sql/70_powerbi_model.sql

# 2. Export Star Schema CSVs to powerbi/data/
python src/export_powerbi_model.py

# 3. Validate Star Schema CSV Integrity and Reconciliation (16 checks)
python src/validate_powerbi_model.py

# 4. Generate Pure Power Query M Ingestion Scripts & Validate
python src/make_pbi_m_scripts.py
python powerbi/power_query/test_m_scripts.py

# 5. Verify DAX Measures Syntax, Column References & Dependencies
python src/check_dax_refs.py

# 6. Validate Custom Report Theme & WCAG Accessibility Contrast
python src/validate_powerbi_theme.py

# 7. Generate Dashboard Narrative and Key Findings Text from Data Marts
python src/make_dashboard_text.py

# 8. Compute Multi-Scenario Expected Validation Benchmarks (S1-S6)
python src/make_pbi_validation.py

# 9. Power BI Desktop Assembly & Validation (Manual Steps for Report Author)
# Follow powerbi/BUILD_GUIDE.md to import queries, create relationships, add DAX measures, apply theme, and assemble visual canvas.
# Verify report cards against benchmarks using powerbi/VALIDATION_CHECKLIST.md.
# Save page screenshots to powerbi/screenshots/ and save report as powerbi/hotel_revenue_analytics.pbix.
```

## Known data issues
Copied from `docs/data_quality_log.md`:

| issue | column(s) | rows affected | percent of data | decision | rationale | rows after cleaning |
| :--- | :--- | :---: | :---: | :--- | :--- | :---: |
| Negative ADR (`adr < 0`) | `adr` | 1 | 0.0008% | **D5: EXCLUDED** | Single row with `adr = -6.38` is written to `data/processed/excluded_rows.csv` with reason column. Negative lodging rates represent invalid billing errors. | 0 |
| Extreme High ADR (`adr > 1000`) | `adr` | 1 | 0.0008% | **D5: EXCLUDED** | Single row with `adr = 5400.0` is written to `data/processed/excluded_rows.csv` with reason column. Extreme outlier that distorts revenue and ADR metrics. | 0 |
| Zero ADR (`adr = 0`) | `adr, market_segment` | 1959 | 1.6408% | **D5: KEPT** | D5 explicitly excludes only `adr < 0 or adr > 1000`. Zero ADR bookings are retained as legitimate non-revenue stays (e.g. 680 Complementary, promotions, house guests); they earn 0 room revenue per K2. | 1,959 |
| Zero Stay Nights (`weekend + week nights = 0`) | `stays_in_weekend_nights, stays_in_week_nights` | 715 | 0.5989% | **D6: KEPT and flagged** (`flag_zero_nights = 1`) | Retained in analytical table; count as bookings in pipeline but generate 0 room-nights sold per K1. | 715 |
| Zero Total Guests (`adults + children + babies = 0`) | `adults, children, babies` | 180 | 0.1508% | **D6: KEPT and flagged** (`flag_zero_guests = 1`) | Retained in analytical table; count as bookings in pipeline but have 0 guests recorded. | 180 |
| Exact Duplicate Rows across all 32 raw columns | All 32 columns | 31994 | 26.7979% | **D7: KEPT and flagged** (`is_duplicate_row = 1`) | No unique booking ID in raw file; duplicates may represent real separate bookings. Kept with later copies flagged for sensitivity analysis. | 31,994 |
| Canceled Date Later Than Arrival Date | `reservation_status, reservation_status_date, arrival_date_*` | 0 | 0.0000% | **D11: Validated** | Zero cancellations have status date after arrival date. D11 calculates `days_cancelled_before_arrival = arrival_date - reservation_status_date` for canceled bookings. | 0 |
| Room Type Mismatch (`assigned <> reserved`) | `reserved_room_type, assigned_room_type` | 14917 | 12.4943% | **D10: KEPT and flagged** (`room_type_mismatch = 1`) | Assigned room differs from reserved room due to operational reassignments or upgrades; flagged as integer 1/0. (1 of 14,917 was the excluded ADR 5400 outlier). | 14,916 |
| Missing Company Identifier | `company` | 112593 | 94.3069% | **D3: DROPPED** | Approximately 94.31% missing; column dropped from final analytical schema and PostgreSQL table. | 0 (column dropped) |
| Missing Agent Identifier | `agent` | 16340 | 13.6862% | **D3: KEPT as nullable integer** | Direct or corporate reservations without travel agency are preserved as nullable integer in schema. | 16,340 (NULL) |
| Missing Country of Origin | `country` | 488 | 0.4087% | **D3: IMPUTED** (`country = 'Unknown'`) | Minor missingness imputed to string `'Unknown'` to retain bookings in geographical aggregations without dropping rows. | 0 NULLs (488 as `'Unknown'`) |
| Missing Children Count | `children` | 4 | 0.0034% | **D3: IMPUTED** (`children = 0`) | 4 rows with NaN imputed to 0 to enable total guest count calculation. | 0 NULLs (4 imputed to 0) |
| Undefined Market Segment | `market_segment` | 2 | 0.0017% | **KEPT as 'Undefined'** | Retained as `'Undefined'` categorical string without dropping rows or synthetic imputation, preserving source fidelity. | 2 |
| Undefined Distribution Channel | `distribution_channel` | 5 | 0.0042% | **KEPT as 'Undefined'** | Retained as `'Undefined'` categorical string without dropping rows or synthetic imputation, preserving source fidelity. | 5 |
