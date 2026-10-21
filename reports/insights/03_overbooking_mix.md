# Strategic Revenue Insights: Overbooking Buffers, Walk-Risk Signals & Commercial Mix

> [!NOTE]
> **Data Integrity and Rule Governance**:
> This report has been compiled in strict adherence to **Global Rule R1** and **Project Context**. Every metric, baseline, buffer calculation, and scenario input is derived directly from physical data outputs saved on disk in `data/outputs/*.csv` and validated in [`reports/findings_data.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/reports/findings_data.json). No numbers have been estimated, forecasted, or typed by hand.
>
> In accordance with **Rule K7**, commercial market segments and distribution channels are evaluated exclusively using room-night share, revenue share, realized ADR, and cancellation rates. **Segment-level occupancy and RevPAR do not exist and are not reported**, as physical room inventory and capacity exist strictly at the property level.

---

## Insight (a): Overbooking Buffer & Capacity Protection

### 1. Finding
Overbooking is an essential yield management mechanism to protect against inventory spoilage associated with cancellations and no-shows, but it must be calibrated conservatively to avoid catastrophic guest walking:

1. **Methodology Behind `v_overbooking_buffer`**:
   - The view [`v_overbooking_buffer.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/data/outputs/v_overbooking_buffer.csv) is derived from daily arrival cohorts in `v_daily_cancel_rates`, filtering strictly for dates with **$\ge 20$ arrivals** to ensure sample stability.
   - For each hotel and calendar month number (1 to 12), the daily cancellation rate distribution is evaluated across historical dates:
     - `median_daily_cancel_rate`: The 50th percentile of observed daily cancellation rates.
     - `conservative_rate`: The **10th percentile** (`PERCENTILE_CONT(0.10)`) of observed daily cancellation rates.
   - *Statistical Rationale for the 10th Percentile*: The 10th percentile represents a conservative lower bound: on **90% of observed days**, the actual realized cancellation rate was *at least* this high. Historically, there is only a 10% risk that fewer guests cancel than this threshold.

2. **Conservative Cancellation Rates & Capacity Conversion**:
   Using the assumed physical capacities derived under Rule W2 (**250 rooms** for City Hotel and **210 rooms** for Resort Hotel) [`capacity.csv`, rooms]:
   - **City Hotel (Capacity = 250 rooms)**:
     - Monthly conservative rates range from **11.13% in October (27.8 rooms, round to 28 rooms)** to **27.09% in April (67.7 rooms, round to 68 rooms)** [`v_overbooking_buffer.csv`, conservative_rate].
     - The unweighted annual mean conservative rate is **18.69%** (18.7%), which corresponds to an average buffer of **46.7 rooms** (round to 47 rooms) [`reports/findings_data.json`, overbooking_and_mix.overbooking_buffer.City Hotel].
     - In contrast, the median daily cancellation rate averages **35.84%** (89.6 rooms), ranging from 28.32% in November to 41.79% in June [`v_overbooking_buffer.csv`, median_daily_cancel_rate].
   - **Resort Hotel (Capacity = 210 rooms)**:
     - Monthly conservative rates range from **2.79% in November (5.9 rooms, round to 6 rooms)** to **20.19% in June (42.4 rooms, round to 42 rooms)** [`v_overbooking_buffer.csv`, conservative_rate].
     - The unweighted annual mean conservative rate is **10.78%** (10.8%), corresponding to an average buffer of **22.6 rooms** (round to 23 rooms) [`reports/findings_data.json`, overbooking_and_mix.overbooking_buffer.Resort Hotel].
     - The median daily cancellation rate averages **23.25%** (48.8 rooms), ranging from 12.12% in January to 32.69% in August [`v_overbooking_buffer.csv`, median_daily_cancel_rate].

3. **Recommended Starting Pilot Buffer: HALF the Conservative Rate**:
   - Rather than overbooking to the full 10th percentile (which still carries a 10% probability of overselling), management should institute a pilot overbooking policy capped at **HALF the conservative rate**:
     - **City Hotel Pilot Buffer**: Half of 18.69% = **9.35%** (an average of **23.4 rooms**, round to **23 rooms**; monthly range: **14 to 34 rooms**) [`reports/findings_data.json`].
     - **Resort Hotel Pilot Buffer**: Half of 10.78% = **5.39%** (an average of **11.3 rooms**, round to **11 rooms**; monthly range: **3 to 21 rooms**) [`reports/findings_data.json`].
   - *Why Half? Critical Operational Constraints*:
     1. *Zero Walk and Compensation Cost Data*: The dataset contains no records of guest relocation expenses, inter-hotel walk penalties, taxi vouchers, brand reputation damage, or customer lifetime value destruction. Overbooking to the full 10th percentile would result in guest walking on 10% of high-demand dates.
     2. *Information Asymmetry*: Cancellations are only known *after the fact*. While cancellations occur across the booking window, if late-stage cancellations unexpectedly halt on a specific date, the property faces an acute physical room deficit.
     3. *Operational Heuristic for Discussion*: This recommendation is explicitly an analytical heuristic for executive review and controlled pilot testing, not an automated algorithm.

