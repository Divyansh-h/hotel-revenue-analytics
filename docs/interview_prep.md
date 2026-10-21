# Technical & Analytical Interview Preparation Guide

This guide provides 25 concise questions and answers grounded in the **Hotel Revenue & Cancellation Analytics** platform. Each answer is strictly under 90 words, cites exact empirical metrics from [`reports/findings_data.json`](../reports/findings_data.json), and adheres to the project rules and data governance standards.

---

## 25 Technical & Strategic Interview Questions

### Q01: How was property capacity derived, and why was this methodology chosen?
**Answer:** Because the raw data lacks physical room inventory, capacity was derived empirically per Rule W2 from the maximum rooms occupied on any single calendar night within the reliable window, buffered by 10% and rounded up to the nearest ten rooms. For City Hotel, the peak was 226 rooms on 2016-08-13, yielding a capacity of 250 rooms [`reports/findings_data.json`, `hotel_benchmarks.City Hotel.capacity`]. For Resort Hotel, the peak was 187 rooms on 2016-03-25, producing a capacity of 210 rooms [`reports/findings_data.json`, `hotel_benchmarks.Resort Hotel.capacity`].

### Q02: What does "stay conversion" mean in this project, and how does it relate to cancellations?
**Answer:** In this project, stay conversion represents the proportion of created reservations that successfully result in guest check-out, calculated strictly as 1 minus the cancellation rate per Rule K6. Across all 119,388 analytical bookings, stay conversion was 62.96% (75,165 completed stays) [`reports/findings_data.json`, `cancellations.overall`]. This is an operational reservation fulfillment proxy, not a web marketing acquisition funnel conversion, because the dataset contains zero clickstream, website visitor sessions, or preliminary availability search logs.

### Q03: Why is ADR calculated as total revenue divided by room-nights sold rather than a plain average?
**Answer:** A simple average across raw reservation rows weights a one-night stay identically to a fourteen-night stay, severely distorting realized lodging yield. Per Rule K3, ADR is calculated as total room revenue divided by room-nights sold. Across the 762-day reliable window, the portfolio generated $25,187,186.16 in room revenue over 248,261 room nights sold, establishing an authentic night-weighted ADR of $101.45 ($106.72 for City Hotel and $95.29 for Resort Hotel) [`reports/findings_data.json`, `hotel_benchmarks`]. Calculating an unweighted mean produces arithmetic distortion.

### Q04: How did you handle duplicate rows, and what impact do they have on the analysis?
**Answer:** The raw file contains 31,994 identical duplicate rows across all 32 columns (26.80% of data) [`data/processed/bookings_clean.csv`]. Because bookings lack unique primary keys, duplicates may represent genuine group room blocks. Under Decision D7, all duplicates were retained and flagged (`is_duplicate_row = 1`). A deduplication sensitivity analysis confirmed that while removing duplicates reduces overall cancellation from 37.04% to 27.49%, all core statistical associations, effect sizes, and operational findings remain robust [`reports/tables/stat_tests_summary.csv`, test_id = 'T6.1'].

### Q05: How were zero-night and zero-guest bookings treated in the pipeline?
**Answer:** Under Decision D6, 715 bookings with zero stay nights and 180 bookings with zero total guests were retained and flagged (`flag_zero_nights = 1`, `flag_zero_guests = 1`) [`data/processed/bookings_clean.csv`]. These records represent valid operational transactions—such as day-use facilities, administrative reservations, or immediate same-day cancellations—and are counted in booking pace and cancellation rate metrics (Rule K5), but contribute zero rooms to room-nights sold, occupancy, or revenue (Rule K1).

### Q06: How were ADR outliers detected and handled during data cleaning?
**Answer:** Under Decision D5, distribution profiling identified two extreme billing anomalies: one negative rate (`adr = -$6.38`) and one extreme upper outlier (`adr = $5,400.00`) [`data/processed/excluded_rows.csv`]. Both rows were removed from the analytical population and logged with written audit justifications in `excluded_rows.csv`, leaving 119,388 clean bookings [`reports/findings_data.json`, `cancellations.overall.total_bookings`]. Additionally, 1,959 legitimate zero-ADR bookings (such as 680 complementary stays) were retained and generate zero room revenue per Rule K2.

