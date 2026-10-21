# Final Delivery & Manual Hand-Off Checklist

This checklist enumerates all manual steps required from the user to finalize the desktop visual layer, document visual assets, and synchronize the repository.

---

### Manual Action Items

- [ ] **Build the Power BI Report & Run Validation Checklist**
  - Open Power BI Desktop on Windows.
  - Follow the numbered instructions in [`powerbi/BUILD_GUIDE.md`](../powerbi/BUILD_GUIDE.md) to import queries, model relationships, add DAX measures, and assemble Pages 1 through 4.
  - Fill out and verify the 60 benchmark checks in [`powerbi/VALIDATION_CHECKLIST.md`](../powerbi/VALIDATION_CHECKLIST.md) against [`powerbi/validation_expected.csv`](../powerbi/validation_expected.csv).
  - Save the completed model as `powerbi/hotel_revenue_analytics.pbix`.

- [ ] **Build the Excel PivotTables, Power Query Queries & Slicer**
  - Open [`excel/hotel_kpi_summary.xlsx`](../excel/hotel_kpi_summary.xlsx) in desktop Excel.
  - Set the `DataFolder` parameter and load the 3 M queries (`q_monthly_kpis`, `q_segments`, `q_cancel_drivers`) to sheets `PQ_Monthly`, `PQ_Segments`, and `PQ_Cancel` per [`excel/POWER_QUERY_GUIDE.md`](../excel/POWER_QUERY_GUIDE.md).
  - Construct the 4 PivotTables (`PT_Monthly`, `PT_Segment`, `PT_LeadTime`, `PT_Channel`) and connect them via a shared Hotel Slicer per [`excel/PIVOT_BUILD_GUIDE.md`](../excel/PIVOT_BUILD_GUIDE.md).
  - Reconcile PivotTable grand totals against [`excel/inputs/pivot_expected_values.csv`](../excel/inputs/pivot_expected_values.csv).

- [ ] **Add Dashboard & Spreadsheet Screenshots**
  - Capture high-resolution images from Power BI Desktop and save them to:
    - `powerbi/screenshots/pbi_p1_executive_kpis.png`
    - `powerbi/screenshots/pbi_p2_booking_cancellations.png`
    - `powerbi/screenshots/pbi_p3_revenue_segments.png`
    - `powerbi/screenshots/pbi_p4_strategic_insights.png`
  - Capture screenshots from desktop Excel and save them to:
    - `excel/screenshots/excel_kpi_summary.png`
    - `excel/screenshots/excel_pivots.png`

- [ ] **Choose and Verify a License**
  - An MIT License has been generated in [`LICENSE`](../LICENSE) (selected in Phase 5). Confirm whether to keep MIT or replace with another open-source license.

- [ ] **Push to Remote GitHub Repository**
  - Verify `git status` is clean.
  - Push branch and tags to GitHub:
    ```bash
    git push origin main --tags
    ```
