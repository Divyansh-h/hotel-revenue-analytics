# Truthful Resume Bullets for Hotel Revenue Analytics

These three alternative resume bullets highlight different aspects of the project (Analytics Engineering, Statistical Data Science, and Business Intelligence). 

Every cited metric is grounded strictly in [`reports/findings_data.json`](../reports/findings_data.json), and only tools physically implemented in the repository are referenced. Claims requiring manual verification of steps performed by hand in desktop applications are marked with **`[CONFIRM]`**.

---

### Option 1: Analytics Engineering & Revenue Operations Focus
> **Hotel Revenue & Analytics Pipeline (Python, PostgreSQL, SQL, Excel, OpenPyXL, Pytest)**
> - Engineered an end-to-end revenue analytics platform modeling 119,388 historical reservations and 248,261 stay nights across PostgreSQL and Python, structuring 17 relational views for monthly RevPAR tracking, capacity buffers, and commercial channel mix.
> - Formulated dynamic seasonal rate rules and a strategic commercial mix shift scenario (2,000 nights per hotel from Groups to Direct) modeling +$189,200.00 in net annual revenue gains.
> - Built a formula-only 15-sheet financial workbook in Excel via OpenPyXL and automated Python pipelines, **[CONFIRM: incorporating desktop PivotTables with multi-table slicers and parameterized Power Query M ETL queries]**, backed by an automated 30-step pipeline auditing 2,073 published numbers with zero discrepancies.

---

### Option 2: Data Science & Statistical Modeling Focus
> **Hospitality Predictive Pacing & Cancellation Modeling (Python, Pandas, Statsmodels, Scipy, NumPy)**
> - Diagnosed reservation cancellation dynamics across 119,388 bookings using non-parametric inferential statistics (Mann-Whitney U, chi-square, two-proportion z-tests) and multiple logistic regression (McFadden Pseudo $R^2 = 0.2674$).
> - Uncovered an administrative Portuguese wholesale group paradox driving an unexpected 99.36% Non-Refund cancellation rate (Cramer's $V = 0.4815$) and identified a +68.0-day median lead time divergence between canceled (113.0 days) and fulfilled stays (45.0 days).
> - Quantified $1,533,486.66 in upper-bound late cancellation revenue at risk across 14,841 room nights within 7 days of arrival, modeling a risk-mitigation framework to recover 1,484.1 room nights and $153,348.67 in preserved revenue.

---

### Option 3: Business Intelligence & Data Modeling Focus
> **Enterprise Business Intelligence & Yield Architecture (Power BI, DAX, Star Schema, SQL, PostgreSQL)**
> - Architected a dimensional star schema constellation (6 tables, 48 columns, 0 bidirectional joins) and authored 26 explicit DAX measures analyzing $25,187,186.16 in room revenue and a 37.04% portfolio cancellation rate.
> - **[CONFIRM: Assembled a 4-page executive Power BI report adhering to WCAG-compliant color-blind palettes]**, validating measures across 6 analytical scenarios and implementing 10th-percentile daily cancellation buffers (23 rooms City Hotel, 11 rooms Resort Hotel) to safeguard peak capacity without inflating guest walk risk.
> - Automated clean-room pipeline reproduction across 30 sequential data and modeling stages, eliminating all hardcoded figures and prohibited causal phrases across 3 executive strategy reports.

---

### Verification Note for `[CONFIRM]` Tags
Before including these bullets on a resume or portfolio:
- **`[CONFIRM: with multi-table slicer-linked PivotTables and Power Query automation]`**: Verify that you opened `excel/hotel_kpi_summary.xlsx` in desktop Excel, connected the Power Query queries (`excel/power_query/*.m`), and created the 4 PivotTables (`PT_Monthly`, `PT_Segment`, `PT_LeadTime`, `PT_Channel`) linked to the Hotel slicer per [`excel/PIVOT_BUILD_GUIDE.md`](../excel/PIVOT_BUILD_GUIDE.md).
- **[CONFIRM: Assembled a 4-page executive Power BI report...]**: Verify that you assembled the `.pbix` in Power BI Desktop following [`powerbi/BUILD_GUIDE.md`](../powerbi/BUILD_GUIDE.md), validated values against [`powerbi/validation_expected.csv`](../powerbi/validation_expected.csv), and saved screenshots to [`powerbi/screenshots/`](../powerbi/screenshots/).