### Q07: Why do cancelled bookings earn zero revenue in stay-night KPIs?
**Answer:** Under Rule K2, room revenue is recognized only when a guest occupies a room night. Although 14,586 bookings had a 'Non Refund' deposit policy [`reports/findings_data.json`, `cancellations.deposit_type.non_refund_totals`], the dataset records zero financial ledger transactions, merchant processing settlements, or retained forfeiture amounts. Assuming revenue from unverified deposits would violate Global Rule R1. Therefore, cancelled bookings earn $0.00 room revenue in stay-night KPIs, and lost potential revenue is modeled strictly as hypothetical scenarios.

### Q08: Why does the reliable stay-night performance window begin on 2015-08-01 rather than 2015-07-01?
**Answer:** The raw arrival dataset begins on 2015-07-01. However, guests staying in early July may have arrived in June, meaning early July stay-night occupancy is artificially truncated. To ensure complete observation of all active stay nights, Rule W1 defines the reliable performance window from 2015-08-01 through 2017-08-31 (762 calendar days), capturing 248,261 room nights sold and $25,187,186.16 in room revenue [`reports/findings_data.json`, `metadata.window_days`, `hotel_benchmarks`]. Arrival booking KPIs utilize the full 26-month arrival span.

### Q09: How did you use the LAG window function in SQL?
**Answer:** In `sql/31_booking_trends.sql` and `hotel.v_monthly_kpis`, the SQL `LAG()` window function was used to calculate month-over-month (MoM) and year-over-year (YoY) revenue pacing and RevPAR momentum. By partitioning by hotel and ordering chronologically by `arrival_month_start`, `LAG(room_revenue, 1)` computed monthly revenue growth, while `LAG(revpar, 12)` established prior-year seasonal RevPAR benchmarks, enabling dynamic tracking of portfolio performance shifts [`data/outputs/v_monthly_kpis.csv`].

### Q10: How was the NTILE window function applied in SQL analytics?
**Answer:** In `sql/60_seasonality_overbooking.sql`, `NTILE(3)` partitioned the 12 calendar months into three equal demand tertiles—Peak, Shoulder, and Low—separately for each hotel based on stay-night RevPAR [`reports/findings_data.json`, `seasonality`]. For City Hotel, Peak months (June to September) averaged $95.96 RevPAR, whereas Low months (December to February) averaged $48.24 RevPAR [`data/outputs/v_seasonality.csv`]. This statistical tiering establishes the objective foundation for seasonal dynamic rate floors.

### Q11: How was the PERCENTILE_CONT window function used for overbooking buffers?
**Answer:** In `sql/60_seasonality_overbooking.sql`, `PERCENTILE_CONT(0.10)` was applied across daily cancellation rates on dates with at least 20 scheduled arrivals. This established a conservative 10th-percentile cancellation floor—representing the cancellation level that will be exceeded 90% of the time. For City Hotel, the mean conservative cancellation rate was 18.69% (46.7 rooms against 250 capacity), providing a mathematically grounded threshold for risk-managed overbooking buffers [`reports/findings_data.json`, `overbooking_and_mix.overbooking_buffer.City Hotel`].

### Q12: Why does the Power BI star schema include a junk dimension (dim_profile)?
**Answer:** The Power BI constellation model consolidates six binary behavioral flags into `dim_profile` (`profile_key`), creating a 101-row junk dimension [`powerbi/data/dim_profile.csv`]. This eliminates six repetitive columns from `fact_bookings` (119,388 rows) and `fact_stay_nights` (248,261 rows), compressing storage. Bidirectional cross-filtering is strictly avoided (using 1:* single-direction relationships) to prevent ambiguous filter paths, cyclical dependencies, and unexpected measure context transitions across the six dimensional tables [`powerbi/MODEL_SPEC.md`].

### Q13: Why are bidirectional cross-filters strictly avoided in the Power BI data model?
**Answer:** Bidirectional filtering can introduce circular filter propagation, non-deterministic query evaluation, and performance degradation across fact-to-dimension relationships. In this schema, `dim_date`, `dim_hotel`, and `dim_profile` connect to `fact_bookings` and `fact_stay_nights` using strictly 1:* single-direction relationships [`powerbi/MODEL_SPEC.md`]. This enforces unambiguous filter flow, guarantees predictable DAX measure calculation context, and ensures compliance with enterprise BI data modeling best practices.