---

### 2. Evidence
Every figure below is derived from analytical output marts saved on disk and indexed in [`reports/findings_data.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/reports/findings_data.json):

#### Overbooking Buffer Parameters by Month (`v_overbooking_buffer.csv`, `capacity.csv`)
| Hotel | Month | Month Num | Median Daily Cancel Rate | Conservative Rate (10th Pct) | Days Observed | Capacity | Conservative Rooms | Half-Rate Pilot % | Pilot Buffer Rooms | Source Tag |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **City Hotel** | January | 1 | 30.33% | **15.76%** | 60 | 250 | 39.4 | 7.88% | 19.7 | `[v_overbooking_buffer.csv, conservative_rate]` |
| City Hotel | February | 2 | 29.50% | **18.34%** | 57 | 250 | 45.9 | 9.17% | 22.9 | `[v_overbooking_buffer.csv, conservative_rate]` |
| City Hotel | March | 3 | 30.32% | **19.30%** | 62 | 250 | 48.3 | 9.65% | 24.1 | `[v_overbooking_buffer.csv, conservative_rate]` |
| City Hotel | April | 4 | 41.44% | **27.09%** | 60 | 250 | 67.7 | 13.55% | 33.9 | `[v_overbooking_buffer.csv, conservative_rate]` |
| City Hotel | May | 5 | 39.36% | **24.73%** | 62 | 250 | 61.8 | 12.37% | 30.9 | `[v_overbooking_buffer.csv, conservative_rate]` |
| City Hotel | June | 6 | 41.79% | **23.59%** | 59 | 250 | 59.0 | 11.80% | 29.5 | `[v_overbooking_buffer.csv, conservative_rate]` |
| City Hotel | July | 7 | 37.50% | **21.77%** | 81 | 250 | 54.4 | 10.89% | 27.2 | `[v_overbooking_buffer.csv, conservative_rate]` |
| City Hotel | August | 8 | 36.61% | **24.46%** | 91 | 250 | 61.2 | 12.23% | 30.6 | `[v_overbooking_buffer.csv, conservative_rate]` |
| City Hotel | September | 9 | 38.94% | **12.16%** | 60 | 250 | 30.4 | 6.08% | 15.2 | `[v_overbooking_buffer.csv, conservative_rate]` |
| City Hotel | October | 10 | 40.06% | **11.13%** | 62 | 250 | 27.8 | 5.57% | 13.9 | `[v_overbooking_buffer.csv, conservative_rate]` |
| City Hotel | November | 11 | 28.32% | **11.25%** | 54 | 250 | 28.1 | 5.63% | 14.1 | `[v_overbooking_buffer.csv, conservative_rate]` |
| City Hotel | December | 12 | 35.88% | **14.76%** | 54 | 250 | 36.9 | 7.38% | 18.5 | `[v_overbooking_buffer.csv, conservative_rate]` |
| **City Mean** | — | — | **35.84%** | **18.69%** | **762** | **250** | **46.7** | **9.35%** | **23.4** | `[reports/findings_data.json]` |
| **Resort Hotel** | January | 1 | 12.12% | **4.56%** | 55 | 210 | 9.6 | 2.28% | 4.8 | `[v_overbooking_buffer.csv, conservative_rate]` |
| Resort Hotel | February | 2 | 18.52% | **7.00%** | 55 | 210 | 14.7 | 3.50% | 7.4 | `[v_overbooking_buffer.csv, conservative_rate]` |
| Resort Hotel | March | 3 | 17.98% | **8.90%** | 60 | 210 | 18.7 | 4.45% | 9.3 | `[v_overbooking_buffer.csv, conservative_rate]` |
| Resort Hotel | April | 4 | 26.04% | **12.03%** | 59 | 210 | 25.3 | 6.02% | 12.6 | `[v_overbooking_buffer.csv, conservative_rate]` |
| Resort Hotel | May | 5 | 26.82% | **14.03%** | 62 | 210 | 29.5 | 7.02% | 14.7 | `[v_overbooking_buffer.csv, conservative_rate]` |
| Resort Hotel | June | 6 | 31.58% | **20.19%** | 59 | 210 | 42.4 | 10.10% | 21.2 | `[v_overbooking_buffer.csv, conservative_rate]` |
| Resort Hotel | July | 7 | 30.61% | **17.68%** | 93 | 210 | 37.1 | 8.84% | 18.6 | `[v_overbooking_buffer.csv, conservative_rate]` |
| Resort Hotel | August | 8 | 32.69% | **19.14%** | 93 | 210 | 40.2 | 9.57% | 20.1 | `[v_overbooking_buffer.csv, conservative_rate]` |
| Resort Hotel | September | 9 | 26.09% | **14.56%** | 59 | 210 | 30.6 | 7.28% | 15.3 | `[v_overbooking_buffer.csv, conservative_rate]` |
| Resort Hotel | October | 10 | 20.83% | **5.13%** | 59 | 210 | 10.8 | 2.57% | 5.4 | `[v_overbooking_buffer.csv, conservative_rate]` |
| Resort Hotel | November | 11 | 16.86% | **2.79%** | 52 | 210 | 5.9 | 1.40% | 2.9 | `[v_overbooking_buffer.csv, conservative_rate]` |
| Resort Hotel | December | 12 | 18.85% | **3.33%** | 54 | 210 | 7.0 | 1.67% | 3.5 | `[v_overbooking_buffer.csv, conservative_rate]` |
| **Resort Mean** | — | — | **23.25%** | **10.78%** | **762** | **210** | **22.6** | **5.39%** | **11.3** | `[reports/findings_data.json]` |

---

### 3. Recommended Action
1. **Pilot Controlled Overbooking on Peak Dates**:
   - Authorize an initial pilot buffer capped strictly at **HALF the conservative 10th percentile rate** on dates where forward on-the-books demand exceeds 90% of capacity:
     - City Hotel: Maintain an average pilot overbooking cushion of **23 rooms** (ranging from **14 rooms** in October to **34 rooms** in April).
     - Resort Hotel: Maintain an average pilot cushion of **11 rooms** (ranging from **3 rooms** in November to **21 rooms** in June).
2. **Dynamic Cut-Off Tightening**:
   - At 7 days before arrival, re-evaluate booked volume against real-time cancellations. If cancellations are running below the 10th percentile, freeze all sales immediately to prevent overselling.
3. **Establish Walk Protocol & Relocation Tracking**:
   - Establish formal tracking of guest walks, hotel relocation costs, and compensation vouchers in the PMS to compute empirical walk costs before ever expanding overbooking beyond the pilot threshold.

---

### 4. Expected Impact (As a Scenario)

> [!WARNING]
> **Scenario, not forecast**:
> The calculations below represent analytical scenarios based on explicit historical data points. State caveat: higher prices would probably reduce occupancy and that the dataset cannot measure price elasticity. Overbooking models assume that incremental buffered rooms are successfully occupied without triggering guest relocation costs; in practice, unexpected drops in cancellation rates would cause guest walks and service recovery liabilities.

#### Scenario A1: Revenue Recapture from Half-Rate Overbooking Buffer on Peak Compression Nights
- **Formula**:
  $$\Delta \text{Recovered Nights} = \text{Target Dates} \times \text{Pilot Buffer Rooms} \times \text{Realization Rate}$$
  $$\Delta \text{Revenue} = \Delta \text{Recovered Nights} \times \text{Window ADR}$$
- **Data Inputs** [`v_overbooking_buffer.csv`, `v_hotel_totals.csv`, `reports/findings_data.json`]:
  - **City Hotel (22 Peak Nights $\ge 90\%$ Capacity)** [`daily_performance.csv`]:
    - Peak compression nights: **22 nights**
    - Pilot buffer: **23.0 rooms** (half of 46.7 conservative rooms)
    - Realization rate (buffered rooms successfully sold without walk): **50.0%** ($0.50$)
    - Window ADR benchmark: **$106.72** [`v_hotel_totals.csv`, adr]
    - Calculation:
      $$\Delta \text{Nights}_{\text{City}} = 22 \times 23.0 \times 0.50 = 253.0 \text{ room-nights}$$
      $$\Delta \text{Revenue}_{\text{City}} = 253.0 \times \$106.72 = \mathbf{\$27,000.16}$$
  - **Resort Hotel (62 Peak Summer Nights: July–August)** [`v_seasonality.csv`]:
    - Peak summer nights: **62 nights**
    - Pilot buffer: **11.0 rooms** (half of 22.6 conservative rooms)
    - Realization rate: **50.0%** ($0.50$)
    - Window ADR benchmark: **$95.29** [`v_hotel_totals.csv`, adr]
    - Calculation:
      $$\Delta \text{Nights}_{\text{Resort}} = 62 \times 11.0 \times 0.50 = 341.0 \text{ room-nights}$$
      $$\Delta \text{Revenue}_{\text{Resort}} = 341.0 \times \$95.29 = \mathbf{\$32,493.89}$$
  - **Combined Portfolio Recapture**:
    $$\Delta \text{Total Recovered Nights} = 253.0 + 341.0 = \mathbf{594.0 \text{ room-nights}}$$
    $$\Delta \text{Total Revenue} = \$27,000.16 + \$32,493.89 = \mathbf{\$59,494.05}$$
- **Scenario Result**:
  If a pilot overbooking buffer of half the conservative rate recaptured 50% of otherwise spoiled room capacity on peak dates, the hotel group would recover **594.0 room-nights** and generate **$59,494.05** in incremental room revenue ($27,000.16 at City Hotel and $32,493.89 at Resort Hotel).

---

## Insight (b): Room-Type Mismatch as a Walk-Risk Signal

### 1. Finding
Room-type mismatch—where the room type assigned upon check-in differs from the room type initially reserved by the guest (`assigned_room_type != reserved_room_type`)—serves as an operational signal of room inventory friction and walk risk:

1. **Portfolio Mismatch Prevalence**:
   - Across the 75,165 non-cancelled guest check-outs in the analytical dataset, **14,114 stays** experienced a room-type mismatch, representing an overall portfolio mismatch rate of **18.78%** [`v_room_mismatch.csv`].
   - **City Hotel**: **14.65%** of non-cancelled stays experienced room-type mismatch (**6,774 mismatched rooms** out of 46,228 checked-in bookings) [`v_room_mismatch.csv`].
   - **Resort Hotel**: **25.37%** of non-cancelled stays experienced room-type mismatch (**7,340 mismatched rooms** out of 28,937 checked-in bookings) [`v_room_mismatch.csv`]. Resort Hotel shows an operational mismatch rate **1.73 times higher** than City Hotel.

2. **Divergent Seasonal Patterns**:
   - **City Hotel (Urban Operational Learning)**: Room mismatch peaked during the property's opening/ramp-up months in 2015, reaching **32.38% in September 2015** and **26.76% in August 2015** [`v_room_mismatch.csv`]. Through 2016, mismatch stabilized between **10.00% and 17.80%**. By 2017, operational front-desk allocation matured significantly, dropping to annual lows of **5.96% in June 2017** and **6.26% in July 2017**.
   - **Resort Hotel (Extreme Counter-Seasonal Winter Surge)**: Rather than peaking in high-demand summer periods, Resort Hotel exhibits an extreme surge in room mismatch during **off-peak winter months**:
     - January 2016 reached **53.46%** (more than 1 in 2 checked-in guests reassigned!) [`v_room_mismatch.csv`].
     - February 2016 reached **41.78%**, November 2015 reached **37.28%**, and January 2017 reached **36.26%** [`v_room_mismatch.csv`].
     - Conversely, during peak leisure summer months, mismatch dropped to its annual lows: **11.56% in August 2016** and **9.76% in August 2017** [`v_room_mismatch.csv`].
   - *Operational Context of Winter Surge*: In low-occupancy winter periods, Resort Hotel likely consolidates guests by closing unheated/unserviced outer villa blocks to save energy and housekeeping costs, reassigning guests to central buildings, or liberally issuing complimentary room upgrades when standard inventory is sparse.

3. **Critical Data Limitation: Upgrades vs. Downgrades**:
   - **What the data CANNOT say**: The dataset records only whether the assigned room type letter differs from the reserved room type letter (e.g., Code A reserved vs Code D assigned).
   - The data contains **no room category hierarchy, room size, bed configurations, view classifications (sea view vs garden view), or room-specific rate tiers**.
   - Consequently, **the dataset cannot determine whether guests were upgraded** (e.g., standard room moved to a junior suite, which enhances guest satisfaction and eliminates walk risk) **or downgraded** (e.g., family suite moved to a standard double, which represents a severe operational failure and walk-risk proxy).

---

### 2. Evidence

#### Room-Type Mismatch by Property (`v_room_mismatch.csv`)
| Hotel | Non-Cancelled Bookings | Mismatched Rooms | Overall Mismatch % | Lowest Monthly Mismatch % | Highest Monthly Mismatch % | Source Tag |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **City Hotel** | 46,228 | 6,774 | **14.65%** | 5.96% (2017-06) | 32.38% (2015-09) | `[v_room_mismatch.csv, mismatch_pct]` |
| **Resort Hotel** | 28,937 | 7,340 | **25.37%** | 9.76% (2017-08) | 53.46% (2016-01) | `[v_room_mismatch.csv, mismatch_pct]` |
| **All Hotels** | **75,165** | **14,114** | **18.78%** | — | — | `[reports/findings_data.json]` |

#### Monthly Mismatch Progression Across Sample Cohorts (`v_room_mismatch.csv`)
- **City Hotel Key Cohorts**:
  - `2015-09-01`: 1,986 non-cancelled stays, 643 mismatched rooms (**32.38%** mismatch) [`v_room_mismatch.csv`].
  - `2016-06-01`: 2,203 non-cancelled stays, 383 mismatched rooms (**17.39%** mismatch) [`v_room_mismatch.csv`].
  - `2017-06-01`: 2,163 non-cancelled stays, 129 mismatched rooms (**5.96%** mismatch) [`v_room_mismatch.csv`].
- **Resort Hotel Key Cohorts**:
  - `2015-11-01`: 920 non-cancelled stays, 343 mismatched rooms (**37.28%** mismatch) [`v_room_mismatch.csv`].
  - `2016-01-01`: 765 non-cancelled stays, 409 mismatched rooms (**53.46%** mismatch) [`v_room_mismatch.csv`].
  - `2016-08-01`: 1,107 non-cancelled stays, 128 mismatched rooms (**11.56%** mismatch) [`v_room_mismatch.csv`].
  - `2017-01-01`: 1,103 non-cancelled stays, 400 mismatched rooms (**36.26%** mismatch) [`v_room_mismatch.csv`].
  - `2017-08-01`: 1,107 non-cancelled stays, 108 mismatched rooms (**9.76%** mismatch) [`v_room_mismatch.csv`].

---

### 3. Recommended Action
1. **PMS Room Assignment Classification Tagging**:
   - Upgrade the hotel's property management system to require front-desk agents to log a specific reason code whenever an assigned room diverges from the reserved type (e.g., `UPG-LOYALTY`, `UPG-OPERATIONAL`, `MAINT-CONSOLIDATE`, or `DOWNGRADE-OVERBOOK`).
2. **Formalize Winter Wing Closure Calendars**:
   - Rather than closing resort villa blocks ad-hoc upon guest arrival (forcing last-minute reassignments for over 50% of arrivals in January), coordinate with maintenance to black out closed inventory in central reservation systems months in advance.
3. **Establish Involuntary Downgrade Protection**:
   - Enforce an absolute zero-involuntary-downgrade threshold during high-demand summer periods to safeguard guest loyalty and eliminate legal compensation liabilities.

---

### 4. Expected Impact (As a Scenario)

> [!WARNING]
> **Scenario, not forecast**:
> The calculations below represent analytical scenarios based on explicit historical baseline data. State caveat: higher prices would probably reduce occupancy and that the dataset cannot measure price elasticity. Operational room mismatch scenarios assume that a portion of reassigned rooms represent preventable operational friction rather than planned complimentary upgrades.

#### Scenario B1: 20% Reduction in Operational Room Mismatch via Inventory Mapping
- **Formula**:
  $$\Delta \text{Mismatches Avoided} = \text{Total Mismatched Rooms} \times 0.20$$
- **Data Inputs** [`v_room_mismatch.csv`, mismatched_rooms; `reports/findings_data.json`]:
  - City Hotel mismatched stays: **6,774 bookings**
  - Resort Hotel mismatched stays: **7,340 bookings**
  - Combined portfolio mismatched stays: **14,114 bookings**
  - Reduction factor: **20.0%** ($0.20$)
- **Calculation**:
  $$\Delta \text{City Mismatches} = 6,774 \times 0.20 = \mathbf{1,354.8 \text{ stays}}$$
  $$\Delta \text{Resort Mismatches} = 7,340 \times 0.20 = \mathbf{1,468.0 \text{ stays}}$$
  $$\Delta \text{Portfolio Mismatches} = 14,114 \times 0.20 = \mathbf{2,822.8 \text{ stays}}$$
- **Scenario Result**:
  If improved advance room blocking and winter inventory mapping eliminated 20% of room-type reassignments, the property group would stabilize room assignments for **2,822.8 guest arrivals** (1,354.8 at City Hotel and 1,468.0 at Resort Hotel), protecting operational service delivery and eliminating downgrade walk risks.

---

## Insight (c): Commercial Segment & Channel Mix Optimization

### 1. Finding
An analysis of commercial market segments [`v_segment_performance.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/data/outputs/v_segment_performance.csv) and distribution channels [`v_channel_performance.csv`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/data/outputs/v_channel_performance.csv) reveals heavy volume concentration alongside sharp profitability discrepancies:

