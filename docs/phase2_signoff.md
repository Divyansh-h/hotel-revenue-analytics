# Phase 2 Sign-off Document: SQL Analytical Modeling & Data Marts

## 1. SQL Pipeline Inventory (Purpose & Grain)

| SQL Script | Purpose | Output Objects | Grain (One Row Represents) |
| :--- | :--- | :--- | :--- |
| `sql/10_dim_date.sql` | Generates canonical calendar date dimension table covering 2015-01-01 to 2017-12-31 with PK on `date_key`. | `hotel.dim_date` | One calendar day (1,096 rows) |
| `sql/20_stay_nights.sql` | Expands non-cancelled bookings (`is_canceled = 0 AND total_nights > 0`) into daily stay-night records per K1. | `hotel.stay_nights` | One booking per night stayed (255,030 rows) |
| `sql/21_capacity_daily.sql` | Establishes reliable window (W1: 2015-08-01 to 2017-08-31), derives capacity with 10% buffer (W2), and creates daily performance mart. | `hotel.window_params`<br>`hotel.capacity_derivation`<br>`hotel.capacity`<br>`hotel.daily_performance` | - Window params: 1 global row<br>- Capacity: 1 row per hotel (2 rows)<br>- Daily performance: 1 row per hotel per date in window (1,524 rows) |
| `sql/30_monthly_kpis.sql` | Defines stay-night KPI views calculating room nights, revenue, occupancy %, ADR, and RevPAR (K1 to K4). | `hotel.v_monthly_kpis`<br>`hotel.v_hotel_totals`<br>`hotel.v_yearly_kpis` | - Monthly KPIs: 1 row per hotel per stay month (50 rows)<br>- Totals: 1 row per hotel + 'All hotels' (3 rows)<br>- Yearly: 1 row per hotel per year (6 rows) |
| `sql/31_booking_trends.sql` | Booking pace and volume analytics view across all 26 arrival months with MoM, YoY, and rolling cancellation metrics (K5, K6). | `hotel.v_booking_trends` | One row per hotel per arrival month (52 rows) |
| `sql/40_cancellation_drivers.sql` | Evaluates cancellation rates, booking shares, and deviations from hotel averages across 12 behavioral and operational dimensions. | `hotel.v_cancellation_drivers` | One row per hotel ('All', 'City Hotel', 'Resort Hotel') per dimension per category (165 rows) |
| `sql/41_cancel_timing.sql` | Analyzes cancellation lead time distributions, deposit interactions, and late-cancellation revenue risk (D11, K5). | `hotel.v_cancel_timing`<br>`hotel.v_lead_deposit_matrix`<br>`hotel.v_late_cancel_revenue_at_risk` | - Cancel timing: 1 row per hotel per timing bucket (21 rows)<br>- Lead deposit: 1 row per hotel per lead x deposit (45 rows)<br>- Late cancel risk: 1 row per hotel per arrival month (78 rows) |
| `sql/50_segment_channel.sql` | Analyzes market segment and distribution channel performance, contributions, and cross-tabulation per K7 and W1. | `hotel.v_segment_performance`<br>`hotel.v_channel_performance`<br>`hotel.v_segment_channel_matrix` | - Segment: 1 row per hotel per segment (22 rows)<br>- Channel: 1 row per hotel per channel (14 rows)<br>- Matrix: 1 row per hotel per segment x channel (71 rows) |
| `sql/60_seasonality_overbooking.sql` | Models seasonal demand tiers (NTILE 3), daily cancellation rate percentiles, and operational upgrade/mismatch rates. | `hotel.v_seasonality`<br>`hotel.v_daily_cancel_rates`<br>`hotel.v_overbooking_buffer`<br>`hotel.v_room_mismatch` | - Seasonality: 1 row per hotel per month number (24 rows)<br>- Daily cancel: 1 row per hotel per date >=20 arrivals (1,522 rows)<br>- Overbooking buffer: 1 row per hotel per month number (24 rows)<br>- Room mismatch: 1 row per hotel per arrival month (52 rows) |
| `sql/99_phase2_summary.sql` | Unified executive summary combining capacity, window, stay-night KPIs, and overall cancellation rates. | Executive summary query | One row per hotel plus portfolio total ('All hotels') (3 rows) |

---

## 2. Exported CSV Data Marts (`data/outputs/`)

Generated via `src/export_sql_outputs.py` (UTF-8, header, ISO dates, '.' decimal, no index):