### Q14: How were analytical numbers verified across Python, SQL, Excel, and Power BI?
**Answer:** Every KPI was independently reconciled across four technical environments. First, PostgreSQL queries were matched against vectorized pandas logic (`src/crosscheck_sql_vs_pandas.py`), passing all checks with 0.0000 maximum difference [`docs/decision_log.md`, Decision 20]. Second, openpyxl scanned all 434 cells in Excel's `KPI_Summary`, verifying 100% formula integrity with zero typed numbers [`src/build_workbook.py`]. Finally, Power BI measures were reconciled across six slicer scenarios in `powerbi/validation_expected.csv`, and all 2,073 report figures were audited [`reports/tables/number_audit.csv`].

### Q15: What were the key findings and effect size of the City vs Resort cancellation test?
**Answer:** A two-proportion z-test (Test T1) confirmed that City Hotel's cancellation rate (41.73%, 33,102 cancellations) is significantly higher than Resort Hotel's (27.76%, 11,121 cancellations) [`reports/findings_data.json`, `cancellations.overall`]. The test yielded $z = 47.91$ ($p < 0.001$) with an absolute risk difference of +13.96 percentage points and a Cohen's $h = 0.295$, denoting a statistically significant, small-to-moderate practical effect size [`reports/tables/stat_tests_summary.csv`, test_id = 'T1'].

### Q16: What did statistical testing reveal about deposit type and cancellation?
**Answer:** A chi-square test of independence (Test T2) revealed an extraordinary association between deposit type and cancellation ($\chi^2 = 27,675.45, df = 2, p < 0.001$) with a strong effect size of Cramer's $V = 0.4815$ [`reports/tables/stat_tests_summary.csv`, test_id = 'T2']. Counter-intuitively, Non Refund bookings exhibited a 99.36% cancellation rate (14,493 / 14,586), driven by Portuguese wholesale group allotments rather than retail consumer choices [`reports/findings_data.json`, `cancellations.deposit_type.non_refund_totals`].