1. **Volume and Revenue Dominance**:
   - **Market Segment**: **Online TA** is the primary volume and revenue engine across both properties, generating **61.1%** of room revenue ($8,732,303.32) at City Hotel and **42.8%** ($4,662,825.19) at Resort Hotel [`v_segment_performance.csv`, revenue_share_pct].
   - **Distribution Channel**: **TA/TO** dominates distribution, capturing **84.7%** of revenue ($12,105,463.58) at City Hotel and **74.0%** ($8,066,941.82) at Resort Hotel [`v_channel_performance.csv`, revenue_share_pct].

2. **Rate Premium and Loyalty Stability (Direct Channels)**:
   - **Market Segment**: **Direct** achieves the **highest realized ADR of any commercial segment** at both hotels: **$120.51** at City Hotel and **$126.78** at Resort Hotel [`v_segment_performance.csv`, adr].
   - **Cancellation Resilience**: **Direct** achieves the **lowest cancellation rate of any commercial paying segment**: **17.3%** at City Hotel (vs 37.4% Online TA, 42.8% Offline TA/TO, 68.9% Groups) and **13.5%** at Resort Hotel (vs 35.2% Online TA, 42.4% Groups) [`v_segment_performance.csv`, cancel_rate_pct].
   - **Distribution Channel**: The **Direct channel** commands an ADR of **$115.09** at City Hotel (second only to niche corporate GDS at $125.98) and **$116.43** at Resort Hotel, while exhibiting low cancellation rates of **18.2%** and **16.8%** [`v_channel_performance.csv`].