| Exported File | Source Object | Rows Written | Primary Keys / Dimensions |
| :--- | :--- | :---: | :--- |
| `data/outputs/v_monthly_kpis.csv` | `hotel.v_monthly_kpis` | 50 | `hotel`, `month_start` |
| `data/outputs/v_hotel_totals.csv` | `hotel.v_hotel_totals` | 3 | `hotel` |
| `data/outputs/v_yearly_kpis.csv` | `hotel.v_yearly_kpis` | 6 | `hotel`, `year` |
| `data/outputs/v_booking_trends.csv` | `hotel.v_booking_trends` | 52 | `hotel`, `arrival_month_start` |
| `data/outputs/v_cancellation_drivers.csv` | `hotel.v_cancellation_drivers` | 165 | `hotel`, `dimension`, `category` |
| `data/outputs/v_cancel_timing.csv` | `hotel.v_cancel_timing` | 21 | `hotel`, `timing_bucket` |
| `data/outputs/v_lead_deposit_matrix.csv` | `hotel.v_lead_deposit_matrix` | 45 | `hotel`, `lead_bucket`, `deposit_type` |
| `data/outputs/v_late_cancel_revenue_at_risk.csv` | `hotel.v_late_cancel_revenue_at_risk` | 78 | `hotel`, `arrival_month_start` |
| `data/outputs/v_segment_performance.csv` | `hotel.v_segment_performance` | 22 | `hotel`, `market_segment` |
| `data/outputs/v_channel_performance.csv` | `hotel.v_channel_performance` | 14 | `hotel`, `distribution_channel` |
| `data/outputs/v_segment_channel_matrix.csv` | `hotel.v_segment_channel_matrix` | 71 | `hotel`, `market_segment`, `distribution_channel` |
| `data/outputs/v_seasonality.csv` | `hotel.v_seasonality` | 24 | `hotel`, `month_num` |
| `data/outputs/v_overbooking_buffer.csv` | `hotel.v_overbooking_buffer` | 24 | `hotel`, `month_num` |
| `data/outputs/v_room_mismatch.csv` | `hotel.v_room_mismatch` | 52 | `hotel`, `arrival_month_start` |
| `data/outputs/capacity.csv` | `hotel.capacity` | 2 | `hotel` |
| `data/outputs/capacity_derivation.csv` | `hotel.capacity_derivation` | 2 | `hotel` |
| `data/outputs/daily_performance.csv` | `hotel.daily_performance` | 1,524 | `hotel`, `stay_date` |

---

## 3. Independent Pandas vs SQL Cross-Check Results

Executed via `src/crosscheck_sql_vs_pandas.py`:
- Recomputed stay-night metrics via day-offset explosion in NumPy/Pandas directly from `data/processed/bookings_clean.csv` (no SQL).
- Filtered to window `2015-08-01` to `2017-08-31` (762 days) using capacities from `config/assumptions.yml` (City: 250, Resort: 210).
- Recomputed booking trends from `data/processed/bookings_clean.csv`.

```
=====================================================================================
CROSS-CHECK RESULTS SUMMARY
=====================================================================================
                               Metric  Rows Compared Worst Difference Threshold Status
     v_monthly_kpis: room_nights_sold             50                0 Exact (0)   PASS
v_monthly_kpis: room_nights_available             50                0 Exact (0)   PASS
     v_monthly_kpis: room_revenue ($)             50           0.0000   <= 0.01   PASS
    v_monthly_kpis: occupancy_pct (%)             50           0.0000   <= 0.01   PASS
              v_monthly_kpis: adr ($)             50           0.0000   <= 0.01   PASS
           v_monthly_kpis: revpar ($)             50           0.0000   <= 0.01   PASS
           v_booking_trends: bookings             52                0 Exact (0)   PASS
      v_booking_trends: cancellations             52                0 Exact (0)   PASS
v_booking_trends: cancel_rate_pct (%)             52           0.0000   <= 0.01   PASS

=====================================================================================
ALL INDEPENDENT PANDAS vs SQL CROSS-CHECKS PASSED.
=====================================================================================
```

---

## 4. Phase 2 Executive Summary Output (`sql/99_phase2_summary.sql`)

```
hotel        | capacity_rooms | window_start | window_end | room_nights_sold | room_revenue   | adr    | occupancy_pct | revpar | overall_cancel_rate_pct
-------------------------------------------------------------------------------------------------------------------------------------------------------
City Hotel   | 250            | 2015-08-01   | 2017-08-31 | 133860           | 14285466.42    | 106.72 | 70.27         | 74.99  | 41.7
Resort Hotel | 210            | 2015-08-01   | 2017-08-31 | 114401           | 10901719.74    | 95.29  | 71.49         | 68.13  | 27.8
All hotels   | 460            | 2015-08-01   | 2017-08-31 | 248261           | 25187186.16    | 101.45 | 70.83         | 71.86  | 37.0
```