### Q17: How does booking lead time correlate with cancellation probability?
**Answer:** A chi-square test (Test T3) showed that cancellation probability increases monotonically with lead time ($\chi^2 = 11,940.73, df = 4, p < 0.001$) with a moderate effect size (Cramer's $V = 0.3162$) [`reports/tables/stat_tests_summary.csv`, test_id = 'T3']. Bookings made 0–7 days prior cancel at 9.63% (1,902 / 19,746), rising steadily to 57.01% (14,077 / 24,691) for bookings made 181+ days in advance [`reports/findings_data.json`, `cancellations.lead_time.lead_buckets`].

### Q18: What continuous lead time differences exist between canceled and checked-out guests?
**Answer:** Because lead time is highly right-skewed, a non-parametric Mann-Whitney U test (Test T4) was conducted, yielding $U = 2,291,139,948$ ($p < 0.001$) and a rank-biserial correlation $r_{\text{rb}} = 0.3785$ [`reports/tables/stat_tests_summary.csv`, test_id = 'T4']. Cancelled reservations had a median lead time of 113.0 days, compared to 45.0 days for check-outs—a dramatic median shift of +68.0 days (+151.1%) [`reports/insights/02_cancellations.md`].

### Q19: What did multiple logistic regression uncover regarding cancellation predictors?
**Answer:** A multiple logistic regression model (Test T5) achieved a McFadden Pseudo $R^2 = 0.2674$ with all variance inflation factors under 1.05 [`reports/tables/stat_tests_summary.csv`, test_id = 'T5']. Controlling for customer segments, lead time, and repeat history, Non Refund deposits exhibited an adjusted odds ratio of $\text{OR} = 278.2$ ($p < 0.001$), while each additional advance lead day increased the odds of cancellation by 0.4% ($\text{OR} = 1.004$).

### Q20: What is the magnitude of late cancellation revenue at risk?
**Answer:** Analysis of cancellation timing revealed that 5,135 cancellations occur within 7 days of arrival (11.61% of all cancellations), representing 14,841 room nights and $1,533,486.66 in potential revenue at risk [`reports/findings_data.json`, `cancellations.timing_and_late_cancellations.late_cancellations_7d_summary`]. City Hotel absorbs 76.11% ($1,167,162.59) of this exposure. A 10% mitigation scenario through automated reconfirmation saves 1,484.1 room nights and $153,348.67 [`reports/insights/02_cancellations.md`].

### Q21: How does operational room-type mismatch act as a walk-risk signal?
**Answer:** Across 75,165 non-cancelled stays, 14,114 bookings (18.78%) experienced a mismatch between assigned and reserved room types [`reports/findings_data.json`, `overbooking_and_mix.room_type_mismatch.portfolio_summary`]. City Hotel recorded 14.65% mismatch, while Resort Hotel averaged 25.37%, surging counter-seasonally to 53.46% in January [`data/outputs/v_room_mismatch.csv`]. This signals significant winter wing closures and operational reassignment friction that increases front-desk walk risk during demand spikes.

### Q22: Which commercial segment and distribution channel present the greatest revenue opportunities?
**Answer:** Online TA captures the dominant portfolio volume (53.2% revenue share, $13,395,128.51 at $114.78 ADR) [`reports/findings_data.json`, `overbooking_and_mix.segment_performance.All`]. However, Direct booking generates the highest ADR ($124.06) and lowest cancellation rate (15.3%), whereas Groups exhibits poor yield ($75.37 ADR) and high cancellations (61.1%). Shifting 2,000 room nights per hotel from Groups to Direct yields +$189,200.00 in net revenue gain (Scenario C1) [`reports/insights/03_overbooking_mix.md`].

### Q23: What operational buffer do you recommend for overbooking, and why?
**Answer:** Based on the conservative 10th-percentile daily cancellation rate, I recommended a pilot overbooking buffer set at half the conservative rate: 23 rooms (9.2%) for City Hotel and 11 rooms (5.2%) for Resort Hotel [`reports/findings_data.json`, `overbooking_and_mix.overbooking_buffer`]. A half-buffer pilot protects revenue on peak compression dates while rigorously mitigating walk risks, compensating for the lack of operational walk cost data.

### Q24: What dynamic pricing rules do you recommend based on seasonality?
**Answer:** To optimize seasonality, I recommended a dynamic rate floor equal to window ADR ($106.72 City, $95.29 Resort) during Low months to prevent rate dilution, combined with a 10% rate premium on peak dates exceeding 90% capacity [`reports/insights/01_pricing_seasonality.md`]. For City Hotel, applying this 10% premium across 22 peak nights yields $58,023.37 in incremental revenue [`reports/findings_data.json`, `hotel_benchmarks.City Hotel.peak_nights_revenue`].

### Q25: What technical and analytical steps would you prioritize next?
**Answer:** I would prioritize three initiatives: (1) deploy a machine learning dynamic pricing model incorporating competitor rate scraping and price elasticity curves; (2) build an automated Kafka or webhook ingestion pipeline from the property management system for real-time cancellation alerts; and (3) launch an A/B test enforcing tiered deposits on bookings with lead times over 90 days to reduce late inventory spoilage.

---

## Questions This Data Cannot Answer

While the dataset provides rich transactional detail across 119,388 bookings, several key commercial and operational questions cannot be answered from these administrative PMS records alone:

1. **Website Acquisition & Funnel Conversion**:  
   The data begins only after a reservation is confirmed. It contains no web session logs, impressions, cart abandonment metrics, or conversion funnel stages. "Stay conversion" represents booking completion, not acquisition conversion.

2. **True Physical Room Inventory & Room Grade Hierarchy**:  
   There is no architectural room count or floor plan in the data. Capacity had to be derived from peak observed room-nights sold. Furthermore, room codes (A through L) are anonymous; the data cannot determine whether an assigned room change was an upgrade or a downgrade.

3. **Realized Cash Collections from Forfeited Deposits**:  
   Although 14,586 bookings were labeled 'Non Refund', the database contains no accounting ledger entries or merchant processing records showing whether forfeiture fees were collected, waived, or refunded.

4. **Walk / Relocation Costs and Guest Compensation**:  
   No financial data exists regarding the actual operational expense of walking an overbooked guest to an alternative hotel, paying taxi vouchers, or issuing guest service recovery compensation.

5. **Price Elasticity of Demand**:  
   Because rate quotes and unbooked search availability are absent, customer sensitivity to price changes cannot be estimated directly from historical transaction prices.