3. **Commercial Underperformers (`is_underperformer = 1`)**:
   - **Groups (Both Properties)**: Flagged as an underperformer across the entire portfolio. At City Hotel, Groups suffers a catastrophic **68.9% cancellation rate** at a depressed ADR of **$86.38** (generating only 6.6% revenue share despite 13,975 bookings) [`v_segment_performance.csv`]. At Resort Hotel, Groups exhibits a **42.4% cancellation rate** and delivers the **lowest ADR of any commercial segment in the resort at $66.31** (revenue share 8.1%) [`v_segment_performance.csv`].
   - **Offline TA/TO (City Hotel)**: Flagged as an underperformer at City Hotel, coinciding with an elevated cancellation rate of **42.8%** and a discounted ADR of **$88.85** (contributing 17.6% revenue share) [`v_segment_performance.csv`].

4. **Rule K7 Methodological Governance**:
   - In strict compliance with **Rule K7**, segment-level occupancy and RevPAR do not exist and are not reported. Physical room inventory belongs strictly to the hotel property. Slicing performance by segment or channel is evaluated solely via room-night share, revenue share, realized ADR, and cancellation rate contribution.

---

### 2. Evidence

#### Market Segment Performance (`v_segment_performance.csv`)
| Hotel | Market Segment | Bookings | Cancellations | Cancel Rate % | Room Nights Sold | Room Revenue ($) | Realized ADR ($) | Room Night Share % | Revenue Share % | Underperformer? | Source Tag |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **City Hotel** | Online TA | 38,748 | 14,491 | 37.4% | 75,062 | $8,732,303.32 | $116.33 | **56.1%** | **61.1%** | No | `[v_segment_performance.csv, revenue_share_pct]` |
| City Hotel | Offline TA/TO | 16,746 | 7,172 | **42.8%** | 28,314 | $2,515,578.67 | $88.85 | 21.2% | 17.6% | **Yes** | `[v_segment_performance.csv, is_underperformer]` |
| City Hotel | Direct | 6,093 | 1,056 | **17.3%** | 13,705 | $1,651,522.04 | **$120.51** | 10.2% | 11.6% | No | `[v_segment_performance.csv, adr]` |
| City Hotel | Groups | 13,975 | 9,623 | **68.9%** | 10,967 | $947,315.63 | $86.38 | 8.2% | 6.6% | **Yes** | `[v_segment_performance.csv, is_underperformer]` |
| City Hotel | Corporate | 2,986 | 641 | 21.5% | 4,401 | $365,135.40 | $82.97 | 3.3% | 2.6% | No | `[v_segment_performance.csv, adr]` |
| City Hotel | Aviation | 237 | 52 | 21.9% | 692 | $70,868.36 | $102.41 | 0.5% | 0.5% | No | `[v_segment_performance.csv, adr]` |
| City Hotel | Complementary | 542 | 64 | 11.8% | 719 | $2,743.00 | $3.82 | 0.5% | 0.0% | No | `[v_segment_performance.csv, adr]` |
| **Resort Hotel** | Online TA | 17,729 | 6,248 | 35.2% | 41,639 | $4,662,825.19 | $111.98 | **36.4%** | **42.8%** | No | `[v_segment_performance.csv, revenue_share_pct]` |
| Resort Hotel | Offline TA/TO | 7,472 | 1,138 | 15.2% | 36,896 | $2,865,312.28 | $77.66 | 32.3% | 26.3% | No | `[v_segment_performance.csv, revenue_share_pct]` |
| Resort Hotel | Direct | 6,513 | 878 | **13.5%** | 17,974 | $2,278,714.67 | **$126.78** | 15.7% | 20.9% | No | `[v_segment_performance.csv, adr]` |
| Resort Hotel | Groups | 5,835 | 2,474 | **42.4%** | 13,338 | $884,436.14 | **$66.31** | 11.7% | 8.1% | **Yes** | `[v_segment_performance.csv, is_underperformer]` |
| Resort Hotel | Corporate | 2,309 | 351 | 15.2% | 4,188 | $208,361.93 | $49.75 | 3.7% | 1.9% | No | `[v_segment_performance.csv, adr]` |
| Resort Hotel | Complementary | 201 | 33 | 16.4% | 366 | $2,069.53 | $5.65 | 0.3% | 0.0% | No | `[v_segment_performance.csv, adr]` |

