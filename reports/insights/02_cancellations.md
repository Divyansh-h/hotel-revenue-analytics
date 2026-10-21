# Strategic Revenue Insights: Cancellation Patterns, Deposit Policies & Timing Risk

> [!NOTE]
> **Data Integrity and Rule Governance**:
> This report has been compiled in strict adherence to **Global Rule R1** and **Project Context**. Every metric, baseline, statistical test statistic, effect size, and scenario input is derived directly from physical data outputs saved on disk in `data/outputs/*.csv`, `reports/tables/stat_tests_summary.csv`, and validated in [`reports/findings_data.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/reports/findings_data.json). No numbers have been estimated, forecasted, or typed by hand.
>
> All causal claims have been intentionally excluded: per instructions, only empirical statistical association language ("is associated with", "correlates positively with", "is concentrated in") is employed.

---

## Insight (a): Lead Time and Cancellation Dynamics

### 1. Finding
Advance booking lead time is strongly and positively associated with cancellation risk across the portfolio:

1. **Monotonic Risk Escalation Across Lead Buckets**:
   - Booking cancellation rates escalate monotonically as lead time extends, displaying a near 6-fold increase from the shortest to longest booking horizons [`v_cancellation_drivers.csv`, category = 'lead_bucket'].
   - Reservations booked within **0-7 days** of arrival exhibit a cancellation rate of only **9.63%** (9.6%) [`v_cancellation_drivers.csv`, cancel_rate_pct].
   - Cancellation rates climb steadily to **27.86%** (27.9%) in the **8-30 days** bucket, **37.70%** (37.7%) in the **31-90 days** bucket, and **44.71%** (44.7%) in the **91-180 days** bucket [`v_cancellation_drivers.csv`, cancel_rate_pct].
   - Bookings made more than six months in advance (**181+ days**) experience the highest cancellation rate at **57.01%** (57.0%), representing more than one in every two reservations made [`v_cancellation_drivers.csv`, cancel_rate_pct].

2. **Continuous Advance Booking Window Divergence**:
   - Examining continuous lead time reveals a stark distribution shift: reservations that ended in cancellation had a median advance booking window of **113.0 days**, compared with **45.0 days** for non-canceled reservations that resulted in realized guest check-outs [`reports/tables/stat_tests_summary.csv`, test_id = 'T4'].
   - This represents a median lead time shift of **+68.0 days** (+151.1%) between canceled and non-canceled bookings [`reports/tables/stat_tests_summary.csv`, test_id = 'T4'].
   - The probability that a randomly selected canceled reservation had a longer advance booking horizon than a randomly selected non-canceled stay is **68.9%** (common language effect size) [`reports/tables/stat_tests_summary.csv`, test_id = 'T4'].

3. **Substantial Inventory Exposure**:
   - Within the **181+ days** lead bucket alone, **14,077 bookings** were canceled, accounting for **49,889 room-nights** and **$4,775,283.00** in potential room revenue at an average ADR of **$95.72** [`reports/findings_data.json`, cancellations.lead_time.scenario_181_plus_reduction_10pct.inputs].

---

### 2. Evidence
Every figure below is sourced directly from physical CSV files on disk and indexed in [`reports/findings_data.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/reports/findings_data.json) and [`reports/tables/stat_tests_summary.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/reports/tables/stat_tests_summary.csv):

#### Cancellation Rates by Lead Time Bucket (`v_cancellation_drivers.csv`)
| Lead Time Bucket | Bucket Order | Total Bookings | Cancellations | Cancel Rate % | Portfolio Share % | Variance vs Hotel Avg (pp) | Source Tag |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0-7 days** | 1.0 | 19,746 | 1,902 | **9.63%** | 16.54% | -27.4 pp | `[v_cancellation_drivers.csv, cancel_rate_pct]` |
| **8-30 days** | 2.0 | 18,960 | 5,283 | **27.86%** | 15.88% | -9.2 pp | `[v_cancellation_drivers.csv, cancel_rate_pct]` |
| **31-90 days** | 3.0 | 29,552 | 11,140 | **37.70%** | 24.75% | +0.7 pp | `[v_cancellation_drivers.csv, cancel_rate_pct]` |
| **91-180 days** | 4.0 | 26,439 | 11,821 | **44.71%** | 22.15% | +7.7 pp | `[v_cancellation_drivers.csv, cancel_rate_pct]` |
| **181+ days** | 5.0 | 24,691 | 14,077 | **57.01%** | 20.68% | +20.0 pp | `[v_cancellation_drivers.csv, cancel_rate_pct]` |
| **All Bookings** | — | **119,388** | **44,223** | **37.04%** | **100.00%** | 0.0 pp | `[v_cancellation_drivers.csv, bookings]` |

#### Property-Specific Lead Bucket Progression (`v_lead_deposit_matrix.csv`)
| Hotel | Lead Bucket | Total Bookings | Cancellations | Cancel Rate % | Hotel Booking Share % | Source Tag |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **City Hotel** | 0-7 days | 10,808 | 1,319 | **12.20%** | 13.62% | `[v_lead_deposit_matrix.csv, cancel_rate_pct]` |
| City Hotel | 8-30 days | 12,554 | 3,880 | **30.91%** | 15.83% | `[v_lead_deposit_matrix.csv, cancel_rate_pct]` |
| City Hotel | 31-90 days | 20,796 | 8,299 | **39.91%** | 26.22% | `[v_lead_deposit_matrix.csv, cancel_rate_pct]` |
| City Hotel | 91-180 days | 18,223 | 8,746 | **47.99%** | 22.97% | `[v_lead_deposit_matrix.csv, cancel_rate_pct]` |
| City Hotel | 181+ days | 16,948 | 10,857 | **64.06%** | 21.36% | `[v_lead_deposit_matrix.csv, cancel_rate_pct]` |
| **Resort Hotel** | 0-7 days | 8,938 | 583 | **6.52%** | 22.31% | `[v_lead_deposit_matrix.csv, cancel_rate_pct]` |
| Resort Hotel | 8-30 days | 6,406 | 1,403 | **21.90%** | 15.99% | `[v_lead_deposit_matrix.csv, cancel_rate_pct]` |
| Resort Hotel | 31-90 days | 8,756 | 2,841 | **32.45%** | 21.86% | `[v_lead_deposit_matrix.csv, cancel_rate_pct]` |
| Resort Hotel | 91-180 days | 8,216 | 3,075 | **37.43%** | 20.51% | `[v_lead_deposit_matrix.csv, cancel_rate_pct]` |
| Resort Hotel | 181+ days | 7,743 | 3,220 | **41.59%** | 19.33% | `[v_lead_deposit_matrix.csv, cancel_rate_pct]` |

#### Inferential Statistical Test Results (`reports/tables/stat_tests_summary.csv`)
1. **Test T3 (Chi-Square Test of Independence: Lead Bucket vs Cancellation)**:
   - Sample Scope: Full clean analytical dataset ($N = 119,388$)
   - Test Statistic: $\chi^2 = 11,940.86$, Degrees of Freedom: $df = 4$, $p$-value: $< 1 \times 10^{-300}$ [`reports/tables/stat_tests_summary.csv`, test_id = 'T3']
   - Effect Size: Cramer's $V = 0.3163$ (indicates a statistically significant, moderate-to-strong association between lead time bucket and cancellation status) [`reports/tables/stat_tests_summary.csv`, test_id = 'T3']
2. **Test T4 (Mann-Whitney U Test: Continuous Lead Time by Cancellation Status)**:
   - Sample Scope: Full clean analytical dataset ($N = 119,388$; 44,223 canceled, 75,165 non-canceled)
   - Test Statistic: $U = 2,291,139,948$, $p$-value: $< 1 \times 10^{-300}$ [`reports/tables/stat_tests_summary.csv`, test_id = 'T4']
   - Effect Size: Rank-biserial correlation $r_{\text{rb}} = 0.3785$; Median canceled lead time = **113.0 days** vs non-canceled = **45.0 days** (median shift of **+68.0 days**) [`reports/tables/stat_tests_summary.csv`, test_id = 'T4']
   - Methodological note: Independent samples $t$-test is invalidated in the presence of severe positive skewness of lead time distributions.
3. **Test T6.3 (Robustness Check on Deduplicated Data)**:
   - Sample Scope: Non-duplicate reservations ($N = 87,394$, excluding 31,994 flagged duplicates)
   - Test Statistic: $\chi^2 = 5,005.16$, $df = 4$, $p$-value: $< 1 \times 10^{-300}$, Cramer's $V = 0.2393$ [`reports/tables/stat_tests_summary.csv`, test_id = 'T6.3']
   - Finding: Monotonic climb persists robustly, scaling from **8.43%** in `0-7` days to **39.74%** in `181+` days.

---

### 3. Recommended Action
1. **Tiered Advance Deposit Requirements**:
   - Replace open, zero-deposit terms on long-lead bookings with a structured advance payment policy:
     - For bookings made $\ge 91$ days in advance: require a **20% deposit** at 90 days before arrival and an additional **30% guarantee** at 30 days before arrival.
     - For bookings made $\ge 181$ days in advance: require a **25% advance commitment** at booking confirmation.
2. **Automated Digital Reconfirmation Milestones**:
   - Establish automated digital reconfirmation touchpoints (via email, SMS, or WhatsApp integration) triggered at **90 days, 60 days, and 30 days** before arrival.
   - Require guests or booking intermediaries to reconfirm stay dates, submit guest names, or re-verify payment credentials.
   - *Inventory Release Rule*: If an unconfirmed long-lead reservation receives no response after 7 business days and two reminders, initiate automated release of the held room back into live inventory for resale to short-lead channels.

---

### 4. Expected Impact (As a Scenario)

> [!WARNING]
> **Scenario, not forecast**:
> The calculations below represent analytical scenarios based on explicit historical data points. State caveat: higher prices would probably reduce occupancy and that the dataset cannot measure price elasticity. Additionally, imposing deposits on long-lead bookings might reduce total booking volume, and this dataset cannot observe lost bookings from potential customer friction.

#### Scenario A1: 10% Reduction in Long-Lead (181+ Days) Cancellations via Tiered Deposits & Reconfirmation
- **Formula**:
  $$\Delta \text{Cancellations Avoided} = \text{Cancellations}_{181+} \times 0.10$$
  $$\text{Preserved Room Nights} = \text{Canceled Room Nights}_{181+} \times 0.10$$
  $$\text{Preserved Potential Revenue} = \text{Canceled Revenue}_{181+} \times 0.10$$
- **Data Inputs** [`reports/findings_data.json`, cancellations.lead_time.scenario_181_plus_reduction_10pct]:
  - Historical cancellations in `181+` bucket: **14,077 bookings** [`v_cancellation_drivers.csv`, category = '181+']
  - Historical room nights in `181+` cancellations: **49,889 nights** [`reports/findings_data.json`]
  - Historical potential revenue in `181+` cancellations: **$4,775,283.00** [`reports/findings_data.json`]
  - Baseline ADR of canceled long-lead bookings: **$95.72**
  - Scenario reduction factor: **10.0%** ($0.10$)
- **Calculation**:
  $$\Delta \text{Cancellations Avoided} = 14,077 \times 0.10 = \mathbf{1,407.7 \text{ bookings}}$$
  $$\text{Preserved Room Nights} = 49,889 \times 0.10 = \mathbf{4,988.9 \text{ room-nights}}$$
  $$\text{Preserved Potential Revenue} = \$4,775,283.00 \times 0.10 = \mathbf{\$477,528.30}$$
- **Scenario Result**:
  If tiered deposits and reconfirmation protocols reduced long-lead cancellations by 10% with other booking behaviors held constant, the hotel group would avoid **1,407.7 cancellations**, protecting **4,988.9 room-nights** and **$477,528.30** in potential room revenue across the analytical window.

---

## Insight (b): Deposit Policy & The Non Refund Paradox

### 1. Finding
An empirical audit of cancellation rates across deposit types reveals an extreme, counter-intuitive distortion:

1. **Deposit Type Cancellation Distribution**:
   - **No Deposit**: 104,640 bookings, 29,694 cancellations, cancellation rate of **28.38%** (28.4%) [`v_cancellation_drivers.csv`, category = 'No Deposit'].
   - **Refundable**: 162 bookings, 36 cancellations, cancellation rate of **22.22%** (22.2%) [`v_cancellation_drivers.csv`, category = 'Refundable'].
   - **Non Refund**: 14,586 bookings, 14,493 cancellations, cancellation rate of **99.36%** (99.4%) [`v_cancellation_drivers.csv`, category = 'Non Refund'].

2. **The Counter-Intuitive Paradox**:
   - Economically and contractually, a non-refundable deposit policy is engineered to eliminate or drastically deter cancellations by imposing complete financial forfeiture upon reservation withdrawal.
   - Observing that **99.36%** of all Non Refund reservations cancel is completely counter-intuitive. In a standard consumer setting, guests do not systematically purchase non-refundable rooms with the intent of forfeiting 100% of their payment.
   - Strictly adhering to analytical objectivity, **we do NOT explain this phenomenon with unverified claims**. Instead, we cross-tabulate Non Refund reservations across key commercial dimensions to isolate where this pattern is concentrated, and present hypotheses for technical and commercial investigation.

3. **Empirical Concentration Profile**:
   Cross-tabulating the 14,586 Non Refund bookings reveals that this phenomenon is not distributed evenly across normal retail guest channels, but is concentrated in specific commercial segments:
   - **Market Segment**: **97.19%** of all Non Refund reservations are concentrated in two wholesale segments: **Groups (62.88%, 9,172 bookings)** and **Offline TA/TO (34.31%, 5,005 bookings)** [`reports/findings_data.json`]. Individual retail segments account for almost none (Online TA: 0.38%, Direct: 0.13%).
   - **Distribution Channel**: **93.58%** (13,650 bookings) originated through the **TA/TO (Travel Agent / Tour Operator)** channel [`reports/findings_data.json`].
   - **Geographic Origin**: **97.18%** (14,175 bookings) originated from a single country: **Portugal (PRT)** [`reports/findings_data.json`].
   - **Property**: **88.21%** (12,867 bookings) were booked at **City Hotel** (Lisbon) [`reports/findings_data.json`].

4. **Investigative Hypotheses (Not Verified Facts)**:
   The empirical concentration in domestic Portuguese wholesale tour operator group blocks suggests three hypotheses to investigate:
   - *Hypothesis 1 (PMS Recording Artefact / Default Classification)*: The hotel's Property Management System (PMS) or central reservation interface may have automatically assigned the label `Non Refund` to cancelled wholesale block allocations upon cancellation, or defaulted non-guaranteed dropped allocations to `Non Refund` in database tables.
   - *Hypothesis 2 (Wholesale Tour Operator Block Option Releases)*: Domestic Portuguese tour operators contracted room blocks under negotiated non-refundable contract templates, but released unsold rooms back to the property without financial settlement prior to arrival cutoff dates without actual individual guest penalties.
   - *Hypothesis 3 (Duplicate Reservation Generation / Synthetic Records)*: Automated booking interfaces or wholesale agents may have created repeated speculative booking passes that were bulk-cancelled, inflating cancellation tallies with synthetic records (supported by the fact that deduplication eliminates 92.9% of Non Refund bookings, reducing count from 14,586 to 1,037 in Test T6.2).

---

### 2. Evidence

#### Deposit Type Cancellation Breakdown (`v_cancellation_drivers.csv`)
| Deposit Type | Total Bookings | Cancellations | No-Shows | Cancel Rate % | Portfolio Share % | Variance vs Avg (pp) | Source Tag |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **No Deposit** | 104,640 | 29,694 | 1,172 | **28.38%** | 87.65% | -8.7 pp | `[v_cancellation_drivers.csv, category = 'No Deposit']` |
| **Refundable** | 162 | 36 | 1 | **22.22%** | 0.14% | -14.8 pp | `[v_cancellation_drivers.csv, category = 'Refundable']` |
| **Non Refund** | 14,586 | 14,493 | 34 | **99.36%** | 12.22% | +62.3 pp | `[v_cancellation_drivers.csv, category = 'Non Refund']` |

#### Non Refund Cross-Tabulations ($N = 14,586$ Bookings)
1. **By Market Segment** [`reports/findings_data.json`, cancellations.deposit_type.non_refund_cross_tabulations.market_segment]:
   - **Groups**: 9,172 bookings (**62.88%** share of Non Refund), 9,110 cancellations (**99.32%** cancel rate).
   - **Offline TA/TO**: 5,005 bookings (**34.31%** share), 5,002 cancellations (**99.94%** cancel rate).
   - **Corporate**: 334 bookings (**2.29%** share), 312 cancellations (**93.41%** cancel rate).
   - **Online TA**: 56 bookings (**0.38%** share), 53 cancellations (**94.64%** cancel rate).
   - **Direct**: 19 bookings (**0.13%** share), 16 cancellations (**84.21%** cancel rate).
2. **By Distribution Channel** [`reports/findings_data.json`, cancellations.deposit_type.non_refund_cross_tabulations.distribution_channel]:
   - **TA/TO**: 13,650 bookings (**93.58%** share of Non Refund), 13,597 cancellations (**99.61%** cancel rate).
   - **Corporate**: 538 bookings (**3.69%** share), 508 cancellations (**94.42%** cancel rate).
   - **Direct**: 398 bookings (**2.73%** share), 388 cancellations (**97.49%** cancel rate).
3. **By Guest Origin Country** [`reports/findings_data.json`, cancellations.deposit_type.non_refund_cross_tabulations.top_countries]:
   - **Portugal (PRT)**: 14,175 bookings (**97.18%** share of Non Refund), 14,139 cancellations (**99.75%** cancel rate).
   - **United Kingdom (GBR)**: 138 bookings (**0.95%** share), 132 cancellations (**95.65%** cancel rate).
   - **Spain (ESP)**: 131 bookings (**0.90%** share), 131 cancellations (**100.00%** cancel rate).
   - **Germany (DEU)**: 44 bookings (**0.30%** share), 1 cancellation (**2.27%** cancel rate).
   - **Poland (POL)**: 38 bookings (**0.26%** share), 37 cancellations (**97.37%** cancel rate).
4. **By Hotel Property** [`reports/findings_data.json`, cancellations.deposit_type.non_refund_cross_tabulations.hotel]:
   - **City Hotel**: 12,867 bookings (**88.21%** share of Non Refund), 12,843 cancellations (**99.81%** cancel rate).
   - **Resort Hotel**: 1,719 bookings (**11.79%** share), 1,650 cancellations (**95.99%** cancel rate).

#### Statistical Test & Modeling Evidence
- **Test T2 (Chi-Square Test of Independence)**: $N = 119,388$, $\chi^2 = 27,675.45$, $df = 2$, $p < 1 \times 10^{-300}$, Cramer's $V = 0.4815$ (strongest bivariate association in dataset) [`reports/tables/stat_tests_summary.csv`, test_id = 'T2'].
- **Test T5 (Multiple Logistic Regression)**: Holding lead time, repeated guest status, segment, and previous cancellations constant, the adjusted odds ratio for `deposit_type = Non Refund` is $\text{OR} = 278.2$ (95% CI: $[225.9, 342.7]$, $p < 1 \times 10^{-300}$) [`reports/tables/stat_tests_summary.csv`, test_id = 'T5']. Note: This reflects statistical association within administrative records, not behavioral causation.
- **Test T6.2 (Deduplication Robustness)**: In deduplicated data ($N = 87,394$), Non Refund volume drops by 92.9% to 1,037 bookings, but **982 cancel** (**94.70%** cancel rate vs **26.69%** for No Deposit), $\chi^2 = 2,378.38$, $df = 2$, $V = 0.1650$ [`reports/tables/stat_tests_summary.csv`, test_id = 'T6.2'].
- **Associated Volume**: The 14,493 canceled Non Refund bookings represent **39,358 room-nights** and **$3,598,937.03** in potential room revenue at an average ADR of **$91.44** [`reports/findings_data.json`].

---

### 3. Recommended Action
1. **Audit PMS & Channel Manager Logging**:
   - Commission an immediate technical audit of the reservation interface between the hotel PMS (e.g., Opera/Protel) and Portuguese wholesale channel managers to verify whether cancelled group blocks are systematically tagged as Non Refund records upon status transition.
2. **Re-evaluate Wholesale Allotment Agreements**:
   - Replace unmonitored non-refundable group allocation codes with structured deposit-backed cut-off contracts, enforcing strict attrition thresholds and rolling cancellation release milestones (e.g. 60-day, 30-day, 14-day cutoffs) so unsold inventory is systematically returned to transient channels.
3. **Establish Contractual Deposit Collection Protocols**:
   - Review commercial contract terms with domestic Portuguese wholesale travel agencies to confirm whether contractual deposits are actually being collected and credited, or whether blocks are dropped without financial forfeiture.

---

### 4. Expected Impact (As a Scenario)

> [!WARNING]
> **Scenario, not forecast**:
> The calculations below represent analytical scenarios based on explicit historical data points. State caveat: higher prices would probably reduce occupancy and that the dataset cannot measure price elasticity. Furthermore, this scenario assumes that un-cancelled group allocations represent genuine room demand that would be paid or resold at historical baseline rates, which cannot be confirmed without verifying whether historical deposits were actually collected.

#### Scenario B1: 10% Recovery of Canceled Non Refund Group Allocations via Contract Reform
- **Formula**:
  $$\Delta \text{Cancellations Recovered} = \text{Non Refund Cancellations} \times 0.10$$
  $$\text{Preserved Room Nights} = \text{Canceled Room Nights}_{\text{Non Refund}} \times 0.10$$
  $$\text{Preserved Potential Revenue} = \text{Canceled Revenue}_{\text{Non Refund}} \times 0.10$$
- **Data Inputs** [`reports/findings_data.json`, cancellations.deposit_type.scenario_non_refund_reform_10pct]:
  - Historical Non Refund cancellations: **14,493 bookings** [`v_cancellation_drivers.csv`, category = 'Non Refund']
  - Historical room nights in Non Refund cancellations: **39,358 nights** [`reports/findings_data.json`]
  - Historical potential revenue in Non Refund cancellations: **$3,598,937.03** [`reports/findings_data.json`]
  - Baseline ADR: **$91.44**
  - Scenario recovery factor: **10.0%** ($0.10$)
- **Calculation**:
  $$\Delta \text{Cancellations Recovered} = 14,493 \times 0.10 = \mathbf{1,449.3 \text{ bookings}}$$
  $$\text{Preserved Room Nights} = 39,358 \times 0.10 = \mathbf{3,935.8 \text{ room-nights}}$$
  $$\text{Preserved Potential Revenue} = \$3,598,937.03 \times 0.10 = \mathbf{\$359,893.70}$$
- **Scenario Result**:
  If administrative and contractual audits eliminated or recovered 10% of these phantom wholesale cancellations, the property group would reclaim **1,449.3 bookings**, freeing up **3,935.8 room-nights** and recovering **$359,893.70** in potential room revenue across the analytical window.

---

## Insight (c): Cancellation Timing & Late Revenue Risk

### 1. Finding
An analysis of cancellation timing relative to scheduled guest arrival reveals significant late-stage revenue exposure:

1. **Share of Cancellations Within 7 Days of Arrival**:
   - Of all 43,016 cancellations with recorded status dates, **11.9%** (11.94%) occur within **7 days of arrival** [`v_cancel_timing.csv`].
   - Specifically, **3.5%** of all timed cancellations (1,511 bookings) occur within **0-1 days** of arrival (same-day or day-before cancellations), and **8.4%** (3,624 bookings) occur between **2-7 days** prior to arrival [`v_cancel_timing.csv`].
   - Across the entire dataset (including 1,208 no-shows with null status intervals), these **5,135 late cancellations** represent **11.61%** of all canceled reservations [`v_late_cancel_revenue_at_risk.csv`].

2. **Perishable Inventory Spoilage**:
   - As these reservations are dropped within 7 days of scheduled arrival, the hotel's revenue management team has virtually no advance window to remarket, discount, or resell the vacated room nights, directly depressing realized occupancy and RevPAR.

3. **Upper-Bound Revenue at Risk**:
   - Across all 26 arrival months, late cancellations within 7 days placed an aggregate of **$1,533,486.66** in upper-bound room revenue at risk [`v_late_cancel_revenue_at_risk.csv`, late_cancel_revenue_at_risk].
   - This upper-bound revenue at risk represents **3.59%** of the portfolio's total potential booking revenue of **$42,718,161.33** [`v_late_cancel_revenue_at_risk.csv`].
   - These 5,135 late cancellations represent **14,841 perishable room-nights** with an average length of stay of **2.89 nights** and a blended ADR of **$103.33** [`reports/findings_data.json`].

4. **Property Concentration**:
   - **City Hotel** bears the overwhelming burden of late cancellations: **3,870 late cancellations** (**75.36%** of all late cancellations), putting **10,864 room nights** and **$1,167,162.59** in revenue at risk (ADR $107.43) [`reports/findings_data.json`].
   - **Resort Hotel** accounts for **1,265 late cancellations** (**24.64%**), representing **3,977 room nights** and **$366,324.07** in revenue at risk (ADR $92.11) [`reports/findings_data.json`].

---

### 2. Evidence

#### Timing Distribution of Cancellations (`v_cancel_timing.csv`)
| Timing Bucket | Sort Order | Cancellations | Share of Cancellations % | Avg Lead Time (days) | Avg Days Cancelled Before Arrival | Room Revenue at Risk ($) | Source Tag |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0-1 days** | 1 | 1,511 | **3.5%** | 34.7 | 0.4 | $371,881.76 | `[v_cancel_timing.csv, room_revenue_at_risk]` |
| **2-7 days** | 2 | 3,624 | **8.4%** | 59.6 | 4.5 | $1,161,604.90 | `[v_cancel_timing.csv, room_revenue_at_risk]` |
| **8-14 days** | 3 | 3,441 | **8.0%** | 77.0 | 11.0 | $1,305,296.09 | `[v_cancel_timing.csv, room_revenue_at_risk]` |
| **15-30 days** | 4 | 5,926 | **13.8%** | 89.4 | 21.6 | $2,317,465.12 | `[v_cancel_timing.csv, room_revenue_at_risk]` |
| **31-60 days** | 5 | 8,070 | **18.8%** | 116.2 | 44.5 | $3,013,591.21 | `[v_cancel_timing.csv, room_revenue_at_risk]` |
| **61-90 days** | 6 | 4,896 | **11.4%** | 143.7 | 74.1 | $1,957,516.27 | `[v_cancel_timing.csv, room_revenue_at_risk]` |
| **91+ days** | 7 | 15,548 | **36.1%** | 233.6 | 186.1 | $6,145,000.76 | `[v_cancel_timing.csv, room_revenue_at_risk]` |
| **Late (0-7d Subtotal)** | — | **5,135** | **11.9%** | — | — | **$1,533,486.66** | `[v_cancel_timing.csv, timing_bucket]` |

#### Late Cancellation Revenue at Risk Summary (`v_late_cancel_revenue_at_risk.csv`)
| Entity Scope | Total Bookings | Total Cancellations | Late Cancellations ($\le 7$d) | Late Room Nights | Revenue at Risk Upper Bound ($) | Total Potential Revenue ($) | Pct Revenue at Risk | Source Tag |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **City Hotel** | 79,330 | 33,102 | **3,870** | 10,864 | **$1,167,162.59** | $25,274,069.96 | 4.62% | `[v_late_cancel_revenue_at_risk.csv, late_cancel_revenue_at_risk]` |
| **Resort Hotel** | 40,058 | 11,121 | **1,265** | 3,977 | **$366,324.07** | $17,444,091.37 | 2.10% | `[v_late_cancel_revenue_at_risk.csv, late_cancel_revenue_at_risk]` |
| **All Hotels** | **119,388** | **44,223** | **5,135** | **14,841** | **$1,533,486.66** | **$42,718,161.33** | **3.59%** | `[v_late_cancel_revenue_at_risk.csv, late_cancel_revenue_at_risk]` |

---

### 3. Recommended Action
1. **Automated 72-to-48-Hour Pre-Arrival Reconfirmation Call / Message**:
   - Deploy automated pre-stay messaging via SMS, email, or WhatsApp sent 48–72 hours prior to check-in, prompting guests to re-confirm estimated arrival time and re-validate payment credentials.
   - For non-responsive reservations on peak dates, initiate personalized concierge outreach to identify soft bookings before arrival day.
2. **Standard 7-Day Cancellation Window**:
   - Tighten standard transient cancellation terms from same-day / 24-hour flexibility to a **7-day cancellation window**.
   - Enforce a **1-night room rate cancellation fee** for reservations cancelled inside the 7-day window. This policy creates financial protection against late spoilage and incentivizes uncommitted travelers to release inventory earlier, allowing revenue managers to resell rooms to last-minute channels.

---

### 4. Expected Impact (As a Scenario)

> [!WARNING]
> **Scenario, not forecast**:
> The calculations below represent analytical scenarios based on explicit historical baseline data. State caveat: higher prices would probably reduce occupancy and that the dataset cannot measure price elasticity. Furthermore, revenue-at-risk calculations represent an upper bound assuming that un-cancelled rooms would have been occupied and paid in full without refund, and do not account for whether vacated rooms were partially re-booked or resold by walk-in or last-minute channels.

#### Scenario C1: 10% Reduction in Late Cancellations ($\le 7$ Days) via Pre-Arrival Reconfirmation & 7-Day Window
- **Formula**:
  $$\Delta \text{Late Cancellations Avoided} = \text{Late Cancellations}_{7\text{d}} \times 0.10$$
  $$\Delta \text{Room Nights Covered} = \text{Late Room Nights} \times 0.10$$
  $$\Delta \text{Upper Bound Revenue Covered} = \text{Late Cancel Revenue at Risk} \times 0.10$$
- **Data Inputs** [`v_late_cancel_revenue_at_risk.csv`, late_cancel_revenue_at_risk; `reports/findings_data.json`]:
  - Total late cancellations within 7 days: **5,135 bookings** [`v_late_cancel_revenue_at_risk.csv`, late_cancellations_7d]
  - Total late room nights: **14,841 room-nights** [`reports/findings_data.json`]
  - Total upper-bound revenue at risk: **$1,533,486.66** [`v_late_cancel_revenue_at_risk.csv`, late_cancel_revenue_at_risk]
  - Scenario reduction factor: **10.0%** ($0.10$)
- **Calculation**:
  - **Portfolio Total**:
    $$\Delta \text{Late Cancellations Avoided} = 5,135 \times 0.10 = \mathbf{513.5 \text{ bookings}}$$
    $$\Delta \text{Room Nights Covered} = 14,841 \times 0.10 = \mathbf{1,484.1 \text{ room-nights}}$$
    $$\Delta \text{Upper Bound Revenue Covered} = \$1,533,486.66 \times 0.10 = \mathbf{\$153,348.67}$$
  - **Property Breakdown**:
    - **City Hotel**:
      $$\Delta \text{Late Cancellations} = 3,870 \times 0.10 = \mathbf{387.0 \text{ bookings}}$$
      $$\Delta \text{Room Nights} = 10,864 \times 0.10 = \mathbf{1,086.4 \text{ room-nights}}$$
      $$\Delta \text{Revenue Covered} = \$1,167,162.59 \times 0.10 = \mathbf{\$116,716.26}$$
    - **Resort Hotel**:
      $$\Delta \text{Late Cancellations} = 1,265 \times 0.10 = \mathbf{126.5 \text{ bookings}}$$
      $$\Delta \text{Room Nights} = 3,977 \times 0.10 = \mathbf{397.7 \text{ room-nights}}$$
      $$\Delta \text{Revenue Covered} = \$366,324.07 \times 0.10 = \mathbf{\$36,632.41}$$
- **Scenario Result**:
  If pre-arrival reconfirmation and a structured 7-day cancellation window reduced late cancellations by 10%, the property group would prevent **513.5 late cancellations**, covering **1,484.1 perishable room-nights** and **$153,348.67** of upper-bound revenue at risk ($116,716.26 at City Hotel and $36,632.41 at Resort Hotel).

---

## Analytical Summary Table: Cancellation Decisions & Scenario Payoffs

| Scenario ID | Focus Dimension | Target Cohort | Baseline Volume | Baseline Exposure ($) | Policy Mechanism | Realized Coverage / Payoff ($) | Key Operational Caveat | Source Tag |
| :--- | :--- | :--- | :---: | :---: | :--- | :---: | :--- | :--- |
| **Scenario A1** | Lead Time Dynamics | Bookings $\ge 181$ days lead | 14,077 cancellations | $4,775,283.00 | Tiered deposits (25% hold) & 90/60/30d reconfirmation | **+$477,528.30** (4,988.9 room-nights) | Scenario, not forecast; customer booking friction unknown | `[reports/findings_data.json, cancellations.lead_time]` |
| **Scenario B1** | Deposit Policy | Non Refund cancellations | 14,493 cancellations | $3,598,937.03 | PMS logging audit & wholesale allocation cutoffs | **+$359,893.70** (3,935.8 room-nights) | Scenario, not forecast; relies on recovering phantom blocks | `[reports/findings_data.json, cancellations.deposit_type]` |
| **Scenario C1** | Cancellation Timing | Cancellations $\le 7$ days | 5,135 cancellations | $1,533,486.66 | 48h reconfirmation outreach & 7-day cancellation window | **+$153,348.67** (1,484.1 room-nights) | Scenario, not forecast; assumes zero replacement bookings | `[reports/findings_data.json, cancellations.timing]` |
