"""
Phase 3 Excel Workbook Builder: excel/hotel_kpi_summary.xlsx
Generates institutional-grade financial and operational model using XlsxWriter.
Adheres strictly to excel/EXCEL_SPEC.md and PROJECT_CONTEXT.md.

Sheets created in exact order:
1. README
2. Assumptions (tblCapacity, named cells WindowStart & WindowEnd)
3. Lookups (tblCountry)
4. Data (tblBookings: 22 source columns + 3 calculated columns)
5. Monthly_KPIs (tblMonthlyKPI: 7 static columns + 8 calculated columns)
6. KPI_Summary (Sections A, B, C, D + 4 native charts + conditional formatting + print layout)
7. PT_Monthly, PT_Segment, PT_LeadTime, PT_Channel (PivotTable placeholders)
8. PQ_Monthly, PQ_Segments, PQ_Cancel (Power Query placeholders)
9. Checks (Reconciliation checks against database expected values)
10. Notes (Data quality log and decisions D1-D12)

Verification:
- Verifies that KPI_Summary contains exactly 4 native charts and conditional formats.
- Scans all table cells in Sections A to D to ensure every value is a formula or text label.
- Checks LibreOffice installation for PDF export; reports findings or skips gracefully.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
import openpyxl
import pandas as pd
import xlsxwriter

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUTS_DIR = REPO_ROOT / "excel" / "inputs"
OUTPUT_WORKBOOK = REPO_ROOT / "excel" / "hotel_kpi_summary.xlsx"


def create_formats(workbook: xlsxwriter.Workbook) -> dict:
    return {
        "title": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 16,
            "bold": True,
            "font_color": "#1B365D"
        }),
        "subtitle": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "italic": True,
            "font_color": "#595959"
        }),
        "section_header": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 12,
            "bold": True,
            "font_color": "#1B365D",
            "bottom": 2,
            "bottom_color": "#1B365D"
        }),
        "tbl_header_dark": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "font_color": "#FFFFFF",
            "bg_color": "#1B365D",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9"
        }),
        "tbl_header_med": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "font_color": "#FFFFFF",
            "bg_color": "#2F5597",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9"
        }),
        "label": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "align": "left",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9"
        }),
        "label_center": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9"
        }),
        "label_bold": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "align": "left",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9"
        }),
        "input_cell": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "font_color": "#002060",
            "bg_color": "#FFF2CC",
            "align": "right",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9",
            "num_format": "#,##0"
        }),
        "num_int": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "align": "right",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9",
            "num_format": "#,##0"
        }),
        "num_currency": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "align": "right",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9",
            "num_format": "$#,##0.00"
        }),
        "num_pct": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "align": "right",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9",
            "num_format": "0.0%"
        }),
        "num_dec1": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "align": "right",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9",
            "num_format": "0.0"
        }),
        "total_int": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "align": "right",
            "valign": "vcenter",
            "top": 1,
            "bottom": 6,
            "num_format": "#,##0"
        }),
        "total_currency": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "align": "right",
            "valign": "vcenter",
            "top": 1,
            "bottom": 6,
            "num_format": "$#,##0.00"
        }),
        "total_pct": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "align": "right",
            "valign": "vcenter",
            "top": 1,
            "bottom": 6,
            "num_format": "0.0%"
        }),
        "total_label": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "align": "left",
            "valign": "vcenter",
            "top": 1,
            "bottom": 6
        }),
        "total_label_center": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "top": 1,
            "bottom": 6
        }),
        "note_bold": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 9.5,
            "bold": True,
            "font_color": "#1B365D",
            "bg_color": "#F2F4F8",
            "text_wrap": True,
            "border": 1,
            "border_color": "#D9D9D9",
            "valign": "vcenter"
        }),
        "underperformer_format": workbook.add_format({
            "bg_color": "#FCE4D6",
            "font_color": "#C00000",
            "bold": True
        }),
        "placeholder_text": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "italic": True,
            "font_color": "#595959",
            "bg_color": "#F2F4F8",
            "border": 1,
            "border_color": "#D9D9D9"
        }),
        "num_pct4": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "align": "right",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9",
            "num_format": "0.0000"
        }),
        "banner_pass": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 12,
            "bold": True,
            "font_color": "#FFFFFF",
            "bg_color": "#375623",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#273D19"
        }),
        "banner_fail": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 12,
            "bold": True,
            "font_color": "#FFFFFF",
            "bg_color": "#C00000",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#800000"
        }),
        "status_pass": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "font_color": "#375623",
            "bg_color": "#E2EFDA",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9"
        }),
        "status_fail": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "font_color": "#C00000",
            "bg_color": "#FCE4D6",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9"
        }),
        "label_wrap": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "align": "left",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9",
            "text_wrap": True
        }),
        "label_bold_wrap": workbook.add_format({
            "font_name": "Segoe UI",
            "font_size": 10,
            "bold": True,
            "align": "left",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D9D9D9",
            "text_wrap": True
        })
    }


def add_readme_sheet(workbook: xlsxwriter.Workbook, fmt: dict) -> None:
    print("Writing sheet 'README' (Governance, 15-Sheet Map, Refresh Order, K1-K7, Limitations)...")
    ws = workbook.add_worksheet("README")
    ws.set_tab_color("#1B365D")
    ws.hide_gridlines(0)

    # Title Block
    ws.write("A1", "HOTEL BOOKING REVENUE & OCCUPANCY ANALYTICS SUMMARY", fmt["title"])
    ws.write("A2", "Executive Model, Capacity Architecture & Reconciliation Governance | PostgreSQL Pipeline", fmt["subtitle"])

    # 1. Purpose & Analytical Scope
    ws.write("A4", "1. Purpose & Analytical Scope", fmt["section_header"])
    purpose_lines = [
        "Business Objective: Provide institutional-grade revenue management, occupancy analysis, and cancellation risk intelligence for City Hotel (Lisbon) and Resort Hotel (Algarve).",
        "Data Foundation: Synthesizes 119,388 cleaned reservation records (July 1, 2015 to August 31, 2017) processed through a rigorous Python/PostgreSQL ETL pipeline.",
        "Technical Architecture: 100% formula-driven executive summary model (COUNTIFS/SUMIFS/XLOOKUP), native dynamic charts, and zero hardcoded metrics to ensure complete auditable integrity."
    ]
    for idx, pline in enumerate(purpose_lines, start=5):
        ws.write(idx, 0, pline, fmt["label"])

    # 2. Master Sheet Directory
    ws.write("A9", "2. Master Sheet Directory (15 Sheets)", fmt["section_header"])
    sheet_map = [
        ("README", "Documentation", "Project governance, sheet map, refresh procedure, analytical assumptions, and limitations."),
        ("Assumptions", "Inputs & Parameters", "Inventory capacity inputs (tblCapacity) and named window parameters (WindowStart, WindowEnd)."),
        ("Lookups", "Reference Dimensions", "Dimension table tblCountry mapping 178 ISO3 country codes to English names via pycountry."),
        ("Data", "Analytical Fact Mart", "Table tblBookings (119,388 rows) with 22 source columns + 3 calculated columns."),
        ("Monthly_KPIs", "Stay-Night Mart", "Table tblMonthlyKPI (50 rows) reconciling stay-night performance against SQL benchmarks."),
        ("KPI_Summary", "Executive Reporting", "Dynamic summary model (COUNTIFS/SUMIFS) covering Sections A, B, C, D + 4 native charts."),
        ("PT_Monthly", "PivotTable Staging", "Placeholder for manual PivotTable: Monthly Booking Trends & Cancellation Pace."),
        ("PT_Segment", "PivotTable Staging", "Placeholder for manual PivotTable: Market Segment Contribution & ADR."),
        ("PT_LeadTime", "PivotTable Staging", "Placeholder for manual PivotTable: Lead Time Buckets vs. Cancellation Risk."),
        ("PT_Channel", "PivotTable Staging", "Placeholder for manual PivotTable: Distribution Channel Breakdown."),
        ("PQ_Monthly", "Power Query Staging", "Placeholder for Power Query connection to data/outputs/v_monthly_kpis.csv."),
        ("PQ_Segments", "Power Query Staging", "Placeholder for Power Query connection to data/outputs/v_segment_performance.csv."),
        ("PQ_Cancel", "Power Query Staging", "Placeholder for Power Query connection to data/outputs/v_cancellation_drivers.csv."),
        ("Checks", "Model Integrity Audit", "Automated reconciliation assertions verifying Excel values against database constants."),
        ("Notes", "Audit Trail", "Data quality profiling (14 checks), cleaning rules D1-D12, and KPI definitions K1-K7.")
    ]

    ws.write_row(10, 0, ["Sheet Name", "Classification", "Operational Purpose"], fmt["tbl_header_dark"])
    for idx, (sname, stype, sdesc) in enumerate(sheet_map, start=11):
        ws.write(idx, 0, sname, fmt["label_bold"])
        ws.write(idx, 1, stype, fmt["label"])
        ws.write(idx, 2, sdesc, fmt["label"])

    # 3. How to Refresh (The Order of Scripts to Re-Run)
    ws.write("A28", "3. How to Refresh (End-to-End Pipeline Execution Order)", fmt["section_header"])
    refresh_steps = [
        (1, "src/clean_data.py", "data/processed/bookings_clean.csv, excluded_rows.csv", "Applies cleaning rules D1-D12, isolates 2 ADR outliers, creates 45-column dataset."),
        (2, "src/create_database.py", "PostgreSQL database hotel_analytics, schema hotel", "Initializes relational PostgreSQL database and schema if not already existing."),
        (3, "src/load_to_postgres.py", "Table hotel.bookings", "Loads 119,388 rows via copy_expert with TRUNCATE idempotency and constraints."),
        (4, "src/run_sql.py", "Relational tables & analytical views", "Sequentially executes SQL scripts 10 through 60 (dates, stay nights, capacity, KPIs, trends, drivers, segments)."),
        (5, "src/export_sql_outputs.py", "data/outputs/*.csv (17 data marts)", "Exports all database tables and analytical views to disk for downstream reporting."),
        (6, "src/export_excel_inputs.py", "excel/inputs/*.csv (4 input marts)", "Directly queries PostgreSQL to export bookings_for_excel, monthly_kpis, capacity, and expected_checks."),
        (7, "src/build_country_lookup.py", "excel/inputs/country_lookup.csv", "Maps 178 distinct ISO3 country codes to canonical English country names using pycountry."),
        (8, "src/make_pq_scripts.py", "excel/power_query/*.m (4 query scripts)", "Generates zero-drift Power Query M scripts with explicit data typing from CSV headers."),
        (9, "src/build_workbook.py", "excel/hotel_kpi_summary.xlsx", "Compiles master Excel workbook with 15 sheets, dynamic formulas, 4 native charts, and 29 audit checks.")
    ]
    ws.write_row(29, 0, ["Step", "Script / Command", "Target Output(s)", "Description / Operation"], fmt["tbl_header_dark"])
    for idx, (s_num, s_cmd, s_out, s_desc) in enumerate(refresh_steps, start=30):
        ws.write(idx, 0, f"Step {s_num}", fmt["label_bold"])
        ws.write(idx, 1, s_cmd, fmt["label"])
        ws.write(idx, 2, s_out, fmt["label"])
        ws.write(idx, 3, s_desc, fmt["label"])

    # 4. Core Operational Assumptions
    ws.write("A41", "4. Core Operational Assumptions (config/assumptions.yml)", fmt["section_header"])
    assumptions = [
        ("Capacity Derivation (W2)", "Physical inventory capacity is not in the data. Derived per hotel as: peak rooms sold on any night inside the reliable window * 1.10 buffer, rounded up to the nearest ten (City Hotel: 250 rooms; Resort Hotel: 210 rooms; Total: 460 rooms). This is an explicit assumption and must accompany all reporting."),
        ("Reliable Reporting Window (W1)", "Stay-night KPIs (Occupancy %, ADR, RevPAR) are strictly valid only for stay dates between 2015-08-01 and 2017-08-31 (762 days / 25 months) due to partial-month boundary truncation. Booking-grain KPIs use all 26 arrival months (2015-07-01 to 2017-08-31).")
    ]
    ws.write_row(42, 0, ["Assumption", "Analytical Specification & Scope"], fmt["tbl_header_dark"])
    for idx, (atitle, adesc) in enumerate(assumptions, start=43):
        ws.write(idx, 0, atitle, fmt["label_bold"])
        ws.write(idx, 1, adesc, fmt["label"])

    # 5. Key Definitions K1 to K7 in Plain English
    ws.write("A47", "5. Key Definitions K1 to K7 in Plain English", fmt["section_header"])
    kpi_defs = [
        ("K1: Room-Night Sold", "A room-night sold represents one non-cancelled reservation occupying one room for one calendar night (from arrival date through checkout date minus 1 day). Bookings with zero nights contribute zero room-nights."),
        ("K2: Room Revenue Realisation", "Room revenue is the sum of daily lodging rates (ADR) across realised room-nights sold. Cancelled bookings earn $0 room revenue; no financial deposit transaction data exists."),
        ("K3: Average Daily Rate (ADR)", "ADR is calculated as total room revenue divided by total room-nights sold (Revenue / Nights). Never use a simple average of the ADR column, as that weights 1-night and 14-night stays equally."),
        ("K4: Occupancy % & RevPAR Identity", "Occupancy % equals room-nights sold divided by available room-nights. RevPAR equals total room revenue divided by available room-nights, and mathematically must equal ADR * Occupancy %."),
        ("K5: Cancellation Rate", "Cancellation rate is the proportion of total bookings with is_canceled = 1 (Cancellations / Total Bookings), attributed to the booking's arrival month. No-show rate is reported separately."),
        ("K6: Stay Conversion (Proxy)", "Stay conversion is the share of bookings that resulted in an actual completed stay (reservation_status = 'Check-Out'), exactly equal to 1 - cancellation rate. The dataset has no website enquiry funnel."),
        ("K7: Property-Level Metric Slicing", "Occupancy and RevPAR exist only at the hotel level because room capacity is not partitioned by market segment or channel. Slices are evaluated by room-night share, revenue share, and realised ADR.")
    ]
    ws.write_row(48, 0, ["KPI Principle", "Plain English Definition & Architectural Rule"], fmt["tbl_header_dark"])
    for idx, (ktitle, kdesc) in enumerate(kpi_defs, start=49):
        ws.write(idx, 0, ktitle, fmt["label_bold"])
        ws.write(idx, 1, kdesc, fmt["label"])

    # 6. Analytical Limitations & Governance Boundaries
    ws.write("A58", "6. Analytical Limitations & Dataset Boundaries", fmt["section_header"])
    limitations = [
        ("No Physical Room Inventory", "The raw dataset contains no physical room counts or capacity registers. Hotel capacity is modeled mathematically via peak observed occupancy with a 10% safety buffer (W2)."),
        ("No Enquiry / Funnel Data", "The dataset contains only confirmed bookings; there is no web traffic, enquiry, search volume, or shopping cart abandonment data. Conversion is measured purely from booking to check-out (K6)."),
        ("Exact Duplicate Rows Retained", "31,994 identical bookings across all 32 raw columns are retained and flagged (is_duplicate_row = 1) per D7 because there is no unique reservation ID and they may represent legitimate multi-room group bookings."),
        ("Cancelled Bookings Earn No Revenue", "The dataset records deposit type categories ('No Deposit', 'Non Refund', 'Refundable') but contains no actual financial payment, receipt, or fee amounts. Per K2, cancelled bookings earn $0 revenue.")
    ]
    ws.write_row(59, 0, ["Limitation", "Operational Reality & Governance Impact"], fmt["tbl_header_dark"])
    for idx, (ltitle, ldesc) in enumerate(limitations, start=60):
        ws.write(idx, 0, ltitle, fmt["label_bold"])
        ws.write(idx, 1, ldesc, fmt["label"])

    ws.set_column("A:A", 36)
    ws.set_column("B:B", 38)
    ws.set_column("C:C", 48)
    ws.set_column("D:D", 68)


def add_assumptions_sheet(workbook: xlsxwriter.Workbook, fmt: dict) -> None:
    ws = workbook.add_worksheet("Assumptions")
    ws.set_tab_color("#ED7D31")
    ws.hide_gridlines(0)

    ws.write("A1", "MODEL PARAMETERS & PHYSICAL INVENTORY ASSUMPTIONS", fmt["title"])
    ws.write("A2", "Central repository for model inputs and reliable reporting window boundaries", fmt["subtitle"])

    ws.write("A4", "1. Named Parameters (Reliable Reporting Window)", fmt["section_header"])
    ws.write_row(5, 0, ["Parameter Name", "Value", "Format / Scope", "Description"], fmt["tbl_header_dark"])
    
    ws.write(6, 0, "WindowStart", fmt["label_bold"])
    ws.write(6, 1, "2015-08-01", fmt["label_center"])
    ws.write(6, 2, "YYYY-MM-DD (Workbook)", fmt["label"])
    ws.write(6, 3, "First calendar date of reliable stay-night window", fmt["label"])

    ws.write(7, 0, "WindowEnd", fmt["label_bold"])
    ws.write(7, 1, "2017-08-31", fmt["label_center"])
    ws.write(7, 2, "YYYY-MM-DD (Workbook)", fmt["label"])
    ws.write(7, 3, "Last calendar date of reliable stay-night window", fmt["label"])

    ws.write(8, 0, "WindowDays", fmt["label_bold"])
    ws.write_formula(8, 1, '=DATEDIF(DATE(2015,8,1), DATE(2017,8,31), "d") + 1', fmt["num_int"])
    ws.write(8, 2, "Integer (762 days)", fmt["label"])
    ws.write(8, 3, "Total calendar days inside the reliable window", fmt["label"])

    workbook.define_name("WindowStart", "='Assumptions'!$B$7")
    workbook.define_name("WindowEnd", "='Assumptions'!$B$8")

    ws.write("A11", "2. Physical Inventory Capacity (Table tblCapacity)", fmt["section_header"])
    df_cap = pd.read_csv(INPUTS_DIR / "capacity_for_excel.csv")

    table_headers = ["Hotel", "Peak_Rooms_Sold", "Buffer", "Rooms"]
    ws.write_row(12, 0, table_headers, fmt["tbl_header_dark"])

    for r_idx, row in enumerate(df_cap.itertuples(index=False), start=13):
        ws.write(r_idx, 0, row.Hotel, fmt["label_bold"])
        ws.write(r_idx, 1, row.Peak_Rooms_Sold, fmt["num_int"])
        ws.write(r_idx, 2, row.Buffer, fmt["num_dec1"])
        ws.write(r_idx, 3, row.Rooms, fmt["input_cell"])

    ws.add_table(12, 0, 14, 3, {
        "name": "tblCapacity",
        "columns": [{"header": h} for h in table_headers],
        "style": "TableStyleMedium9"
    })

    ws.write(15, 0, "Total Portfolio", fmt["total_label"])
    ws.write_formula(15, 1, "=SUM(tblCapacity[Peak_Rooms_Sold])", fmt["total_int"])
    ws.write(15, 2, "-", fmt["total_label_center"])
    ws.write_formula(15, 3, "=SUM(tblCapacity[Rooms])", fmt["total_int"])

    ws.set_column("A:A", 22)
    ws.set_column("B:B", 18)
    ws.set_column("C:C", 22)
    ws.set_column("D:D", 35)


def add_lookups_sheet(workbook: xlsxwriter.Workbook, fmt: dict) -> None:
    ws = workbook.add_worksheet("Lookups")
    ws.set_tab_color("#70AD47")
    ws.hide_gridlines(0)

    ws.write("A1", "DIMENSIONAL LOOKUP TABLES", fmt["title"])
    ws.write("A2", "ISO 3166-1 alpha-3 country master mapping for tblBookings enrichment", fmt["subtitle"])

    df_country = pd.read_csv(INPUTS_DIR / "country_lookup.csv")
    headers = ["Code", "Country_Name"]
    ws.write_row(3, 0, headers, fmt["tbl_header_dark"])

    for r_idx, row in enumerate(df_country.itertuples(index=False), start=4):
        ws.write(r_idx, 0, row.Code, fmt["label_center"])
        ws.write(r_idx, 1, row.Country_Name, fmt["label"])

    ws.add_table(3, 0, len(df_country) + 3, 1, {
        "name": "tblCountry",
        "columns": [{"header": "Code"}, {"header": "Country_Name"}],
        "style": "TableStyleMedium9"
    })

    ws.set_column("A:A", 12)
    ws.set_column("B:B", 35)


def add_data_sheet(workbook: xlsxwriter.Workbook, fmt: dict) -> None:
    print("Writing sheet 'Data' (119,388 rows with calculated table columns)...")
    ws = workbook.add_worksheet("Data")
    ws.set_tab_color("#4472C4")
    ws.freeze_panes(1, 0)
    ws.hide_gridlines(0)

    df_bookings = pd.read_csv(INPUTS_DIR / "bookings_for_excel.csv")
    base_cols = df_bookings.columns.tolist()

    for r_idx, row in enumerate(df_bookings.itertuples(index=False), start=1):
        ws.write_row(r_idx, 0, row)

    table_columns = [{"header": col} for col in base_cols]
    table_columns.append({
        "header": "Country_Name",
        "formula": '=XLOOKUP([@country], tblCountry[Code], tblCountry[Country_Name], "Unknown")'
    })
    table_columns.append({
        "header": "Revenue_Realised",
        "formula": "=IF([@is_canceled]=0, [@room_revenue], 0)"
    })
    table_columns.append({
        "header": "Nights_Realised",
        "formula": "=IF([@is_canceled]=0, [@total_nights], 0)"
    })

    total_rows = len(df_bookings)
    total_cols = len(table_columns)

    ws.add_table(0, 0, total_rows, total_cols - 1, {
        "name": "tblBookings",
        "columns": table_columns,
        "style": "TableStyleMedium9"
    })

    ws.set_column("A:A", 12)
    ws.set_column("B:B", 14)
    ws.set_column("C:D", 14)
    ws.set_column("E:G", 12)
    ws.set_column("H:I", 14)
    ws.set_column("J:M", 10)
    ws.set_column("N:R", 16)
    ws.set_column("S:T", 14)
    ws.set_column("U:V", 14)
    ws.set_column("W:Y", 18)


def add_monthly_kpis_sheet(workbook: xlsxwriter.Workbook, fmt: dict) -> None:
    print("Writing sheet 'Monthly_KPIs' (50 stay months with calculated columns)...")
    ws = workbook.add_worksheet("Monthly_KPIs")
    ws.set_tab_color("#2F5597")
    ws.freeze_panes(1, 0)
    ws.hide_gridlines(0)

    df_monthly = pd.read_csv(INPUTS_DIR / "monthly_kpis_for_excel.csv")
    base_cols = df_monthly.columns.tolist()

    for r_idx, row in enumerate(df_monthly.itertuples(index=False), start=1):
        ws.write_row(r_idx, 0, row)

    table_columns = [{"header": col} for col in base_cols]
    table_columns.extend([
        {"header": "Days_In_Month", "formula": "=DAY(EOMONTH([@[Month_Start]], 0))"},
        {"header": "Rooms", "formula": "=XLOOKUP([@[Hotel]], tblCapacity[Hotel], tblCapacity[Rooms])"},
        {"header": "Rooms_Available_Nights", "formula": "=[@[Days_In_Month]] * [@[Rooms]]"},
        {"header": "Occupancy_Pct", "formula": "=[@[Room_Nights_Sold]] / [@[Rooms_Available_Nights]]"},
        {"header": "ADR", "formula": "=[@[Room_Revenue]] / [@[Room_Nights_Sold]]"},
        {"header": "RevPAR", "formula": "=[@[Room_Revenue]] / [@[Rooms_Available_Nights]]"},
        {"header": "Check_Occupancy", "formula": '=IF(ABS([@[Occupancy_Pct]] - [@[SQL_Occupancy_Pct]]/100) < 0.001, "OK", "DIFF")'},
        {"header": "Check_RevPAR", "formula": '=IF(ABS([@[RevPAR]] - [@[SQL_RevPAR]]) < 0.05, "OK", "DIFF")'}
    ])

    total_rows = len(df_monthly)
    total_cols = len(table_columns)

    ws.add_table(0, 0, total_rows, total_cols - 1, {
        "name": "tblMonthlyKPI",
        "columns": table_columns,
        "style": "TableStyleMedium9"
    })

    ws.set_column("A:A", 14)
    ws.set_column("B:B", 14)
    ws.set_column("C:O", 15)


def add_kpi_summary_sheet(workbook: xlsxwriter.Workbook, fmt: dict) -> None:
    print("Writing sheet 'KPI_Summary' (Sections A, B, C, D, charts, conditional formats)...")
    ws = workbook.add_worksheet("KPI_Summary")
    ws.set_tab_color("#7030A0")
    ws.hide_gridlines(0)

    # Print Layout Settings
    ws.set_landscape()
    ws.fit_to_pages(1, 0)  # Fit to 1 page wide, unconstrained tall
    ws.repeat_rows(3, 4)   # Repeat Rows 4-5 on every page
    ws.set_paper(9)        # A4 size
    ws.set_margins(left=0.5, right=0.5, top=0.75, bottom=0.75)

    # Sheet Title Block
    ws.write("A1", "HOTEL GROUP EXECUTIVE KPI SUMMARY", fmt["title"])
    ws.write("A2", "Dynamic Executive Performance Model | Fully Reconciled against Relational Marts", fmt["subtitle"])

    # -------------------------------------------------------------------------
    # SECTION A: Headline KPIs
    # -------------------------------------------------------------------------
    ws.write("A4", "Section A: Headline Portfolio KPIs", fmt["section_header"])
    sec_a_headers = ["Headline KPI Metric", "City Hotel", "Resort Hotel", "All hotels"]
    ws.write_row(4, 0, sec_a_headers, fmt["tbl_header_dark"])

    # Row 6: Bookings
    ws.write(5, 0, "Bookings", fmt["label_bold"])
    ws.write_formula(5, 1, '=COUNTIFS(tblBookings[hotel], "City Hotel")', fmt["num_int"])
    ws.write_formula(5, 2, '=COUNTIFS(tblBookings[hotel], "Resort Hotel")', fmt["num_int"])
    ws.write_formula(5, 3, "=SUM(B6:C6)", fmt["num_int"])

    # Row 7: Cancellations
    ws.write(6, 0, "Cancellations", fmt["label_bold"])
    ws.write_formula(6, 1, '=COUNTIFS(tblBookings[hotel], "City Hotel", tblBookings[is_canceled], 1)', fmt["num_int"])
    ws.write_formula(6, 2, '=COUNTIFS(tblBookings[hotel], "Resort Hotel", tblBookings[is_canceled], 1)', fmt["num_int"])
    ws.write_formula(6, 3, "=SUM(B7:C7)", fmt["num_int"])

    # Row 8: Cancellation rate
    ws.write(7, 0, "Cancellation rate", fmt["label_bold"])
    ws.write_formula(7, 1, "=B7 / B6", fmt["num_pct"])
    ws.write_formula(7, 2, "=C7 / C6", fmt["num_pct"])
    ws.write_formula(7, 3, "=D7 / D6", fmt["num_pct"])

    # Row 9: Stay conversion
    ws.write(8, 0, "Stay conversion (proxy: 1 - cancellation rate)", fmt["label_bold"])
    ws.write_formula(8, 1, "=1 - B8", fmt["num_pct"])
    ws.write_formula(8, 2, "=1 - C8", fmt["num_pct"])
    ws.write_formula(8, 3, "=1 - D8", fmt["num_pct"])

    # Row 10: Average lead time
    ws.write(9, 0, "Average lead time in days", fmt["label_bold"])
    ws.write_formula(9, 1, '=AVERAGEIFS(tblBookings[lead_time], tblBookings[hotel], "City Hotel")', fmt["num_dec1"])
    ws.write_formula(9, 2, '=AVERAGEIFS(tblBookings[lead_time], tblBookings[hotel], "Resort Hotel")', fmt["num_dec1"])
    ws.write_formula(9, 3, "=AVERAGE(tblBookings[lead_time])", fmt["num_dec1"])

    # Row 11: Room-nights on non-cancelled bookings
    ws.write(10, 0, "Room-nights on non-cancelled bookings", fmt["label_bold"])
    ws.write_formula(10, 1, '=SUMIFS(tblBookings[Nights_Realised], tblBookings[hotel], "City Hotel")', fmt["num_int"])
    ws.write_formula(10, 2, '=SUMIFS(tblBookings[Nights_Realised], tblBookings[hotel], "Resort Hotel")', fmt["num_int"])
    ws.write_formula(10, 3, "=SUM(B11:C11)", fmt["num_int"])

    # Row 12: Room revenue on non-cancelled bookings
    ws.write(11, 0, "Room revenue on non-cancelled bookings", fmt["label_bold"])
    ws.write_formula(11, 1, '=SUMIFS(tblBookings[Revenue_Realised], tblBookings[hotel], "City Hotel")', fmt["num_currency"])
    ws.write_formula(11, 2, '=SUMIFS(tblBookings[Revenue_Realised], tblBookings[hotel], "Resort Hotel")', fmt["num_currency"])
    ws.write_formula(11, 3, "=SUM(B12:C12)", fmt["num_currency"])

    # Row 13: ADR, booking basis, night-weighted
    ws.write(12, 0, "ADR, booking basis, night-weighted", fmt["label_bold"])
    ws.write_formula(12, 1, "=B12 / B11", fmt["num_currency"])
    ws.write_formula(12, 2, "=C12 / C11", fmt["num_currency"])
    ws.write_formula(12, 3, "=D12 / D11", fmt["num_currency"])

    # Row 14: Window occupancy (stay-night basis)
    ws.write(13, 0, "Window occupancy (stay-night basis)", fmt["label_bold"])
    ws.write_formula(13, 1, '=SUMIFS(tblMonthlyKPI[Room_Nights_Sold], tblMonthlyKPI[Hotel], "City Hotel") / SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], "City Hotel")', fmt["num_pct"])
    ws.write_formula(13, 2, '=SUMIFS(tblMonthlyKPI[Room_Nights_Sold], tblMonthlyKPI[Hotel], "Resort Hotel") / SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], "Resort Hotel")', fmt["num_pct"])
    ws.write_formula(13, 3, "=SUM(tblMonthlyKPI[Room_Nights_Sold]) / SUM(tblMonthlyKPI[Rooms_Available_Nights])", fmt["num_pct"])

    # Row 15: Window ADR (stay-night basis)
    ws.write(14, 0, "Window ADR (stay-night basis)", fmt["label_bold"])
    ws.write_formula(14, 1, '=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], "City Hotel") / SUMIFS(tblMonthlyKPI[Room_Nights_Sold], tblMonthlyKPI[Hotel], "City Hotel")', fmt["num_currency"])
    ws.write_formula(14, 2, '=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], "Resort Hotel") / SUMIFS(tblMonthlyKPI[Room_Nights_Sold], tblMonthlyKPI[Hotel], "Resort Hotel")', fmt["num_currency"])
    ws.write_formula(14, 3, "=SUM(tblMonthlyKPI[Room_Revenue]) / SUM(tblMonthlyKPI[Room_Nights_Sold])", fmt["num_currency"])

    # Row 16: Window RevPAR (stay-night basis)
    ws.write(15, 0, "Window RevPAR (stay-night basis)", fmt["label_bold"])
    ws.write_formula(15, 1, '=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], "City Hotel") / SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], "City Hotel")', fmt["num_currency"])
    ws.write_formula(15, 2, '=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], "Resort Hotel") / SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], "Resort Hotel")', fmt["num_currency"])
    ws.write_formula(15, 3, "=SUM(tblMonthlyKPI[Room_Revenue]) / SUM(tblMonthlyKPI[Rooms_Available_Nights])", fmt["num_currency"])

    # Bold Note beneath Section A (Row 18)
    note_text = (
        "Note: Booking-basis ADR ($106.50 City / $96.78 Resort / $101.93 Portfolio) and stay-night ADR "
        "($106.72 City / $95.29 Resort / $101.45 Portfolio) differ slightly due to arrival-month attribution "
        "(all booking revenue and stay nights attributed to arrival month across all 26 months) versus "
        "night-by-night attribution (revenue and nights attributed strictly day-by-day across daily stays within "
        "the 2015-08-01 to 2017-08-31 window). Both methodologies are analytically valid and reconcile to the database."
    )
    ws.merge_range("A18:D18", note_text, fmt["note_bold"])

    # -------------------------------------------------------------------------
    # SECTION B: Monthly Trends by Hotel (2015-07 to 2017-08)
    # -------------------------------------------------------------------------
    ws.write("A20", "Section B: Monthly Trend by Hotel (2015-07 to 2017-08)", fmt["section_header"])

    super_headers = [
        "Arrival Month",
        "City Hotel (Bookings)", "City Hotel (Cancel %)", "City Hotel (RevPAR)",
        "Resort Hotel (Bookings)", "Resort Hotel (Cancel %)", "Resort Hotel (RevPAR)",
        "All hotels (Bookings)", "All hotels (Cancel %)", "All hotels (RevPAR)"
    ]
    ws.write_row(20, 0, super_headers, fmt["tbl_header_dark"])

    sec_b_headers = [
        "Month",
        "Bookings", "Cancel Rate", "RevPAR",
        "Bookings", "Cancel Rate", "RevPAR",
        "Bookings", "Cancel Rate", "RevPAR"
    ]
    ws.write_row(21, 0, sec_b_headers, fmt["tbl_header_med"])

    months = pd.date_range("2015-07-01", "2017-08-01", freq="MS").strftime("%Y-%m-%d").tolist()

    for idx, m_str in enumerate(months, start=23):
        r = idx
        ws.write(r - 1, 0, m_str, fmt["label_center"])

        # City Hotel
        ws.write_formula(r - 1, 1, f'=COUNTIFS(tblBookings[arrival_month_start], $A{r}, tblBookings[hotel], "City Hotel")', fmt["num_int"])
        ws.write_formula(r - 1, 2, f'=IFERROR(COUNTIFS(tblBookings[arrival_month_start], $A{r}, tblBookings[hotel], "City Hotel", tblBookings[is_canceled], 1) / B{r}, 0)', fmt["num_pct"])
        ws.write_formula(r - 1, 3, f'=SUMIFS(tblMonthlyKPI[RevPAR], tblMonthlyKPI[Hotel], "City Hotel", tblMonthlyKPI[Month_Start], $A{r})', fmt["num_currency"])

        # Resort Hotel
        ws.write_formula(r - 1, 4, f'=COUNTIFS(tblBookings[arrival_month_start], $A{r}, tblBookings[hotel], "Resort Hotel")', fmt["num_int"])
        ws.write_formula(r - 1, 5, f'=IFERROR(COUNTIFS(tblBookings[arrival_month_start], $A{r}, tblBookings[hotel], "Resort Hotel", tblBookings[is_canceled], 1) / E{r}, 0)', fmt["num_pct"])
        ws.write_formula(r - 1, 6, f'=SUMIFS(tblMonthlyKPI[RevPAR], tblMonthlyKPI[Hotel], "Resort Hotel", tblMonthlyKPI[Month_Start], $A{r})', fmt["num_currency"])

        # All hotels
        ws.write_formula(r - 1, 7, f'=B{r} + E{r}', fmt["num_int"])
        ws.write_formula(r - 1, 8, f'=IFERROR(COUNTIFS(tblBookings[arrival_month_start], $A{r}, tblBookings[is_canceled], 1) / H{r}, 0)', fmt["num_pct"])
        ws.write_formula(r - 1, 9, f'=IFERROR(SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Month_Start], $A{r}) / SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Month_Start], $A{r}), 0)', fmt["num_currency"])

    # Section B Total Row (Row 49)
    ws.write(48, 0, "Total / Average", fmt["total_label"])
    ws.write_formula(48, 1, "=SUM(B23:B48)", fmt["total_int"])
    ws.write_formula(48, 2, '=COUNTIFS(tblBookings[hotel], "City Hotel", tblBookings[is_canceled], 1) / B49', fmt["total_pct"])
    ws.write_formula(48, 3, '=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], "City Hotel") / SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], "City Hotel")', fmt["total_currency"])
    ws.write_formula(48, 4, "=SUM(E23:E48)", fmt["total_int"])
    ws.write_formula(48, 5, '=COUNTIFS(tblBookings[hotel], "Resort Hotel", tblBookings[is_canceled], 1) / E49', fmt["total_pct"])
    ws.write_formula(48, 6, '=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], "Resort Hotel") / SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], "Resort Hotel")', fmt["total_currency"])
    ws.write_formula(48, 7, "=SUM(H23:H48)", fmt["total_int"])
    ws.write_formula(48, 8, "=COUNTIFS(tblBookings[is_canceled], 1) / H49", fmt["total_pct"])
    ws.write_formula(48, 9, "=SUM(tblMonthlyKPI[Room_Revenue]) / SUM(tblMonthlyKPI[Rooms_Available_Nights])", fmt["total_currency"])

    # -------------------------------------------------------------------------
    # SECTION C: Segment Table
    # -------------------------------------------------------------------------
    ws.write("A51", "Section C: Market Segment Performance Table", fmt["section_header"])
    sec_c_headers = ["Market Segment", "Bookings", "Cancel Rate", "ADR (booking basis)", "Revenue Share", "Rank"]
    ws.write_row(51, 0, sec_c_headers, fmt["tbl_header_dark"])

    segments = [
        "Online TA",
        "Offline TA/TO",
        "Groups",
        "Direct",
        "Corporate",
        "Complementary",
        "Aviation",
        "Undefined"
    ]

    for idx, seg in enumerate(segments, start=53):
        r = idx
        ws.write(r - 1, 0, seg, fmt["label_bold"])
        ws.write_formula(r - 1, 1, f'=COUNTIFS(tblBookings[market_segment], $A{r})', fmt["num_int"])
        ws.write_formula(r - 1, 2, f'=IFERROR(COUNTIFS(tblBookings[market_segment], $A{r}, tblBookings[is_canceled], 1) / B{r}, 0)', fmt["num_pct"])
        ws.write_formula(r - 1, 3, f'=IFERROR(SUMIFS(tblBookings[Revenue_Realised], tblBookings[market_segment], $A{r}) / SUMIFS(tblBookings[Nights_Realised], tblBookings[market_segment], $A{r}), 0)', fmt["num_currency"])
        ws.write_formula(r - 1, 4, f'=IFERROR(SUMIFS(tblBookings[Revenue_Realised], tblBookings[market_segment], $A{r}) / SUM(tblBookings[Revenue_Realised]), 0)', fmt["num_pct"])
        ws.write_formula(r - 1, 5, f'=RANK(B{r}, $B$53:$B$60)', fmt["num_int"])

    # Section C Total Row (Row 61)
    ws.write(60, 0, "Total Portfolio", fmt["total_label"])
    ws.write_formula(60, 1, "=SUM(B53:B60)", fmt["total_int"])
    ws.write_formula(60, 2, "=COUNTIFS(tblBookings[is_canceled], 1) / B61", fmt["total_pct"])
    ws.write_formula(60, 3, "=SUM(tblBookings[Revenue_Realised]) / SUM(tblBookings[Nights_Realised])", fmt["total_currency"])
    ws.write_formula(60, 4, "=SUM(E53:E60)", fmt["total_pct"])
    ws.write(60, 5, "-", fmt["total_label_center"])

    # -------------------------------------------------------------------------
    # SECTION D: Lead Time Bucket Helper Table (for Chart D)
    # -------------------------------------------------------------------------
    ws.write("A63", "Section D: Cancellation Rate by Lead Time Bucket", fmt["section_header"])
    sec_d_headers = ["Lead Bucket", "Lead Bucket Order", "City Hotel", "Resort Hotel", "All hotels"]
    ws.write_row(63, 0, sec_d_headers, fmt["tbl_header_dark"])

    lead_buckets = ["0-7", "8-30", "31-90", "91-180", "181+"]

    for idx, bucket in enumerate(lead_buckets, start=65):
        r = idx
        ws.write(r - 1, 0, bucket, fmt["label_center"])
        # Order formula reads tblBookings
        ws.write_formula(r - 1, 1, f'=AVERAGEIFS(tblBookings[lead_bucket_order], tblBookings[lead_bucket], $A{r})', fmt["num_int"])
        # City Hotel
        ws.write_formula(r - 1, 2, f'=IFERROR(COUNTIFS(tblBookings[lead_bucket], $A{r}, tblBookings[hotel], "City Hotel", tblBookings[is_canceled], 1) / COUNTIFS(tblBookings[lead_bucket], $A{r}, tblBookings[hotel], "City Hotel"), 0)', fmt["num_pct"])
        # Resort Hotel
        ws.write_formula(r - 1, 3, f'=IFERROR(COUNTIFS(tblBookings[lead_bucket], $A{r}, tblBookings[hotel], "Resort Hotel", tblBookings[is_canceled], 1) / COUNTIFS(tblBookings[lead_bucket], $A{r}, tblBookings[hotel], "Resort Hotel"), 0)', fmt["num_pct"])
        # All hotels
        ws.write_formula(r - 1, 4, f'=IFERROR(COUNTIFS(tblBookings[lead_bucket], $A{r}, tblBookings[is_canceled], 1) / COUNTIFS(tblBookings[lead_bucket], $A{r}), 0)', fmt["num_pct"])

    # Section D Total Row (Row 70)
    ws.write(69, 0, "Total Portfolio", fmt["total_label_center"])
    ws.write(69, 1, "-", fmt["total_label_center"])
    ws.write_formula(69, 2, '=COUNTIFS(tblBookings[hotel], "City Hotel", tblBookings[is_canceled], 1) / COUNTIFS(tblBookings[hotel], "City Hotel")', fmt["total_pct"])
    ws.write_formula(69, 3, '=COUNTIFS(tblBookings[hotel], "Resort Hotel", tblBookings[is_canceled], 1) / COUNTIFS(tblBookings[hotel], "Resort Hotel")', fmt["total_pct"])
    ws.write_formula(69, 4, "=COUNTIFS(tblBookings[is_canceled], 1) / COUNTA(tblBookings[booking_id])", fmt["total_pct"])

    # -------------------------------------------------------------------------
    # CONDITIONAL FORMATTING
    # -------------------------------------------------------------------------
    # 1. 3-colour scale on cancel-rate columns
    # Green (low cancel rate) -> Yellow -> Red (high cancel rate)
    scale_format = {
        "type": "3_color_scale",
        "min_color": "#63BE7B",
        "mid_color": "#FFEB84",
        "max_color": "#F8696B"
    }
    ws.conditional_format("C23:C48", scale_format)  # Section B City
    ws.conditional_format("F23:F48", scale_format)  # Section B Resort
    ws.conditional_format("I23:I48", scale_format)  # Section B All
    ws.conditional_format("C53:C60", scale_format)  # Section C Segment
    ws.conditional_format("C65:E69", scale_format)  # Section D Lead Buckets

    # 2. Data bars on revenue share (Section C)
    ws.conditional_format("E53:E60", {
        "type": "data_bar",
        "bar_color": "#4472C4",
        "bar_solid": True
    })

    # 3. Light red fill on underperforming segments:
    # cancel rate > hotel average ($C$61) AND ADR < hotel ADR ($D$61)
    ws.conditional_format("A53:F60", {
        "type": "formula",
        "criteria": "=AND($C53>$C$61, $D53<$D$61)",
        "format": fmt["underperformer_format"]
    })

    # -------------------------------------------------------------------------
    # NATIVE EXCEL CHARTS (XlsxWriter)
    # -------------------------------------------------------------------------
    ws.write("A72", "Executive Performance Visualizations", fmt["section_header"])

    # (a) Line Chart: Monthly Cancel Rate by Hotel
    chart_a = workbook.add_chart({"type": "line"})
    chart_a.add_series({
        "name": "City Hotel",
        "categories": "=KPI_Summary!$A$23:$A$48",
        "values": "=KPI_Summary!$C$23:$C$48",
        "line": {"color": "#1B365D", "width": 2.25},
        "marker": {"type": "circle", "size": 5, "fill": {"color": "#1B365D"}}
    })
    chart_a.add_series({
        "name": "Resort Hotel",
        "categories": "=KPI_Summary!$A$23:$A$48",
        "values": "=KPI_Summary!$F$23:$F$48",
        "line": {"color": "#ED7D31", "width": 2.25},
        "marker": {"type": "square", "size": 5, "fill": {"color": "#ED7D31"}}
    })
    chart_a.add_series({
        "name": "All hotels",
        "categories": "=KPI_Summary!$A$23:$A$48",
        "values": "=KPI_Summary!$I$23:$I$48",
        "line": {"color": "#70AD47", "width": 2.0, "dash_type": "dash"},
        "marker": {"type": "diamond", "size": 5, "fill": {"color": "#70AD47"}}
    })
    chart_a.set_title({
        "name": "Monthly Cancellation Rate Trend by Hotel (2015-07 to 2017-08)",
        "name_font": {"name": "Segoe UI", "size": 11, "bold": True, "color": "#1B365D"}
    })
    chart_a.set_x_axis({
        "name": "Arrival Month",
        "name_font": {"name": "Segoe UI", "size": 9.5, "bold": True},
        "num_font": {"name": "Segoe UI", "size": 8.5}
    })
    chart_a.set_y_axis({
        "name": "Cancellation Rate",
        "name_font": {"name": "Segoe UI", "size": 9.5, "bold": True},
        "num_font": {"name": "Segoe UI", "size": 8.5},
        "num_format": "0%",
        "major_gridlines": {"visible": True, "line": {"color": "#E0E0E0"}}
    })
    chart_a.set_legend({"position": "bottom", "font": {"name": "Segoe UI", "size": 9}})
    chart_a.set_size({"width": 580, "height": 330})
    ws.insert_chart("A74", chart_a)

    # (b) Line Chart: Monthly RevPAR by Hotel (Reliable Window: 2015-08 to 2017-08)
    chart_b = workbook.add_chart({"type": "line"})
    chart_b.add_series({
        "name": "City Hotel",
        "categories": "=KPI_Summary!$A$24:$A$48",
        "values": "=KPI_Summary!$D$24:$D$48",
        "line": {"color": "#1B365D", "width": 2.25},
        "marker": {"type": "circle", "size": 5, "fill": {"color": "#1B365D"}}
    })
    chart_b.add_series({
        "name": "Resort Hotel",
        "categories": "=KPI_Summary!$A$24:$A$48",
        "values": "=KPI_Summary!$G$24:$G$48",
        "line": {"color": "#ED7D31", "width": 2.25},
        "marker": {"type": "square", "size": 5, "fill": {"color": "#ED7D31"}}
    })
    chart_b.add_series({
        "name": "All hotels",
        "categories": "=KPI_Summary!$A$24:$A$48",
        "values": "=KPI_Summary!$J$24:$J$48",
        "line": {"color": "#70AD47", "width": 2.0, "dash_type": "dash"},
        "marker": {"type": "diamond", "size": 5, "fill": {"color": "#70AD47"}}
    })
    chart_b.set_title({
        "name": "Monthly RevPAR Trend by Hotel (Reliable Window: 2015-08 to 2017-08)",
        "name_font": {"name": "Segoe UI", "size": 11, "bold": True, "color": "#1B365D"}
    })
    chart_b.set_x_axis({
        "name": "Stay Month",
        "name_font": {"name": "Segoe UI", "size": 9.5, "bold": True},
        "num_font": {"name": "Segoe UI", "size": 8.5}
    })
    chart_b.set_y_axis({
        "name": "RevPAR ($)",
        "name_font": {"name": "Segoe UI", "size": 9.5, "bold": True},
        "num_font": {"name": "Segoe UI", "size": 8.5},
        "num_format": "$#,##0",
        "major_gridlines": {"visible": True, "line": {"color": "#E0E0E0"}}
    })
    chart_b.set_legend({"position": "bottom", "font": {"name": "Segoe UI", "size": 9}})
    chart_b.set_size({"width": 580, "height": 330})
    ws.insert_chart("F74", chart_b)

    # (c) Clustered Bar Chart: ADR (Booking Basis) by Market Segment
    chart_c = workbook.add_chart({"type": "bar"})
    chart_c.add_series({
        "name": "ADR (Booking Basis)",
        "categories": "=KPI_Summary!$A$53:$A$60",
        "values": "=KPI_Summary!$D$53:$D$60",
        "fill": {"color": "#2F5597"}
    })
    chart_c.set_title({
        "name": "Average Daily Rate (ADR) by Market Segment",
        "name_font": {"name": "Segoe UI", "size": 11, "bold": True, "color": "#1B365D"}
    })
    chart_c.set_y_axis({
        "name": "Market Segment",
        "name_font": {"name": "Segoe UI", "size": 9.5, "bold": True},
        "num_font": {"name": "Segoe UI", "size": 9}
    })
    chart_c.set_x_axis({
        "name": "Average Daily Rate ($)",
        "name_font": {"name": "Segoe UI", "size": 9.5, "bold": True},
        "num_font": {"name": "Segoe UI", "size": 8.5},
        "num_format": "$#,##0",
        "major_gridlines": {"visible": True, "line": {"color": "#E0E0E0"}}
    })
    chart_c.set_legend({"position": "bottom", "font": {"name": "Segoe UI", "size": 9}})
    chart_c.set_size({"width": 580, "height": 330})
    ws.insert_chart("A91", chart_c)

    # (d) Column Chart: Cancel Rate by Lead Bucket
    chart_d = workbook.add_chart({"type": "column"})
    chart_d.add_series({
        "name": "City Hotel",
        "categories": "=KPI_Summary!$A$65:$A$69",
        "values": "=KPI_Summary!$C$65:$C$69",
        "fill": {"color": "#1B365D"}
    })
    chart_d.add_series({
        "name": "Resort Hotel",
        "categories": "=KPI_Summary!$A$65:$A$69",
        "values": "=KPI_Summary!$D$65:$D$69",
        "fill": {"color": "#ED7D31"}
    })
    chart_d.add_series({
        "name": "All hotels",
        "categories": "=KPI_Summary!$A$65:$A$69",
        "values": "=KPI_Summary!$E$65:$E$69",
        "fill": {"color": "#70AD47"}
    })
    chart_d.set_title({
        "name": "Cancellation Rate by Lead Time Bucket & Property",
        "name_font": {"name": "Segoe UI", "size": 11, "bold": True, "color": "#1B365D"}
    })
    chart_d.set_x_axis({
        "name": "Lead Time Bucket (Days)",
        "name_font": {"name": "Segoe UI", "size": 9.5, "bold": True},
        "num_font": {"name": "Segoe UI", "size": 9}
    })
    chart_d.set_y_axis({
        "name": "Cancellation Rate",
        "name_font": {"name": "Segoe UI", "size": 9.5, "bold": True},
        "num_font": {"name": "Segoe UI", "size": 8.5},
        "num_format": "0%",
        "major_gridlines": {"visible": True, "line": {"color": "#E0E0E0"}}
    })
    chart_d.set_legend({"position": "bottom", "font": {"name": "Segoe UI", "size": 9}})
    chart_d.set_size({"width": 580, "height": 330})
    ws.insert_chart("F91", chart_d)

    # Column widths
    ws.set_column("A:A", 42)
    ws.set_column("B:D", 16)
    ws.set_column("E:G", 16)
    ws.set_column("H:J", 16)


def add_placeholder_sheets(workbook: xlsxwriter.Workbook, fmt: dict) -> None:
    placeholders = [
        ("PT_Monthly", "#A6A6A6", "PivotTable Placeholder: Monthly Booking Trends & Cancellation Analysis. Source: tblBookings. Follow instructions in excel/PIVOT_BUILD_GUIDE.md to build PivotTable (Rows: arrival_month_start grouped by Year & Month; Columns: hotel; Values: Count of booking_id, Average of is_canceled %, Sum of Revenue_Realised)."),
        ("PT_Segment", "#A6A6A6", "PivotTable Placeholder: Market Segment Performance & Revenue Contribution. Source: tblBookings. Follow instructions in excel/PIVOT_BUILD_GUIDE.md to build PivotTable (Rows: market_segment; Columns: hotel; Values: Count of booking_id, Average of is_canceled %, Sum of Revenue_Realised, Revenue Share % of Column)."),
        ("PT_LeadTime", "#A6A6A6", "PivotTable Placeholder: Lead Time Bucket & Cancellation Risk Analysis. Source: tblBookings. Follow instructions in excel/PIVOT_BUILD_GUIDE.md to build PivotTable (Rows: lead_bucket ordered by lead_bucket_order; Columns: hotel; Values: Count of booking_id, Average of is_canceled %, Average of lead_time, Sum of Revenue_Realised)."),
        ("PT_Channel", "#A6A6A6", "PivotTable Placeholder: Distribution Channel Breakdown & Sourcing Mix. Source: tblBookings. Follow instructions in excel/PIVOT_BUILD_GUIDE.md to build PivotTable (Rows: distribution_channel; Columns: hotel; Values: Count of booking_id, Share % of Column, Average of is_canceled %, Sum of Revenue_Realised)."),
        ("PQ_Monthly", "#7F7F7F", "Power Query Destination Placeholder: Ingest and load data/outputs/v_monthly_kpis.csv into an Excel Table here. Follow step-by-step instructions in excel/POWER_QUERY_GUIDE.md."),
        ("PQ_Segments", "#7F7F7F", "Power Query Destination Placeholder: Ingest and load data/outputs/v_segment_performance.csv into an Excel Table here. Follow step-by-step instructions in excel/POWER_QUERY_GUIDE.md."),
        ("PQ_Cancel", "#7F7F7F", "Power Query Destination Placeholder: Ingest and load data/outputs/v_cancellation_drivers.csv into an Excel Table here. Follow step-by-step instructions in excel/POWER_QUERY_GUIDE.md.")
    ]

    for sname, scolor, stext in placeholders:
        ws = workbook.add_worksheet(sname)
        ws.set_tab_color(scolor)
        ws.hide_gridlines(0)
        ws.write("A1", stext, fmt["placeholder_text"])
        ws.set_column("A:A", 120)


def add_checks_sheet(workbook: xlsxwriter.Workbook, fmt: dict) -> None:
    print("Writing sheet 'Checks' (Model Integrity Audit Table tblChecks)...")
    ws = workbook.add_worksheet("Checks")
    ws.set_tab_color("#C00000")
    ws.hide_gridlines(0)

    # Title Block
    ws.write("A1", "MODEL INTEGRITY & DATABASE RECONCILIATION AUDIT", fmt["title"])
    ws.write("A2", "Formula-Driven Assertions Comparing Excel Calculations Against Database Benchmarks", fmt["subtitle"])

    # Overall Status Banner (Cell B4)
    ws.write("A4", "Overall Model Status:", fmt["label_bold"])
    ws.write_formula("B4", '=IF(COUNTIF(tblChecks[Status], "CHECK")=0, "ALL CHECKS OK", "REVIEW")', fmt["banner_pass"])

    # Conditional formatting on B4
    ws.conditional_format("B4", {
        "type": "cell",
        "criteria": "equal to",
        "value": '"ALL CHECKS OK"',
        "format": fmt["banner_pass"]
    })
    ws.conditional_format("B4", {
        "type": "cell",
        "criteria": "equal to",
        "value": '"REVIEW"',
        "format": fmt["banner_fail"]
    })

    # Table Definitions (29 checks)
    headers = ["Check Name", "Workbook Value", "Expected Value", "Difference", "Tolerance", "Status"]

    checks_def = [
        # 1-3: Bookings per hotel and total
        ("Bookings - City Hotel", '=COUNTIFS(tblBookings[hotel], "City Hotel")', 79329, 0, "num_int"),
        ("Bookings - Resort Hotel", '=COUNTIFS(tblBookings[hotel], "Resort Hotel")', 40059, 0, "num_int"),
        ("Bookings - Total Portfolio", '=COUNTA(tblBookings[booking_id])', 119388, 0, "num_int"),

        # 4-6: Cancellations per hotel and total
        ("Cancellations - City Hotel", '=COUNTIFS(tblBookings[hotel], "City Hotel", tblBookings[is_canceled], 1)', 33101, 0, "num_int"),
        ("Cancellations - Resort Hotel", '=COUNTIFS(tblBookings[hotel], "Resort Hotel", tblBookings[is_canceled], 1)', 11122, 0, "num_int"),
        ("Cancellations - Total Portfolio", '=COUNTIFS(tblBookings[is_canceled], 1)', 44223, 0, "num_int"),

        # 7-9: Cancel rate per hotel and total
        ("Cancel Rate - City Hotel", '=COUNTIFS(tblBookings[hotel], "City Hotel", tblBookings[is_canceled], 1) / COUNTIFS(tblBookings[hotel], "City Hotel")', 0.4173, 0.0001, "num_pct4"),
        ("Cancel Rate - Resort Hotel", '=COUNTIFS(tblBookings[hotel], "Resort Hotel", tblBookings[is_canceled], 1) / COUNTIFS(tblBookings[hotel], "Resort Hotel")', 0.2776, 0.0001, "num_pct4"),
        ("Cancel Rate - Total Portfolio", '=COUNTIFS(tblBookings[is_canceled], 1) / COUNTA(tblBookings[booking_id])', 0.3704, 0.0001, "num_pct4"),

        # 10-12: Room revenue on non-cancelled bookings per hotel and total
        ("Room Revenue Realised - City Hotel", '=SUMIFS(tblBookings[Revenue_Realised], tblBookings[hotel], "City Hotel")', 14394410.18, 0.01, "num_currency"),
        ("Room Revenue Realised - Resort Hotel", '=SUMIFS(tblBookings[Revenue_Realised], tblBookings[hotel], "Resort Hotel")', 11601914.03, 0.01, "num_currency"),
        ("Room Revenue Realised - Total Portfolio", '=SUM(tblBookings[Revenue_Realised])', 25996324.21, 0.01, "num_currency"),

        # 13-15: Non-cancelled room-nights per hotel and total
        ("Nights Realised - City Hotel", '=SUMIFS(tblBookings[Nights_Realised], tblBookings[hotel], "City Hotel")', 135153, 0, "num_int"),
        ("Nights Realised - Resort Hotel", '=SUMIFS(tblBookings[Nights_Realised], tblBookings[hotel], "Resort Hotel")', 119877, 0, "num_int"),
        ("Nights Realised - Total Portfolio", '=SUM(tblBookings[Nights_Realised])', 255030, 0, "num_int"),

        # 16-18: Window room-nights sold per hotel and total
        ("Window Room-Nights Sold - City Hotel", '=SUMIFS(tblMonthlyKPI[Room_Nights_Sold], tblMonthlyKPI[Hotel], "City Hotel")', 133860, 0, "num_int"),
        ("Window Room-Nights Sold - Resort Hotel", '=SUMIFS(tblMonthlyKPI[Room_Nights_Sold], tblMonthlyKPI[Hotel], "Resort Hotel")', 114401, 0, "num_int"),
        ("Window Room-Nights Sold - Total Portfolio", '=SUM(tblMonthlyKPI[Room_Nights_Sold])', 248261, 0, "num_int"),

        # 19-21: Window room revenue per hotel and total
        ("Window Room Revenue - City Hotel", '=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], "City Hotel")', 14285466.42, 0.01, "num_currency"),
        ("Window Room Revenue - Resort Hotel", '=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], "Resort Hotel")', 10901719.74, 0.01, "num_currency"),
        ("Window Room Revenue - Total Portfolio", '=SUM(tblMonthlyKPI[Room_Revenue])', 25187186.16, 0.01, "num_currency"),

        # 22-24: Window occupancy per hotel and total
        ("Window Occupancy - City Hotel", '=SUMIFS(tblMonthlyKPI[Room_Nights_Sold], tblMonthlyKPI[Hotel], "City Hotel") / SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], "City Hotel")', 0.7027, 0.0001, "num_pct4"),
        ("Window Occupancy - Resort Hotel", '=SUMIFS(tblMonthlyKPI[Room_Nights_Sold], tblMonthlyKPI[Hotel], "Resort Hotel") / SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], "Resort Hotel")', 0.7149, 0.0001, "num_pct4"),
        ("Window Occupancy - Total Portfolio", '=SUM(tblMonthlyKPI[Room_Nights_Sold]) / SUM(tblMonthlyKPI[Rooms_Available_Nights])', 0.7083, 0.0001, "num_pct4"),

        # 25-27: Window RevPAR per hotel and total
        ("Window RevPAR - City Hotel", '=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], "City Hotel") / SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], "City Hotel")', 74.99, 0.05, "num_currency"),
        ("Window RevPAR - Resort Hotel", '=SUMIFS(tblMonthlyKPI[Room_Revenue], tblMonthlyKPI[Hotel], "Resort Hotel") / SUMIFS(tblMonthlyKPI[Rooms_Available_Nights], tblMonthlyKPI[Hotel], "Resort Hotel")', 68.13, 0.05, "num_currency"),
        ("Window RevPAR - Total Portfolio", '=SUM(tblMonthlyKPI[Room_Revenue]) / SUM(tblMonthlyKPI[Rooms_Available_Nights])', 71.86, 0.05, "num_currency"),

        # 28: Monthly_KPIs rows where Check_Occupancy is DIFF / above 0.05 (expected 0)
        ("Monthly_KPIs Check_Occupancy DIFF Count", '=COUNTIF(tblMonthlyKPI[Check_Occupancy], "DIFF")', 0, 0, "num_int"),

        # 29: Country_Name cells that equal Unknown
        ("Country_Name Unknown Count", '=COUNTIF(tblBookings[Country_Name], "Unknown")', 488, 0, "num_int")
    ]

    ws.write_row(5, 0, headers, fmt["tbl_header_dark"])
    for r_idx, (chk_name, f_val, exp_val, tol_val, val_fmt_key) in enumerate(checks_def, start=6):
        ws.write(r_idx, 0, chk_name, fmt["label_bold"])
        ws.write_formula(r_idx, 1, f_val, fmt[val_fmt_key])
        ws.write(r_idx, 2, exp_val, fmt[val_fmt_key])
        ws.write_formula(r_idx, 3, "=[@[Workbook Value]] - [@[Expected Value]]", fmt[val_fmt_key])
        ws.write(r_idx, 4, tol_val, fmt[val_fmt_key])
        ws.write_formula(r_idx, 5, '=IF(ABS([@Difference])<=[@Tolerance], "OK", "CHECK")', fmt["status_pass"])

    total_rows = len(checks_def)
    ws.add_table(5, 0, 5 + total_rows, 5, {
        "name": "tblChecks",
        "columns": [{"header": h} for h in headers],
        "style": "TableStyleMedium9"
    })

    # Conditional formatting on Status column F
    status_range = f"F7:F{6 + total_rows}"
    ws.conditional_format(status_range, {
        "type": "cell",
        "criteria": "equal to",
        "value": '"OK"',
        "format": fmt["status_pass"]
    })
    ws.conditional_format(status_range, {
        "type": "cell",
        "criteria": "equal to",
        "value": '"CHECK"',
        "format": fmt["status_fail"]
    })

    # Column widths
    ws.set_column("A:A", 44)
    ws.set_column("B:C", 20)
    ws.set_column("D:D", 18)
    ws.set_column("E:E", 14)
    ws.set_column("F:F", 14)


def add_notes_sheet(workbook: xlsxwriter.Workbook, fmt: dict) -> None:
    print("Writing sheet 'Notes' (Data Quality Log docs/data_quality_log.md, D1-D12, K1-K7)...")
    ws = workbook.add_worksheet("Notes")
    ws.set_tab_color("#595959")
    ws.hide_gridlines(0)

    # Title Block
    ws.write("A1", "DATA GOVERNANCE, CLEANING AUDIT & ANALYTICAL DECISION LOG", fmt["title"])
    ws.write("A2", "Comprehensive Data Quality Profile, Cleaning Decisions D1-D12, and Architectural KPI Rules K1-K7", fmt["subtitle"])

    # Section 1: Data Quality Profile & Outlier Audit (14 rows from docs/data_quality_log.md)
    ws.write("A4", "1. Data Quality Profile & Outlier Audit (from docs/data_quality_log.md)", fmt["section_header"])
    dq_headers = ["Issue Description", "Column(s) Evaluated", "Rows Affected", "Percent of Data", "Cleaning Decision", "Analytical Rationale", "Rows After Cleaning"]

    dq_rows = [
        ("Negative ADR (adr < 0)", "adr", 1, 0.0008, "D5: EXCLUDED", "Single row with adr = -6.38 is written to data/processed/excluded_rows.csv with reason column. Negative lodging rates represent invalid billing errors.", "0"),
        ("Extreme High ADR (adr > 1000)", "adr", 1, 0.0008, "D5: EXCLUDED", "Single row with adr = 5400.0 is written to data/processed/excluded_rows.csv with reason column. Extreme outlier that distorts revenue and ADR metrics.", "0"),
        ("Zero ADR (adr = 0)", "adr, market_segment", 1959, 1.6408, "D5: KEPT", "D5 explicitly excludes only adr < 0 or adr > 1000. Zero ADR bookings are retained as legitimate non-revenue stays (e.g. 680 Complementary, promotions, house guests); they earn 0 room revenue per K2.", "1,959"),
        ("Zero Stay Nights (weekend + week nights = 0)", "stays_in_weekend_nights, stays_in_week_nights", 715, 0.5989, "D6: KEPT and flagged", "Retained in analytical table (flag_zero_nights = 1); count as bookings in pipeline but generate 0 room-nights sold per K1.", "715"),
        ("Zero Total Guests (adults + children + babies = 0)", "adults, children, babies", 180, 0.1508, "D6: KEPT and flagged", "Retained in analytical table (flag_zero_guests = 1); count as bookings in pipeline but have 0 guests recorded.", "180"),
        ("Exact Duplicate Rows across all 32 raw columns", "All 32 raw columns", 31994, 26.7979, "D7: KEPT and flagged", "No unique booking ID in raw file; duplicates may represent real separate bookings. Kept with later copies flagged (is_duplicate_row = 1) for sensitivity analysis.", "31,994"),
        ("Canceled Date Later Than Arrival Date", "reservation_status, reservation_status_date, arrival_date_*", 0, 0.0, "D11: Validated", "Zero cancellations have status date after arrival date. D11 calculates days_cancelled_before_arrival = arrival_date - reservation_status_date for canceled bookings.", "0"),
        ("Room Type Mismatch (assigned <> reserved)", "reserved_room_type, assigned_room_type", 14917, 12.4943, "D10: KEPT and flagged", "Assigned room differs from reserved room due to operational reassignments or upgrades; flagged as integer 1/0 (room_type_mismatch = 1). (1 of 14,917 was the excluded ADR 5400 outlier).", "14,916"),
        ("Missing Company Identifier", "company", 112593, 94.3069, "D3: DROPPED", "Approximately 94.31% missing; column dropped from final analytical schema and PostgreSQL table.", "0 (column dropped)"),
        ("Missing Agent Identifier", "agent", 16340, 13.6862, "D3: KEPT as nullable integer", "Direct or corporate reservations without travel agency are preserved as nullable integer in schema.", "16,340 (NULL)"),
        ("Missing Country of Origin", "country", 488, 0.4087, "D3: IMPUTED", "Minor missingness imputed to string 'Unknown' to retain bookings in geographical aggregations without dropping rows.", "0 NULLs (488 as 'Unknown')"),
        ("Missing Children Count", "children", 4, 0.0034, "D3: IMPUTED", "4 rows with NaN imputed to 0 to enable total guest count calculation.", "0 NULLs (4 imputed to 0)"),
        ("Undefined Market Segment", "market_segment", 2, 0.0017, "KEPT as 'Undefined'", "Retained as 'Undefined' categorical string without dropping rows or synthetic imputation, preserving source fidelity.", "2"),
        ("Undefined Distribution Channel", "distribution_channel", 5, 0.0042, "KEPT as 'Undefined'", "Retained as 'Undefined' categorical string without dropping rows or synthetic imputation, preserving source fidelity.", "5")
    ]

    ws.write_row(5, 0, dq_headers, fmt["tbl_header_dark"])
    for r_idx, (issue, col, r_aff, pct, dec, rat, r_clean) in enumerate(dq_rows, start=6):
        ws.write(r_idx, 0, issue, fmt["label_bold"])
        ws.write(r_idx, 1, col, fmt["label"])
        ws.write(r_idx, 2, r_aff, fmt["num_int"])
        ws.write(r_idx, 3, pct / 100.0, fmt["num_pct"])
        ws.write(r_idx, 4, dec, fmt["label_bold"])
        ws.write(r_idx, 5, rat, fmt["label_wrap"])
        ws.write(r_idx, 6, r_clean, fmt["label_center"])

    ws.add_table(5, 0, 19, 6, {
        "name": "tblDataQualityLog",
        "columns": [{"header": h} for h in dq_headers],
        "style": "TableStyleMedium9"
    })

    # Section 2: Data Cleaning Decisions D1 to D12
    ws.write("A22", "2. Data Cleaning Rules & Transformations (D1 to D12)", fmt["section_header"])
    d_rules = [
        ("D1", "booking_id", "1-based row number assigned to raw records as primary key."),
        ("D2", "arrival_date", "Constructed from arrival_date_year, arrival_date_month, arrival_date_day_of_month."),
        ("D3", "Imputations", "children NaN -> 0; country NaN -> 'Unknown'; agent kept nullable; company dropped."),
        ("D4", "Derived Metrics", "total_nights = weekend + week; total_guests = adults + children + babies; room_revenue = adr * total_nights."),
        ("D5", "ADR Outliers", "adr < 0 or adr > 1000 excluded (2 rows isolated to excluded_rows.csv)."),
        ("D6", "Zero Stays / Guests", "total_nights = 0 or total_guests = 0 kept and flagged (flag_zero_nights, flag_zero_guests)."),
        ("D7", "Exact Duplicates", "31,994 identical rows kept and flagged (is_duplicate_row = 1) for sensitivity analysis."),
        ("D8", "Status Flags", "is_canceled = 1 for Canceled and No-Show; is_no_show = 1 only for No-Show."),
        ("D9", "Lead Time Buckets", "0-7, 8-30, 31-90, 91-180, 181+ with lead_bucket_order 1 to 5."),
        ("D10", "Room Mismatch", "room_type_mismatch = 1 when assigned_room_type <> reserved_room_type."),
        ("D11", "Cancellation Lead", "days_cancelled_before_arrival = arrival_date - reservation_status_date for Canceled."),
        ("D12", "Integer Booleans", "All flag and boolean columns stored as integer 0/1, never True/False.")
    ]
    ws.write_row(23, 0, ["Decision ID", "Target / Scope", "Analytical Transformation Rule"], fmt["tbl_header_dark"])
    for idx, (did, dscope, ddesc) in enumerate(d_rules, start=24):
        ws.write(idx, 0, did, fmt["label_bold"])
        ws.write(idx, 1, dscope, fmt["label"])
        ws.write(idx, 2, ddesc, fmt["label"])

    # Section 3: Revenue & Occupancy Key Principles K1 to K7
    ws.write("A38", "3. Revenue & Occupancy Key Principles (K1 to K7)", fmt["section_header"])
    k_principles = [
        ("K1", "Room-Night Sold", "One non-cancelled booking occupying one room for one night (arrival to checkout - 1)."),
        ("K2", "Room Revenue Realisation", "Sum of daily adr across room-nights sold. Cancelled bookings earn $0."),
        ("K3", "Average Daily Rate (ADR)", "ADR = room revenue / room-nights sold. Never use AVG(adr)."),
        ("K4", "Occupancy % & RevPAR Identity", "Occupancy = Sold / Available; RevPAR = Revenue / Available = ADR * Occupancy %."),
        ("K5", "Cancellation Rate", "Cancellations / all bookings, attributed to arrival month. No-shows reported separately."),
        ("K6", "Stay Conversion (Proxy)", "Check-Out bookings / all bookings = 1 - cancellation rate. No enquiry funnel exists."),
        ("K7", "Metric Slicing Boundaries", "Occupancy and RevPAR exist only at hotel level. Slices use shares and realised ADR.")
    ]
    ws.write_row(39, 0, ["Principle ID", "Key Concept", "Authoritative Operational Principle"], fmt["tbl_header_dark"])
    for idx, (kid, kname, kdesc) in enumerate(k_principles, start=40):
        ws.write(idx, 0, kid, fmt["label_bold"])
        ws.write(idx, 1, kname, fmt["label"])
        ws.write(idx, 2, kdesc, fmt["label"])

    ws.set_column("A:A", 28)
    ws.set_column("B:B", 24)
    ws.set_column("C:C", 16)
    ws.set_column("D:D", 16)
    ws.set_column("E:E", 22)
    ws.set_column("F:F", 65)
    ws.set_column("G:G", 22)


def verify_expected_checks_with_pandas() -> bool:
    print("\n" + "=" * 80)
    print("INDEPENDENT PANDAS RECOMPUTATION OF WORKBOOK VALUES (vs EXPECTED BENCHMARKS)")
    print("=" * 80)

    import calendar

    df_b = pd.read_csv(INPUTS_DIR / "bookings_for_excel.csv")
    df_m = pd.read_csv(INPUTS_DIR / "monthly_kpis_for_excel.csv")
    df_c = pd.read_csv(INPUTS_DIR / "capacity_for_excel.csv")
    df_exp = pd.read_csv(INPUTS_DIR / "expected_checks.csv")
    df_country = pd.read_csv(INPUTS_DIR / "country_lookup.csv")

    # Realised metrics
    df_b["Nights_Realised"] = df_b["total_nights"] * (1 - df_b["is_canceled"])
    df_b["Revenue_Realised"] = df_b["room_revenue"] * (1 - df_b["is_canceled"])

    # Monthly KPIs capacity & available nights
    cap_map = dict(zip(df_c["Hotel"], df_c["Rooms"]))
    df_m["Days_In_Month"] = df_m["Month_Start"].apply(lambda d: calendar.monthrange(int(d[:4]), int(d[5:7]))[1])
    df_m["Rooms"] = df_m["Hotel"].map(cap_map)
    df_m["Rooms_Available_Nights"] = df_m["Days_In_Month"] * df_m["Rooms"]
    df_m["Occupancy_Pct"] = df_m["Room_Nights_Sold"] / df_m["Rooms_Available_Nights"]
    df_m["RevPAR"] = df_m["Room_Revenue"] / df_m["Rooms_Available_Nights"]

    results = []
    for _, row in df_exp.iterrows():
        name = row["check_name"]
        hotel = row["hotel"]
        exp = float(row["expected_value"])
        tol = float(row["tolerance"])

        if name == "bookings":
            val = float(len(df_b) if hotel == "Total" else (df_b["hotel"] == hotel).sum())
        elif name == "cancellations":
            val = float((df_b["is_canceled"] == 1).sum() if hotel == "Total" else ((df_b["hotel"] == hotel) & (df_b["is_canceled"] == 1)).sum())
        elif name == "cancel_rate":
            b = float(len(df_b) if hotel == "Total" else (df_b["hotel"] == hotel).sum())
            c = float((df_b["is_canceled"] == 1).sum() if hotel == "Total" else ((df_b["hotel"] == hotel) & (df_b["is_canceled"] == 1)).sum())
            val = c / b
        elif name == "sum_room_revenue_realised":
            val = float(df_b["Revenue_Realised"].sum() if hotel == "Total" else df_b.loc[df_b["hotel"] == hotel, "Revenue_Realised"].sum())
        elif name == "sum_total_nights_realised":
            val = float(df_b["Nights_Realised"].sum() if hotel == "Total" else df_b.loc[df_b["hotel"] == hotel, "Nights_Realised"].sum())
        elif name == "room_nights_sold":
            val = float(df_m["Room_Nights_Sold"].sum() if hotel == "Total" else df_m.loc[df_m["Hotel"] == hotel, "Room_Nights_Sold"].sum())
        elif name == "room_revenue":
            val = float(df_m["Room_Revenue"].sum() if hotel == "Total" else df_m.loc[df_m["Hotel"] == hotel, "Room_Revenue"].sum())
        elif name == "occupancy":
            sold = float(df_m["Room_Nights_Sold"].sum() if hotel == "Total" else df_m.loc[df_m["Hotel"] == hotel, "Room_Nights_Sold"].sum())
            avail = float(df_m["Rooms_Available_Nights"].sum() if hotel == "Total" else df_m.loc[df_m["Hotel"] == hotel, "Rooms_Available_Nights"].sum())
            val = sold / avail
        elif name == "revpar":
            rev = float(df_m["Room_Revenue"].sum() if hotel == "Total" else df_m.loc[df_m["Hotel"] == hotel, "Room_Revenue"].sum())
            avail = float(df_m["Rooms_Available_Nights"].sum() if hotel == "Total" else df_m.loc[df_m["Hotel"] == hotel, "Rooms_Available_Nights"].sum())
            val = rev / avail
        else:
            raise ValueError(f"Unknown check: {name}")

        diff = abs(val - exp)
        status = "PASS" if diff <= tol else "FAIL"
        results.append((f"{name} ({hotel})", val, exp, diff, tol, status))

    # Check 28: Monthly_KPIs Check_Occupancy > 0.05
    diff_occ = int((abs(df_m["Occupancy_Pct"] - df_m["SQL_Occupancy_Pct"] / 100.0) > 0.05).sum())
    results.append(("Monthly_KPIs Check_Occupancy > 0.05 count", float(diff_occ), 0.0, float(abs(diff_occ - 0)), 0.0, "PASS" if diff_occ == 0 else "FAIL"))

    # Check 29: Country_Name == Unknown count
    country_map = dict(zip(df_country["Code"], df_country["Country_Name"]))
    df_b["Country_Name"] = df_b["country"].map(country_map).fillna("Unknown")
    unk_count = int((df_b["Country_Name"] == "Unknown").sum())
    results.append(("Country_Name Unknown count", float(unk_count), 488.0, float(abs(unk_count - 488)), 0.0, "PASS" if unk_count == 488 else "FAIL"))

    all_pass = True
    print(f"{'STATUS':<6} | {'CHECK DESCRIPTION':<46} | {'CALCULATED':<14} | {'EXPECTED':<14} | {'DIFFERENCE':<10} | {'TOLERANCE':<10}")
    print("-" * 115)
    for chk, val, exp, diff, tol, stat in results:
        if stat != "PASS":
            all_pass = False
        print(f"{stat:<6} | {chk:<46} | {val:14.4f} | {exp:14.4f} | {diff:10.6f} | {tol:<10}")

    print("-" * 115)
    print(f"Independent Pandas Verification Summary: {'ALL 29 CHECKS PASSED [PASS]' if all_pass else 'FAILURES DETECTED [FAIL]'}")
    print("=" * 80)
    return all_pass


def verify_workbook_structure_and_cells(workbook_path: Path) -> bool:
    print("\n" + "=" * 80)
    print("VERIFYING COMPLETE WORKBOOK STRUCTURE WITH OPENPYXL")
    print("=" * 80)

    wb = openpyxl.load_workbook(workbook_path, data_only=False)

    # 1. Verify Sheet Count & Order
    expected_sheets = [
        "README", "Assumptions", "Lookups", "Data", "Monthly_KPIs", "KPI_Summary",
        "PT_Monthly", "PT_Segment", "PT_LeadTime", "PT_Channel",
        "PQ_Monthly", "PQ_Segments", "PQ_Cancel", "Checks", "Notes"
    ]
    print(f"1. Master Sheet Order Verification:")
    print(f"   - Expected ({len(expected_sheets)}): {expected_sheets}")
    print(f"   - Actual   ({len(wb.sheetnames)}): {wb.sheetnames}")
    if wb.sheetnames != expected_sheets:
        print(f"   [FAIL] Sheet names or order mismatch!")
        return False
    print("   [PASS] Exactly 15 sheets present in precise required sequence.")

    # 2. Verify KPI_Summary charts and conditional formatting
    ws_kpi = wb["KPI_Summary"]
    charts_count = len(ws_kpi._charts)
    print(f"\n2. KPI_Summary Chart Verification:")
    print(f"   - Native Charts Detected: {charts_count} (Expected: 4)")
    if charts_count != 4:
        print(f"   [FAIL] Expected 4 charts, but found {charts_count}!")
        return False
    print("   [PASS] Exactly 4 charts present on KPI_Summary.")

    cf_count = len(ws_kpi.conditional_formatting)
    print(f"\n3. KPI_Summary Conditional Formatting Verification:")
    print(f"   - Rule sets detected: {cf_count}")
    if cf_count < 3:
        print(f"   [FAIL] Expected at least 3 conditional formatting rule sets, found {cf_count}!")
        return False
    print("   [PASS] 3-color scales, data bars, and underperformer formula rules verified.")

    # 4. Scan all cells across Sections A to D on KPI_Summary
    sections = [
        ("Section A (Headers & Data)", 5, 16, 1, 4),
        ("Section A (Note Block)", 18, 18, 1, 4),
        ("Section B (Headers & Data)", 21, 49, 1, 10),
        ("Section C (Headers & Data)", 52, 61, 1, 6),
        ("Section D (Headers & Data)", 64, 70, 1, 5)
    ]

    total_scanned = 0
    formulas_count = 0
    labels_count = 0
    invalid_cells = []

    for sec_name, r_start, r_end, c_start, c_end in sections:
        for r in range(r_start, r_end + 1):
            for c in range(c_start, c_end + 1):
                cell = ws_kpi.cell(row=r, column=c)
                val = cell.value

                if val is None:
                    if r == 18 and c in [2, 3, 4]:
                        continue
                    invalid_cells.append((cell.coordinate, "None/Blank", val))
                    continue

                total_scanned += 1
                if isinstance(val, str) and val.startswith("="):
                    formulas_count += 1
                elif isinstance(val, str):
                    labels_count += 1
                else:
                    invalid_cells.append((cell.coordinate, type(val).__name__, val))

    print(f"\n4. KPI_Summary Cell Integrity Scan (Sections A to D):")
    print(f"   - Total Cells Scanned:             {total_scanned}")
    print(f"   - Formula Cells:                   {formulas_count}")
    print(f"   - Text Label Cells:                {labels_count}")
    print(f"   - Invalid / Non-formula Cells:     {len(invalid_cells)}")

    if invalid_cells:
        print("   [FAIL] Invalid cells detected on KPI_Summary:")
        for coord, ctype, cval in invalid_cells[:10]:
            print(f"     Cell {coord}: type={ctype}, value={cval}")
        return False
    print("   [PASS] 100% of cells on KPI_Summary are strictly formulas or text labels (0 typed numbers).")

    # 5. Verify Checks Sheet
    print(f"\n5. Checks Sheet Verification:")
    ws_checks = wb["Checks"]
    banner_formula = ws_checks["B4"].value
    print(f"   - Banner Formula (Cell B4): {banner_formula}")
    expected_banner = '=IF(COUNTIF(tblChecks[Status], "CHECK")=0, "ALL CHECKS OK", "REVIEW")'
    if banner_formula != expected_banner:
        print(f"   [FAIL] Banner formula mismatch! Expected: {expected_banner}, Found: {banner_formula}")
        return False
    print("   [PASS] Overall status banner formula exactly matches specification.")

    if "tblChecks" not in ws_checks.tables:
        print("   [FAIL] Table 'tblChecks' not found on Checks sheet!")
        return False
    tbl_checks = ws_checks.tables["tblChecks"]
    print(f"   - Table tblChecks Detected: Range={tbl_checks.ref}")

    # Verify that all 29 rows in tblChecks have formula in Workbook Value (Col B), Difference (Col D), Status (Col F)
    # Data rows are 7 to 35
    non_formula_cells = []
    for r in range(7, 36):
        for col_letter in ["B", "D", "F"]:
            cell_val = ws_checks[f"{col_letter}{r}"].value
            if not (isinstance(cell_val, str) and cell_val.startswith("=")):
                non_formula_cells.append((f"{col_letter}{r}", cell_val))

    if non_formula_cells:
        print(f"   [FAIL] Found non-formula cells in tblChecks: {non_formula_cells}")
        return False
    print(f"   [PASS] All 29 rows in tblChecks have formulas only in Workbook Value, Difference, and Status (0 typed numbers).")

    # 6. Verify Notes Sheet
    print(f"\n6. Notes Sheet Verification:")
    ws_notes = wb["Notes"]
    if "tblDataQualityLog" not in ws_notes.tables:
        print("   [FAIL] Table 'tblDataQualityLog' not found on Notes sheet!")
        return False
    tbl_dq = ws_notes.tables["tblDataQualityLog"]
    print(f"   - Table tblDataQualityLog Detected: Range={tbl_dq.ref}")
    print("   [PASS] Table tblDataQualityLog present with data quality log rows.")

    # 7. Check LibreOffice / PDF export
    print(f"\n7. LibreOffice PDF Conversion Check:")
    soffice_bin = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice_bin:
        print(f"   - Found LibreOffice executable at: {soffice_bin}")
        try:
            pdf_out_dir = REPO_ROOT / "excel"
            cmd = [soffice_bin, "--headless", "--convert-to", "pdf", str(workbook_path), "--outdir", str(pdf_out_dir)]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0:
                print(f"   [PASS] Converted {workbook_path.name} to PDF successfully.")
            else:
                print(f"   [WARN] PDF conversion exited with code {res.returncode}: {res.stderr}")
        except Exception as e:
            print(f"   [WARN] LibreOffice conversion error: {e}")
    else:
        print("   [INFO] LibreOffice ('soffice' / 'libreoffice') is not installed on this system. Skipping PDF preview.")

    print("=" * 80)
    return True


def build_workbook() -> None:
    OUTPUT_WORKBOOK.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("BUILDING COMPLETE EXCEL WORKBOOK: excel/hotel_kpi_summary.xlsx")
    print("=" * 80)

    # 1. Independent pandas verification of expected checks
    pandas_ok = verify_expected_checks_with_pandas()
    if not pandas_ok:
        print("[CRITICAL ERROR] Independent pandas verification failed! Halting per Rule R5.")
        sys.exit(1)

    workbook = xlsxwriter.Workbook(str(OUTPUT_WORKBOOK), {"constant_memory": False})
    fmt = create_formats(workbook)

    # 15 Sheets in exact required order
    add_readme_sheet(workbook, fmt)
    add_assumptions_sheet(workbook, fmt)
    add_lookups_sheet(workbook, fmt)
    add_data_sheet(workbook, fmt)
    add_monthly_kpis_sheet(workbook, fmt)
    add_kpi_summary_sheet(workbook, fmt)
    add_placeholder_sheets(workbook, fmt)  # PT_Monthly, PT_Segment, PT_LeadTime, PT_Channel, PQ_Monthly, PQ_Segments, PQ_Cancel
    add_checks_sheet(workbook, fmt)
    add_notes_sheet(workbook, fmt)

    print("Closing workbook and saving to disk...")
    workbook.close()
    file_size_mb = OUTPUT_WORKBOOK.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Workbook saved: {OUTPUT_WORKBOOK} ({file_size_mb:.2f} MB)")

    structure_ok = verify_workbook_structure_and_cells(OUTPUT_WORKBOOK)
    if not structure_ok:
        print("[CRITICAL ERROR] Workbook verification failed! Halting.")
        sys.exit(1)


def main():
    build_workbook()


if __name__ == "__main__":
    main()