#### Distribution Channel Performance (`v_channel_performance.csv`)
| Hotel | Channel | Bookings | Cancellations | Cancel Rate % | Room Nights Sold | Room Revenue ($) | Realized ADR ($) | Revenue Share % | Source Tag |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **City Hotel** | TA/TO | 68,944 | 31,042 | **45.0%** | 113,621 | $12,105,463.58 | $106.54 | **84.7%** | `[v_channel_performance.csv, revenue_share_pct]` |
| City Hotel | Direct | 6,780 | 1,232 | **18.2%** | 14,516 | $1,670,702.19 | **$115.09** | **11.7%** | `[v_channel_performance.csv, adr]` |
| City Hotel | Corporate | 3,408 | 786 | 23.1% | 5,461 | $476,292.69 | $87.22 | 3.3% | `[v_channel_performance.csv, adr]` |
| City Hotel | GDS | 193 | 37 | 19.2% | 262 | $33,007.96 | **$125.98** | 0.2% | `[v_channel_performance.csv, adr]` |
| **Resort Hotel** | TA/TO | 28,925 | 9,109 | **31.5%** | 86,459 | $8,066,941.82 | $93.30 | **74.0%** | `[v_channel_performance.csv, revenue_share_pct]` |
| Resort Hotel | Direct | 7,864 | 1,325 | **16.8%** | 21,361 | $2,487,031.55 | **$116.43** | **22.8%** | `[v_channel_performance.csv, adr]` |
| Resort Hotel | Corporate | 3,269 | 688 | 21.0% | 6,581 | $347,746.37 | $52.84 | 3.2% | `[v_channel_performance.csv, adr]` |

