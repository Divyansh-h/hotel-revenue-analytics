# Strategic Revenue Insights: Pricing & Seasonality Dynamics

> [!NOTE]
> **Data Integrity and Rule Governance**:
> This report has been compiled in strict adherence to **Global Rule R1** and **Project Context**. Every metric, baseline, and scenario input is derived directly from physical data outputs saved on disk in `data/outputs/*.csv` and validated in [`reports/findings_data.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/reports/findings_data.json). No numbers have been estimated, forecasted, or typed by hand.
>
> All performance metrics are evaluated over the authoritative reliable performance window (**2015-08-01 to 2017-08-31**, 762 calendar days) established under Rules W1 and W2. Hotel capacity assumptions are fixed at **250 rooms** for City Hotel (peak 226 rooms sold on 2016-08-13 with 1.10 buffer) and **210 rooms** for Resort Hotel (peak 187 rooms sold on 2016-03-25 with 1.10 buffer) [`capacity.csv`, rooms; `capacity_derivation.csv`].

---

## Insight (a): Seasonality Patterns & Dynamic Rate Rules

### 1. Finding
Both properties experience distinct three-tier seasonality (Peak, Shoulder, and Low) as classified in `v_seasonality.csv`, but their pricing dynamics and occupancy co-movement diverge sharply:

1. **City Hotel (Lisbon, Urban Commercial & Leisure)**:
   - **Peak Season (April, May, June, July)**: Unweighted average occupancy reaches **82.99%**, with average daily rate (ADR) of **$117.61** and RevPAR of **$97.91** [`v_seasonality.csv`, season = 'Peak'].
   - **Shoulder Season (March, August, September, October)**: Unweighted average occupancy moderates to **77.44%**, with ADR of **$103.83** and RevPAR of **$81.73** [`v_seasonality.csv`, season = 'Shoulder'].
   - **Low Season (November, December, January, February)**: Unweighted average occupancy drops to **49.98%**, with ADR of **$85.66** and RevPAR of **$43.80** [`v_seasonality.csv`, season = 'Low'].
   - **ADR & Occupancy Co-movement**: City Hotel displays steady, synchronized co-movement across the calendar year. Peak occupancy reaches **86.19%** in July while low occupancy bottoms at **42.38%** in January (a spread of 43.81 percentage points) [`v_seasonality.csv`, avg_occupancy_pct]. In parallel, ADR peaks in May at **$121.39** and reaches its annual trough in January at **$84.28** (a spread of $37.11 or +44.0%) [`v_seasonality.csv`, avg_adr]. Transitioning from Peak to Low season, occupancy drops by **33.01 percentage points** (-39.8%) while ADR decreases by **$31.95** (-27.2%) [`reports/findings_data.json`, seasonality.City Hotel.co_movement]. ADR and volume move in harmony without extreme structural dislocations.

2. **Resort Hotel (Algarve, Coastal Leisure Destination)**:
   - **Peak Season (June, July, August, September)**: Unweighted average occupancy surges to **85.35%**, with ADR reaching **$131.24** and RevPAR reaching **$112.06** [`v_seasonality.csv`, season = 'Peak'].
   - **Shoulder Season (March, April, May, October)**: Unweighted average occupancy averages **77.17%**, with ADR dropping to **$67.95** and RevPAR dropping to **$52.73** [`v_seasonality.csv`, season = 'Shoulder'].
   - **Low Season (November, December, January, February)**: Unweighted average occupancy falls to **50.03%**, with ADR dropping to **$56.74** and RevPAR dropping to **$28.19** [`v_seasonality.csv`, season = 'Low'].
   - **ADR & Occupancy Co-movement & Pricing Inefficiency**: Resort Hotel exhibits extreme seasonal rate elasticity and an asymmetric late-summer rate decoupling. Occupancy varies from **40.29%** in January to **86.06%** in September (a spread of 45.77 percentage points) [`v_seasonality.csv`, avg_occupancy_pct]. However, ADR fluctuates by **$126.80** (+251.8%), surging from **$50.36** in November to **$177.16** in August [`v_seasonality.csv`, avg_adr]. 
   - *Critical Misalignment*: In **September**, Resort Hotel occupancy is the highest of any month in the year at **86.06%** (higher than August's 85.90% and July's 85.16%), yet its ADR collapses by **47.0%** from August's **$177.16** down to **$93.97** [`v_seasonality.csv`, avg_adr]. While guest volume remains at full peak-season capacity, the property prematurely discounts room rates by $83.19 per night to shoulder pricing levels.

---

### 2. Evidence
Every figure below is derived from analytical output marts saved on disk and indexed in [`reports/findings_data.json`](file:///Users/divyansh/code/Development/DataScience/hotel-revenue-analytics/reports/findings_data.json):

#### Monthly Seasonality Breakdown (`v_seasonality.csv`)
| Hotel | Month | Month Num | Avg Occupancy % | Avg ADR ($) | Avg RevPAR ($) | Season Tier | Historical Years | Source Tag |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **City Hotel** | January | 1 | 42.38% | $84.28 | $36.27 | Low | 2 | `[v_seasonality.csv, avg_adr]` |
| City Hotel | February | 2 | 60.34% | $86.66 | $52.69 | Low | 2 | `[v_seasonality.csv, avg_adr]` |
| City Hotel | March | 3 | 78.12% | $89.14 | $69.71 | Shoulder | 2 | `[v_seasonality.csv, avg_adr]` |
| City Hotel | April | 4 | 81.88% | $110.94 | $91.36 | Peak | 2 | `[v_seasonality.csv, avg_adr]` |
| City Hotel | May | 5 | 82.84% | $121.39 | $100.78 | Peak | 2 | `[v_seasonality.csv, avg_adr]` |
| City Hotel | June | 6 | 81.03% | $119.10 | $96.87 | Peak | 2 | `[v_seasonality.csv, avg_adr]` |
| City Hotel | July | 7 | 86.19% | $118.99 | $102.61 | Peak | 2 | `[v_seasonality.csv, avg_adr]` |
| City Hotel | August | 8 | 73.20% | $111.07 | $85.75 | Shoulder | 3 | `[v_seasonality.csv, avg_adr]` |
| City Hotel | September | 9 | 80.52% | $112.62 | $91.07 | Shoulder | 2 | `[v_seasonality.csv, avg_adr]` |
| City Hotel | October | 10 | 77.91% | $102.51 | $80.40 | Shoulder | 2 | `[v_seasonality.csv, avg_adr]` |
| City Hotel | November | 11 | 53.44% | $84.68 | $47.34 | Low | 2 | `[v_seasonality.csv, avg_adr]` |
| City Hotel | December | 12 | 43.77% | $87.01 | $38.90 | Low | 2 | `[v_seasonality.csv, avg_adr]` |
| **Resort Hotel** | January | 1 | 40.29% | $56.37 | $22.67 | Low | 2 | `[v_seasonality.csv, avg_adr]` |
| Resort Hotel | February | 2 | 56.11% | $53.44 | $30.13 | Low | 2 | `[v_seasonality.csv, avg_adr]` |
| Resort Hotel | March | 3 | 71.80% | $56.90 | $40.84 | Shoulder | 2 | `[v_seasonality.csv, avg_adr]` |
| Resort Hotel | April | 4 | 76.10% | $75.37 | $57.54 | Shoulder | 2 | `[v_seasonality.csv, avg_adr]` |
| Resort Hotel | May | 5 | 82.23% | $74.99 | $61.68 | Shoulder | 2 | `[v_seasonality.csv, avg_adr]` |
| Resort Hotel | June | 6 | 84.28% | $102.10 | $85.94 | Peak | 2 | `[v_seasonality.csv, avg_adr]` |
| Resort Hotel | July | 7 | 85.16% | $151.73 | $129.18 | Peak | 2 | `[v_seasonality.csv, avg_adr]` |
| Resort Hotel | August | 8 | 85.90% | $177.16 | $152.24 | Peak | 3 | `[v_seasonality.csv, avg_adr]` |
| Resort Hotel | September | 9 | 86.06% | $93.97 | $80.86 | Peak | 2 | `[v_seasonality.csv, avg_adr]` |
| Resort Hotel | October | 10 | 78.56% | $64.53 | $50.87 | Shoulder | 2 | `[v_seasonality.csv, avg_adr]` |
| Resort Hotel | November | 11 | 58.31% | $50.36 | $29.49 | Low | 2 | `[v_seasonality.csv, avg_adr]` |
| Resort Hotel | December | 12 | 45.39% | $66.79 | $30.46 | Low | 2 | `[v_seasonality.csv, avg_adr]` |

#### Seasonal Performance Aggregates
- **City Hotel Realized Totals**:
  - Peak Season (Apr, May, Jun, Jul): **44,783** room nights sold, **53,950** room nights available (**83.01%** blended occupancy), **$5,431,885.55** room revenue, **$121.29** blended ADR [`v_monthly_kpis.csv`, room_revenue; `reports/findings_data.json`].
  - Shoulder Season (Mar, Aug, Sep, Oct): **59,132** room nights sold, **76,050** room nights available (**77.75%** blended occupancy), **$6,230,214.85** room revenue, **$105.36** blended ADR [`v_monthly_kpis.csv`, room_revenue; `reports/findings_data.json`].
  - Low Season (Nov, Dec, Jan, Feb): **29,945** room nights sold, **60,500** room nights available (**49.50%** blended occupancy), **$2,623,366.02** room revenue, **$87.61** blended ADR [`v_monthly_kpis.csv`, room_revenue; `reports/findings_data.json`].
- **Resort Hotel Realized Totals**:
  - Peak Season (Jun, Jul, Aug, Sep): **49,326** room nights sold, **57,750** room nights available (**85.41%** blended occupancy), **$6,756,682.18** room revenue, **$136.98** blended ADR [`v_monthly_kpis.csv`, room_revenue; `reports/findings_data.json`].
  - Shoulder Season (Mar, Apr, May, Oct): **39,870** room nights sold, **51,660** room nights available (**77.18%** blended occupancy), **$2,722,073.29** room revenue, **$68.27** blended ADR [`v_monthly_kpis.csv`, room_revenue; `reports/findings_data.json`].
  - Low Season (Nov, Dec, Jan, Feb): **25,205** room nights sold, **50,610** room nights available (**49.80%** blended occupancy), **$1,422,964.27** room revenue, **$56.46** blended ADR [`v_monthly_kpis.csv`, room_revenue; `reports/findings_data.json`].

#### Peak-Night Capacity Share (Prompt 2.3 Benchmark)
- **City Hotel (Capacity = 250 rooms)** [`capacity.csv`, rooms]:
  - 90% Capacity Threshold = **225 rooms** [`sql/21_capacity_daily.sql`, threshold_90pct].
  - Over the 762-day analytical window, exactly **22 nights** operated at or above 90% capacity (**2.89%** of all calendar nights) [`daily_performance.csv`, rooms_sold; `sql/21_capacity_daily.sql`, nights_ge_90pct].
  - Across these 22 high-compression nights, City Hotel sold **4,958 room nights** and generated **$580,233.65** in room revenue at an average realized ADR of **$117.03** and average occupancy of **90.15%** [`daily_performance.csv`, room_revenue; `reports/findings_data.json`].
  - The single highest peak night was **2016-08-13** with **226 rooms sold** (90.40% capacity) generating **$28,321.70** [`capacity_derivation.csv`, peak_rooms_sold; `daily_performance.csv`].
- **Resort Hotel (Capacity = 210 rooms)** [`capacity.csv`, rooms]:
  - 90% Capacity Threshold = **189 rooms** [`sql/21_capacity_daily.sql`, threshold_90pct].
  - Over the 762-day window, exactly **0 nights** operated at or above 90% capacity (**0.00%** of calendar nights) [`daily_performance.csv`, rooms_sold; `sql/21_capacity_daily.sql`, nights_ge_90pct].
  - The maximum rooms sold on any night was **187 rooms** (89.05% of capacity) on **2016-03-25**, generating **$15,059.09** at an ADR of $80.53 [`capacity_derivation.csv`, peak_rooms_sold; `daily_performance.csv`].
  - However, Resort Hotel operated at or above **85.7% capacity** (>= 180 rooms sold) on **220 nights** (**28.87%** of window nights) [`daily_performance.csv`; `reports/findings_data.json`].

---

### 3. Recommended Action
1. **Automated Compression Pricing Hurdles (Peak Premium Rule)**:
   - **City Hotel**: Institute an automated dynamic rate tier that applies a **10% premium** above standard Best Available Rate (BAR) whenever projected on-the-books occupancy reaches or exceeds 90% of capacity (225 rooms). This rule targets the property's proven top 2.89% compression nights to harvest inelastic last-minute business and leisure demand.
   - **Resort Hotel**: Because Resort Hotel never crosses 90% capacity due to inventory derivation buffers but operates at >= 85.7% capacity on 220 nights (28.87%), set dynamic compression triggers at **85.0% capacity** (179 rooms) throughout the June–September summer window.
2. **Defensive Rate Floors in Low Months**:
   - Establish a hard rate floor of **$85.00** for City Hotel and **$55.00** for Resort Hotel during Low season months (November, December, January, February).
   - In Low months, prohibit flash-sale discounting below marginal cleaning and servicing costs. Instead of unbundling and discounting base room rates, stimulate off-peak demand using value-added packages (e.g., complimentary breakfast, parking, dining vouchers, and flexible cancellation terms).
3. **Resort Hotel September Yield Realignment**:
   - Discontinue premature transition to shoulder rates in September. Since September achieves higher occupancy (**86.06%**) than July (**85.16%**) and August (**85.90%**), maintain peak summer rate tiers through the third week of September rather than collapsing ADR by 47.0% from August levels.

---

### 4. Expected Impact (As a Scenario)

> [!WARNING]
> **Scenario, not forecast**:
> The calculations below represent analytical scenarios based on explicit historical data points. State caveat: higher prices would probably reduce occupancy and that the dataset cannot measure price elasticity. Additionally, competitor pricing behavior and demand diversion are outside the scope of this dataset.

#### Scenario A1: 10% Rate Premium on City Hotel Peak Compression Nights (>= 90% Capacity)
- **Formula**:
  $$\Delta \text{Revenue} = \text{Revenue}_{\text{Peak Nights}} \times \text{Premium \%}$$
  $$\text{New Revenue} = \text{Revenue}_{\text{Peak Nights}} + \Delta \text{Revenue}$$
- **Data Inputs** [`reports/findings_data.json`, pricing_rules_and_scenarios.city_hotel_peak_night_premium_10pct]:
  - Number of eligible peak nights ($\ge 90\%$ capacity): **22 nights** [`sql/21_capacity_daily.sql`, nights_ge_90pct]
  - Historical room nights sold on peak nights: **4,958 nights** [`daily_performance.csv`, rooms_sold]
  - Historical room revenue realized on peak nights: **$580,233.65** [`daily_performance.csv`, room_revenue]
  - Baseline blended ADR on peak nights: **$117.03**
  - Scenario premium: **10.0%** ($0.10$)
- **Calculation**:
  $$\Delta \text{Revenue} = \$580,233.65 \times 0.10 = \$58,023.37$$
  $$\text{New Revenue} = \$580,233.65 + \$58,023.37 = \$638,257.02$$
  $$\text{New Blended ADR} = \frac{\$638,257.02}{4,958} = \$128.73 \quad (+\$11.70/\text{night})$$
- **Scenario Result**:
  If ADR on these 22 high-compression nights rose by 10% with occupancy unchanged, City Hotel room revenue would rise by **$58,023.37** across those nights.

#### Scenario A2: 5% Rate Premium Across All City Hotel Peak Season Months
- **Formula**:
  $$\Delta \text{Revenue} = \text{Revenue}_{\text{Peak Season}} \times 0.05$$
- **Data Inputs** [`v_monthly_kpis.csv`, room_revenue; `reports/findings_data.json`]:
  - Total historical Peak season revenue (April, May, June, July): **$5,431,885.55**
  - Total Peak season room nights sold: **44,783 nights**
  - Baseline blended Peak season ADR: **$121.29**
- **Calculation**:
  $$\Delta \text{Revenue} = \$5,431,885.55 \times 0.05 = \$271,594.28$$
  $$\text{New Revenue} = \$5,431,885.55 + \$271,594.28 = \$5,703,479.83$$
  $$\text{New Blended ADR} = \frac{\$5,703,479.83}{44,783} = \$127.36 \quad (+\$6.07/\text{night})$$
- **Scenario Result**:
  If ADR across all four Peak season months rose by 5% with occupancy unchanged, City Hotel room revenue would rise by **$271,594.28**.

---

## Insight (b): Price and Occupancy Gaps

### 1. Finding
Cross-tabulating monthly occupancy and realized ADR against each property's window averages reveals two operational anomalies:

1. **Group 1 (Underpriced Peak Demand: Occupancy > 85.0% but ADR < Hotel Window Average)**:
   - Across the entire portfolio, this pricing distortion occurs exclusively at **Resort Hotel** in exactly **2 calendar months**: **September 2015** (86.32% occupancy, $88.85 ADR) and **June 2016** (85.32% occupancy, $91.63 ADR) [`v_monthly_kpis.csv`]. In both months, occupancy exceeded the 85% threshold, yet ADR sat well below the hotel's window benchmark of **$95.29** [`v_hotel_totals.csv`, adr].
   - **City Hotel** experienced **0 months** fitting this profile [`reports/findings_data.json`, price_occupancy_gaps.group1_high_occ_low_adr.City Hotel]. Whenever City Hotel occupancy exceeded 85% (six distinct months: 2016-07, 2016-08, 2016-09, 2017-04, 2017-07, 2017-08), ADR ranged from **$112.73 to $134.52**, consistently outpacing its window benchmark of **$106.72** [`v_monthly_kpis.csv`].
   - *Underlying Cause for Group 1*: At Resort Hotel, June and September represent high-demand leisure shoulder-to-peak transitions. In September 2015 and June 2016, management accepted heavy wholesale tour-operator and discounted group blocks early in the booking curve, filling over 85% of rooms at off-peak rates and denying inventory to high-yield direct transient travelers.

2. **Group 2 (Off-Peak Depression: Occupancy < Hotel Window Average AND ADR < Hotel Window Average)**:
   - This dual-drag underperformance affects **17 hotel-months** across the portfolio (**8 months** at City Hotel and **9 months** at Resort Hotel) [`reports/findings_data.json`, price_occupancy_gaps.group2_low_occ_low_adr].
   - These periods correspond to severe off-peak winter lulls (November through February across both years, plus the startup ramp-up in August 2015 for City Hotel and the early spring lull in March 2016 for Resort Hotel) [`v_monthly_kpis.csv`].
   - In these months, both properties suffer from simultaneous volume collapse and rate degradation: City Hotel achieves an average occupancy of only **46.44%** at an ADR of **$84.94** (vs window averages of 70.27% and $106.72); Resort Hotel achieves an average occupancy of only **51.69%** at an ADR of **$56.56** (vs window averages of 71.49% and $95.29) [`reports/findings_data.json`, price_occupancy_gaps.group2_low_occ_low_adr].

---

### 2. Evidence

#### Property Window Benchmarks (`v_hotel_totals.csv`)
| Hotel | Room Nights Sold | Room Nights Available | Room Revenue ($) | Window Occupancy % | Window ADR ($) | Window RevPAR ($) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **City Hotel** | 133,860 | 190,500 | $14,285,466.42 | **70.27%** | **$106.72** | $74.99 |
| **Resort Hotel** | 114,401 | 160,020 | $10,901,719.74 | **71.49%** | **$95.29** | $68.13 |
| **All Hotels** | 248,261 | 350,520 | $25,187,186.16 | **70.83%** | **$101.45** | $71.86 |

#### Group 1 Details: High Occupancy (> 85%), Low ADR (< Window ADR)
*Criteria: Occupancy % > 85.0% AND ADR < Property Window ADR ($95.29 for Resort Hotel, $106.72 for City Hotel)*
- **City Hotel**: **0 months** meet the criteria [`reports/findings_data.json`].
- **Resort Hotel**: Exactly **2 months** meet the criteria:

| Hotel | Month Start | Room Nights Sold | Available Nights | Room Revenue ($) | Occupancy % | ADR ($) | Window ADR ($) | ADR Deficit ($) | Source Tag |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| Resort Hotel | 2015-09-01 | 5,438 | 6,300 | $483,189.78 | **86.32%** | **$88.85** | $95.29 | -$6.44 | `[v_monthly_kpis.csv, month_start]` |
| Resort Hotel | 2016-06-01 | 5,375 | 6,300 | $492,518.87 | **85.32%** | **$91.63** | $95.29 | -$3.66 | `[v_monthly_kpis.csv, month_start]` |
| **Group 1 Total** | — | **10,813** | **12,600** | **$975,708.65** | **85.82%** | **$90.23** | $95.29 | -$5.06 | `[reports/findings_data.json]` |

#### Group 2 Details: Low Occupancy (< Window Avg) AND Low ADR (< Window Avg)
*Criteria: Occupancy % < Property Window Occupancy AND ADR < Property Window ADR*
- **City Hotel (Thresholds: Occupancy < 70.27%, ADR < $106.72)**: Exactly **8 months** [`v_monthly_kpis.csv`]:

| Month Start | Room Nights Sold | Available Nights | Room Revenue ($) | Occupancy % | ADR ($) | RevPAR ($) | Source Tag |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 2015-08-01 | 3,440 | 7,750 | $275,450.09 | 44.39% | $80.07 | $35.54 | `[v_monthly_kpis.csv, adr]` |
| 2015-11-01 | 2,725 | 7,500 | $197,495.38 | 36.33% | $72.48 | $26.33 | `[v_monthly_kpis.csv, adr]` |
| 2015-12-01 | 2,631 | 7,750 | $207,115.64 | 33.95% | $78.72 | $26.72 | `[v_monthly_kpis.csv, adr]` |
| 2016-01-01 | 2,459 | 7,750 | $194,455.18 | 31.73% | $79.08 | $25.09 | `[v_monthly_kpis.csv, adr]` |
| 2016-02-01 | 3,739 | 7,250 | $306,620.56 | 51.57% | $82.01 | $42.29 | `[v_monthly_kpis.csv, adr]` |
| 2016-12-01 | 4,153 | 7,750 | $395,765.30 | 53.59% | $95.30 | $51.07 | `[v_monthly_kpis.csv, adr]` |
| 2017-01-01 | 4,110 | 7,750 | $367,719.30 | 53.03% | $89.47 | $47.45 | `[v_monthly_kpis.csv, adr]` |
| 2017-02-01 | 4,837 | 7,000 | $441,617.92 | 69.10% | $91.30 | $63.09 | `[v_monthly_kpis.csv, adr]` |
| **City G2 Total** | **28,094** | **60,500** | **$2,386,239.37** | **46.44%** | **$84.94** | **$39.44** | `[reports/findings_data.json]` |

- **Resort Hotel (Thresholds: Occupancy < 71.49%, ADR < $95.29)**: Exactly **9 months** [`v_monthly_kpis.csv`]:

| Month Start | Room Nights Sold | Available Nights | Room Revenue ($) | Occupancy % | ADR ($) | RevPAR ($) | Source Tag |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 2015-11-01 | 3,295 | 6,300 | $159,162.61 | 52.30% | $48.30 | $25.26 | `[v_monthly_kpis.csv, adr]` |
| 2015-12-01 | 2,682 | 6,510 | $169,591.31 | 41.20% | $63.23 | $26.05 | `[v_monthly_kpis.csv, adr]` |
| 2016-01-01 | 2,116 | 6,510 | $120,315.21 | 32.50% | $56.86 | $18.48 | `[v_monthly_kpis.csv, adr]` |
| 2016-02-01 | 3,028 | 6,090 | $155,152.92 | 49.72% | $51.24 | $25.48 | `[v_monthly_kpis.csv, adr]` |
| 2016-03-01 | 4,319 | 6,510 | $246,926.91 | 66.34% | $57.17 | $37.93 | `[v_monthly_kpis.csv, adr]` |
| 2016-11-01 | 4,052 | 6,300 | $212,374.39 | 64.32% | $52.41 | $33.71 | `[v_monthly_kpis.csv, adr]` |
| 2016-12-01 | 3,227 | 6,510 | $227,019.95 | 49.57% | $70.35 | $34.87 | `[v_monthly_kpis.csv, adr]` |
| 2017-01-01 | 3,130 | 6,510 | $174,882.46 | 48.08% | $55.87 | $26.86 | `[v_monthly_kpis.csv, adr]` |
| 2017-02-01 | 3,675 | 5,880 | $204,465.42 | 62.50% | $55.64 | $34.77 | `[v_monthly_kpis.csv, adr]` |
| **Resort G2 Total** | **29,524** | **57,120** | **$1,669,891.18** | **51.69%** | **$56.56** | **$29.23** | `[reports/findings_data.json]` |

- **Portfolio Group 2 Combined Total**:
  - Total hotel-months: **17 months**
  - Room nights sold: **57,618 nights**
  - Room nights available: **117,620 nights**
  - Realized room revenue: **$4,056,130.55**
  - Blended occupancy: **48.99%**
  - Blended ADR: **$70.40** [`reports/findings_data.json`, price_occupancy_gaps.group2_low_occ_low_adr.portfolio_summary]

---

### 3. Recommended Action
1. **Price Increases for Group 1 (High Occupancy, Low ADR)**:
   - **Dynamic BAR Escalation**: Implement yield management caps on discount allocations for June and September at Resort Hotel. Once forward occupancy reaches 70%, close out discounted wholesale/tour operator allotments and raise published BAR tiers into the high summer range ($120.00–$140.00).
   - **Minimum Length of Stay (MLOS)**: Enforce a 3-night MLOS over September and June weekends to filter out low-rate short stays and yield maximize available room nights.
2. **Demand Stimulation for Group 2 (Low Occupancy, Low ADR)**:
   - **Off-Peak Demand Generation**: Do not discount below established floors ($85 for City, $55 for Resort). Instead, activate targeted promotional programs:
     - *Corporate & MICE Segment Targeting*: Lisbon City Hotel should contract mid-week corporate conferences and government business in November–February, where commercial business travel is active.
     - *Extended Stay Leisure & "Workation" Packages*: Resort Hotel should market winter long-stay golf, wellness, and remote-work packages (e.g., "Stay 7 Nights, Pay 5" or inclusive dinner-and-spa packages) to northern European retirees and digital nomads.
     - *Local Resident & Weekend Staycation Promos*: Stimulate weekend leisure volume among domestic Portuguese travelers using value packaging rather than rate destruction.

---

### 4. Expected Impact (As a Scenario)

> [!WARNING]
> **Scenario, not forecast**:
> The calculations below represent analytical scenarios based on explicit historical baseline data. State caveat: higher prices would probably reduce occupancy and that the dataset cannot measure price elasticity. Conversely, demand stimulation scenarios assume that incremental promotional volume can be captured at historical baseline ADR without cannibalizing regular rate tiers or incurring unsustainable incremental operating costs.

#### Scenario B1: 5% ADR Increase on Group 1 Months with Occupancy Unchanged
- **Formula**:
  $$\Delta \text{Revenue} = \text{Revenue}_{\text{Group 1}} \times \text{Rate Increase \%}$$
  $$\text{New Revenue} = \text{Revenue}_{\text{Group 1}} + \Delta \text{Revenue}$$
- **Data Inputs** [`reports/findings_data.json`, price_occupancy_gaps.group1_high_occ_low_adr.scenarios.adr_increase_5pct]:
  - Historical Group 1 room revenue (September 2015 + June 2016): **$975,708.65** [`v_monthly_kpis.csv`]
  - Historical room nights sold: **10,813 nights** [`v_monthly_kpis.csv`]
  - Historical blended ADR: **$90.23**
  - Scenario rate increase: **5.0%** ($0.05$)
- **Calculation**:
  $$\Delta \text{Revenue} = \$975,708.65 \times 0.05 = \$48,785.43$$
  $$\text{New Revenue} = \$975,708.65 + \$48,785.43 = \$1,024,494.08$$
  $$\text{New Blended ADR} = \frac{\$1,024,494.08}{10,813} = \$94.75 \quad (+\$4.52/\text{night})$$
- **Scenario Result**:
  If ADR in these 2 months rose by 5% with occupancy unchanged, Resort Hotel room revenue would rise by **$48,785.43** (5% of the revenue of those months), increasing total realized revenue from $975,708.65 to $1,024,494.08.

#### Scenario B2: Elevating Group 1 ADR to the Hotel Window Average ($95.29)
- **Formula**:
  $$\Delta \text{Revenue} = (\text{Room Nights}_{\text{Group 1}} \times \text{Window ADR}) - \text{Revenue}_{\text{Group 1}}$$
- **Data Inputs** [`reports/findings_data.json`, price_occupancy_gaps.group1_high_occ_low_adr.scenarios.adr_brought_to_window_average]:
  - Historical room nights sold: **10,813 nights** [`v_monthly_kpis.csv`]
  - Resort Hotel Window ADR benchmark: **$95.29** [`v_hotel_totals.csv`, adr]
  - Historical Group 1 room revenue: **$975,708.65**
- **Calculation**:
  $$\Delta \text{Revenue} = (10,813 \times \$95.29) - \$975,708.65 = \$1,030,370.77 - \$975,708.65 = \$54,662.12$$
- **Scenario Result**:
  If ADR in these 2 months reached Resort Hotel's overall window average of $95.29 with occupancy unchanged, room revenue would rise by **$54,662.12**, yielding $1,030,370.77.

#### Scenario B3: Demand Stimulation in Group 2 Months (+5.0 Percentage Points Occupancy at Constant ADR)
- **Formula**:
  $$\Delta \text{Room Nights} = \text{Available Nights} \times \frac{\Delta \text{Occupancy \%}}{100}$$
  $$\Delta \text{Revenue} = \Delta \text{Room Nights} \times \text{Blended ADR}$$
  $$\text{New Revenue} = \text{Baseline Revenue} + \Delta \text{Revenue}$$
- **Data Inputs** [`reports/findings_data.json`, price_occupancy_gaps.group2_low_occ_low_adr]:
  - **City Hotel (8 months)**:
    - Available nights: **60,500 nights** [`v_monthly_kpis.csv`]
    - Baseline room nights sold: **28,094 nights** (46.44% occupancy)
    - Baseline room revenue: **$2,386,239.37**
    - Blended ADR: **$84.94**
    - Occupancy stimulation: **+5.0 percentage points** ($0.05$)
    - Calculation:
      $$\Delta \text{Room Nights} = 60,500 \times 0.05 = 3,025.0 \text{ nights}$$
      $$\Delta \text{Revenue} = 3,025.0 \times \$84.94 = \$256,943.50$$
      $$\text{New Revenue} = \$2,386,239.37 + \$256,943.50 = \$2,643,182.87$$
      $$\text{New Occupancy \%} = 46.44\% + 5.00\% = 51.44\%$$
  - **Resort Hotel (9 months)**:
    - Available nights: **57,120 nights** [`v_monthly_kpis.csv`]
    - Baseline room nights sold: **29,524 nights** (51.69% occupancy)
    - Baseline room revenue: **$1,669,891.18**
    - Blended ADR: **$56.56**
    - Occupancy stimulation: **+5.0 percentage points** ($0.05$)
    - Calculation:
      $$\Delta \text{Room Nights} = 57,120 \times 0.05 = 2,856.0 \text{ nights}$$
      $$\Delta \text{Revenue} = 2,856.0 \times \$56.56 = \$161,535.36$$
      $$\text{New Revenue} = \$1,669,891.18 + \$161,535.36 = \$1,831,426.54$$
      $$\text{New Occupancy \%} = 51.69\% + 5.00\% = 56.69\%$$
  - **Combined Portfolio Group 2 Impact**:
    $$\Delta \text{Total Room Nights} = 3,025.0 + 2,856.0 = 5,881.0 \text{ nights}$$
    $$\Delta \text{Total Revenue} = \$256,943.50 + \$161,535.36 = \$418,478.86$$
    $$\text{New Portfolio Revenue} = \$4,056,130.55 + \$418,478.86 = \$4,474,609.41$$
- **Scenario Result**:
  If demand stimulation programs stimulated occupancy by +5.0 percentage points across these 17 off-peak months with ADR held constant at historical levels, portfolio room revenue would rise by **$418,478.86** across **5,881 incremental room nights sold** ($256,943.50 at City Hotel and $161,535.36 at Resort Hotel).

---

## Analytical Summary Table: Decisions & Scenario Payoffs

| Scenario ID | Focus Area | Property | Target Cohort | Baseline Revenue ($) | Scenario Mechanism | Realized Impact ($) | Key Operational Caveat | Source Tag |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- | :--- |
| **Scenario A1** | Seasonality Peak Pricing | City Hotel | 22 nights $\ge 90\%$ capacity | $580,233.65 | +10% rate premium on compression dates | **+$58,023.37** | Scenario, not forecast; higher rates may reduce occupancy | `[reports/findings_data.json, pricing_rules_and_scenarios]` |
| **Scenario A2** | Seasonality Peak Pricing | City Hotel | 4 Peak season months (Apr–Jul) | $5,431,885.55 | +5% rate premium across peak calendar months | **+$271,594.28** | Scenario, not forecast; price elasticity unknown | `[reports/findings_data.json, pricing_rules_and_scenarios]` |
| **Scenario B1** | Price & Occupancy Gaps | Resort Hotel | 2 Group 1 months (2015-09, 2016-06) | $975,708.65 | +5% ADR increase on unconstrained peak volume | **+$48,785.43** | Scenario, not forecast; price elasticity unknown | `[reports/findings_data.json, price_occupancy_gaps]` |
| **Scenario B2** | Price & Occupancy Gaps | Resort Hotel | 2 Group 1 months (2015-09, 2016-06) | $975,708.65 | Close gap to property window ADR ($95.29) | **+$54,662.12** | Scenario, not forecast; relies on curtailing wholesale blocks | `[reports/findings_data.json, price_occupancy_gaps]` |
| **Scenario B3** | Price & Occupancy Gaps | Portfolio | 17 Group 2 off-peak winter months | $4,056,130.55 | +5.0 pp occupancy stimulation at stable ADR | **+$418,478.86** | Scenario, not forecast; ignores marginal servicing costs | `[reports/findings_data.json, price_occupancy_gaps]` |
