# Phase 1 Sign-off Document

## 1. Project File Tree (3 Levels)
```
.
├── .env
├── .env.example
├── .gitignore
├── PROJECT_CONTEXT.md
├── README.md
├── config
│   └── .gitkeep
├── data
│   ├── outputs
│   │   └── .gitkeep
│   ├── processed
│   │   ├── .gitkeep
│   │   ├── bookings_clean.csv
│   │   └── excluded_rows.csv
│   └── raw
│       ├── .gitkeep
│       └── hotel_bookings.csv
├── docs
│   ├── .gitkeep
│   ├── data_dictionary.md
│   ├── data_quality_log.md
│   ├── decision_log.md
│   └── phase1_signoff.md
├── excel
│   └── .gitkeep
├── notebooks
│   ├── .gitkeep
│   └── 01_cleaning_eda.ipynb
├── powerbi
│   └── .gitkeep
├── reports
│   ├── figures
│   │   ├── .gitkeep
│   │   ├── fig01_cancellation_rate_by_hotel.png
│   │   ├── fig02_bookings_by_arrival_month.png
│   │   ├── fig03_adr_distribution_non_cancelled.png
│   │   ├── fig04_cancellation_rate_by_lead_bucket.png
│   │   ├── fig05_cancellation_rate_by_deposit_type.png
│   │   └── fig06_night_weighted_adr_by_arrival_month.png
│   └── tables
│       ├── .gitkeep
│       ├── profile_adr_extremes.csv
│       ├── profile_adr_zero_by_segment.csv
│       ├── profile_categorical_distributions.csv
│       ├── profile_issues.csv
│       ├── profile_missing_values.csv
│       ├── profile_numeric_summary.csv
│       ├── profile_top_20_countries.csv
│       └── raw_verification.csv
├── requirements.txt
├── sql
│   ├── .gitkeep
│   ├── 01_schema.sql
│   └── 02_phase1_checks.sql
├── src
│   ├── .gitkeep
│   ├── build_eda_notebook.py
│   ├── check_phase1.py
│   ├── clean_data.py
│   ├── create_database.py
│   ├── db.py
│   ├── load_to_postgres.py
│   ├── profile_raw.py
│   ├── run_sql.py
│   └── verify_raw.py
└── tests
    ├── .gitkeep
    └── test_clean.py
```

## 2. Row Transformation Summary
- **Raw Rows**: 119,390 (`data/raw/hotel_bookings.csv`)
- **Excluded Rows**: 2 (`data/processed/excluded_rows.csv`)
  - Row 1: `booking_id = 14969`, ADR = -6.38 (Reason: `adr < 0 (-6.38)`)
  - Row 2: `booking_id = 48515`, ADR = 5400.0 (Reason: `adr > 1000 (5400.0)`)
- **Cleaned Rows**: 119,388 (`data/processed/bookings_clean.csv`)
- **Database Rows**: 119,388 (`hotel.bookings` table in PostgreSQL database `hotel_analytics`)

```
Raw Rows (119,390) -> Excluded Rows (2) -> Cleaned Rows (119,388) -> Database Rows (119,388)
```

## 3. Pytest Verification Suite Output
Command: `pytest tests/test_clean.py -v`

```
============================= test session starts ==============================
platform darwin -- Python 3.11.17, pytest-9.1.1, pluggy-1.7.0 -- /Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/.venv/bin/python3.11
cachedir: .pytest_cache
rootdir: /Users/divyansh/code/Development/DataScience/hotel-revenue-analytics
plugins: platformdirs-4.13.3, anyio-4.15.1
collecting ... collected 14 items

tests/test_clean.py::test_01_row_count PASSED                            [  7%]
tests/test_clean.py::test_02_booking_id_integrity PASSED                 [ 14%]
tests/test_clean.py::test_03_column_list_and_order PASSED                [ 21%]
tests/test_clean.py::test_04_no_nulls_in_key_columns PASSED              [ 28%]
tests/test_clean.py::test_05_categorical_domain_validity PASSED          [ 35%]
tests/test_clean.py::test_06_cancellation_flags_consistency PASSED       [ 42%]
tests/test_clean.py::test_07_adr_range_and_room_revenue PASSED           [ 50%]
tests/test_clean.py::test_08_total_nights_and_checkout_date PASSED       [ 57%]
tests/test_clean.py::test_09_booking_date_lead_time_consistency PASSED   [ 64%]
tests/test_clean.py::test_10_lead_bucket_boundaries_and_mapping PASSED   [ 71%]
tests/test_clean.py::test_11_flag_columns_and_zero_conditions PASSED     [ 78%]
tests/test_clean.py::test_12_cancellation_days_lead_null_rule PASSED     [ 85%]
tests/test_clean.py::test_13_arrival_date_range PASSED                   [ 92%]
tests/test_clean.py::test_14_excluded_rows_schema_and_count PASSED       [100%]

============================== 14 passed in 1.15s ==============================
```

## 4. Cross-Engine Integrity Reconciliation Output (`src/check_phase1.py`)
Command: `python src/check_phase1.py`

```
Reading /Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/data/processed/bookings_clean.csv for Phase 1 reconciliation...

================================================================================
PHASE 1 INTEGRITY RECONCILIATION: PANDAS vs SQL
================================================================================
                                           Check Item Pandas (CSV) PostgreSQL Status
                    Check a: Total Portfolio Bookings       119388     119388   PASS
                         Check a: City Hotel Bookings        79329      79329   PASS
                       Check a: Resort Hotel Bookings        40059      40059   PASS
              Check b: City Hotel Total Cancellations        33101      33101   PASS
                   Check b: City Hotel Total No-Shows          916        916   PASS
                Check b: City Hotel Cancellation Rate       0.4173     0.4173   PASS
            Check b: Resort Hotel Total Cancellations        11122      11122   PASS
                 Check b: Resort Hotel Total No-Shows          291        291   PASS
              Check b: Resort Hotel Cancellation Rate       0.2776     0.2776   PASS
               Check c: Total Distinct Arrival Months           26         26   PASS
         Check c: All 26 Monthly Counts Match Exactly         True       True   PASS
                     Check d: Lead Bucket '0-7' Count        19746      19746   PASS
                    Check d: Lead Bucket '8-30' Count        18960      18960   PASS
                   Check d: Lead Bucket '31-90' Count        29552      29552   PASS
                  Check d: Lead Bucket '91-180' Count        26439      26439   PASS
                    Check d: Lead Bucket '181+' Count        24691      24691   PASS
Check f: Non-Cancelled Stays (total_nights > 0) Count        74485      74485   PASS
       Check f: Non-Cancelled Stays Sum(total_nights)       255030     255030   PASS

================================================================================
ALL PHASE 1 CHECKS PASSED.
================================================================================
```