---

### 3. Recommended Action
1. **Aggressive Direct Channel Shift**:
   - Reallocate marketing spend from generic wholesale brochure distribution toward direct consumer digital acquisition (search engine marketing, brand-direct booking engines, and member-only rate plans).
   - Direct bookings achieve the highest realized ADR ($120.51 and $126.78), the lowest cancellation rates (17.3% and 13.5%), and completely bypass 15%–20% OTA intermediary commissions.
2. **Restrict Wholesale Group Allotments**:
   - Significantly reduce room block commitments to wholesale tour operator group codes. Groups at City Hotel suffer from a 68.9% cancellation rate, while at Resort Hotel they dilute rate integrity at $66.31 ADR.
   - Introduce strict non-refundable advance deposits and rolling 60/30-day cut-off rules for groups, reallocating unpicked rooms to higher-yielding Direct and Online TA channels.

---

### 4. Expected Impact (As a Scenario)

> [!WARNING]
> **Scenario, not forecast**:
> The calculations below represent analytical scenarios based on explicit historical data points. State caveat: higher prices would probably reduce occupancy and that the dataset cannot measure price elasticity. Mix shift scenarios assume that sufficient unmet Direct consumer demand exists at full BAR to replace wholesale group allotments, and omit digital customer acquisition advertising costs.

#### Scenario C1: Shifting 2,000 Room-Nights from Underperforming Groups to Direct Segment per Hotel
- **Formula**:
  $$\Delta \text{Revenue} = \text{Shifted Nights} \times (\text{ADR}_{\text{Direct}} - \text{ADR}_{\text{Groups}})$$
- **Data Inputs** [`v_segment_performance.csv`, adr; `reports/findings_data.json`, overbooking_and_mix.mix_shift_scenario]:
  - **City Hotel**:
    - Shifted volume: **2,000 room-nights** (18.2% of City Groups volume of 10,967 nights)
    - Direct ADR benchmark: **$120.51** [`v_segment_performance.csv`, adr]
    - Groups ADR benchmark: **$86.38** [`v_segment_performance.csv`, adr]
    - ADR Spread: $\$120.51 - \$86.38 = \mathbf{+\$34.13}$ per night
    - Calculation:
      $$\Delta \text{Revenue}_{\text{City}} = 2,000 \times \$34.13 = \mathbf{+\$68,260.00}$$
    - Cancellation Attrition Benefit: Shifts booking volume from a 68.9% cancel rate segment to a 17.3% cancel rate segment (**-51.6 percentage points** in cancellation risk).
  - **Resort Hotel**:
    - Shifted volume: **2,000 room-nights** (15.0% of Resort Groups volume of 13,338 nights)
    - Direct ADR benchmark: **$126.78** [`v_segment_performance.csv`, adr]
    - Groups ADR benchmark: **$66.31** [`v_segment_performance.csv`, adr]
    - ADR Spread: $\$126.78 - \$66.31 = \mathbf{+\$60.47}$ per night
    - Calculation:
      $$\Delta \text{Revenue}_{\text{Resort}} = 2,000 \times \$60.47 = \mathbf{+\$120,940.00}$$
    - Cancellation Attrition Benefit: Shifts booking volume from a 42.4% cancel rate segment to a 13.5% cancel rate segment (**-28.9 percentage points** in cancellation risk).
  - **Combined Portfolio Financial Impact**:
    $$\Delta \text{Portfolio Revenue} = \$68,260.00 + \$120,940.00 = \mathbf{+\$189,200.00}$$
- **Scenario Result**:
  Shifting 2,000 room-nights at each property from the underperforming Groups segment to high-yield Direct channels would generate an incremental **+$189,200.00** in room revenue ($68,260.00 at City Hotel and $120,940.00 at Resort Hotel) across 4,000 shifted room-nights, with zero expansion in physical room inventory or occupancy required.

---

## Analytical Summary Table: Overbooking & Commercial Mix Payoffs

| Scenario ID | Focus Area | Property | Target Cohort | Baseline Parameters | Policy Mechanism | Realized Impact ($) | Key Operational Caveat | Source Tag |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- | :--- |
| **Scenario A1** | Capacity Protection | Portfolio | Peak dates (22 City, 62 Resort) | 23 City / 11 Resort buffer rooms | Pilot overbooking at half conservative rate | **+$59,494.05** (594.0 room-nights) | Scenario, not forecast; risk of guest walks if cancels stop | `[reports/findings_data.json, overbooking_and_mix]` |
| **Scenario B1** | Walk-Risk Signals | Portfolio | 14,114 mismatched stays | 14.65% City / 25.37% Resort mismatch | Advance inventory mapping & wing closures | **2,822.8 stays** protected | Scenario, not forecast; cannot measure upgrade vs downgrade | `[reports/findings_data.json, overbooking_and_mix]` |
| **Scenario C1** | Mix Optimization | Portfolio | 4,000 shifted room-nights | Groups ADR $86/$66 vs Direct $121/$127 | Reallocate 2k nights/hotel from Groups to Direct | **+$189,200.00** pure rate gain | Scenario, not forecast; assumes unmet Direct demand exists | `[reports/findings_data.json, overbooking_and_mix]` |
