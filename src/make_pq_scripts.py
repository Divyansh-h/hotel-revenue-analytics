"""
Generate Power Query M scripts for Excel staging sheets.
Reads the REAL CSV headers from data/outputs/*.csv to ensure column names can never drift.

Generates:
- excel/power_query/q_monthly_kpis.m
- excel/power_query/q_segments.m
- excel/power_query/q_cancel_drivers.m
- excel/power_query/DataFolder.m (parameter definition snippet)
"""

import sys
from pathlib import Path
import csv

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = REPO_ROOT / "data" / "outputs"
PQ_DIR = REPO_ROOT / "excel" / "power_query"


def get_csv_headers(filename: str) -> list[str]:
    """Read the real header row from a CSV in data/outputs/."""
    csv_path = OUTPUTS_DIR / filename
    if not csv_path.exists():
        raise FileNotFoundError(f"Required CSV not found: {csv_path}")
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
    return [h.strip() for h in headers if h.strip()]


# Explicit type dictionaries for each CSV mart
MONTHLY_TYPES = {
    "hotel": "type text",
    "month_start": "type date",
    "room_nights_sold": "Int64.Type",
    "room_nights_available": "Int64.Type",
    "room_revenue": "type number",
    "occupancy_pct": "type number",
    "adr": "type number",
    "revpar": "type number",
}

SEGMENT_TYPES = {
    "hotel": "type text",
    "market_segment": "type text",
    "bookings": "Int64.Type",
    "cancellations": "Int64.Type",
    "cancel_rate_pct": "type number",
    "room_nights_sold": "Int64.Type",
    "room_revenue": "type number",
    "adr": "type number",
    "room_night_share_pct": "type number",
    "revenue_share_pct": "type number",
    "revenue_rank": "Int64.Type",
    "is_zero_revenue_segment": "Int64.Type",
    "is_underperformer": "Int64.Type",
}

CANCEL_TYPES = {
    "hotel": "type text",
    "dimension": "type text",
    "category": "type text",
    "sort_order": "Int64.Type",
    "bookings": "Int64.Type",
    "cancellations": "Int64.Type",
    "no_shows": "Int64.Type",
    "cancel_rate_pct": "type number",
    "share_of_bookings_pct": "type number",
    "cancel_rate_vs_hotel_avg_pp": "type number",
}


def build_transform_step(headers: list[str], type_map: dict[str, str], step_input: str) -> str:
    """Build Table.TransformColumnTypes step covering every header."""
    for h in headers:
        if h not in type_map:
            raise ValueError(f"Header '{h}' missing from type map!")
    
    transform_lines = [f'        {{"{h}", {type_map[h]}}}' for h in headers]
    transforms_str = ",\n".join(transform_lines)
    return f'    #"Changed Type" = Table.TransformColumnTypes({step_input}, {{\n{transforms_str}\n    }}, "en-US")'


def generate_q_monthly_kpis() -> str:
    headers = get_csv_headers("v_monthly_kpis.csv")
    transform_step = build_transform_step(headers, MONTHLY_TYPES, '#"Promoted Headers"')
    
    template = """let
    Source = Csv.Document(File.Contents(DataFolder & "v_monthly_kpis.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
__TRANSFORM_STEP__,
    #"Inserted Year" = Table.AddColumn(#"Changed Type", "Year", each Date.Year([month_start]), Int64.Type),
    #"Inserted Month Name" = Table.AddColumn(#"Inserted Year", "Month_Name", each Date.MonthName([month_start]), type text),
    #"Added High Occupancy" = Table.AddColumn(#"Inserted Month Name", "High_Occupancy_Flag", each if [occupancy_pct] >= 85 then "High" else "Normal", type text),
    #"Sorted Rows" = Table.Sort(#"Added High Occupancy", {{"hotel", Order.Ascending}, {"month_start", Order.Ascending}})
in
    #"Sorted Rows"
"""
    return template.replace("__TRANSFORM_STEP__", transform_step)


def generate_q_segments() -> str:
    headers = get_csv_headers("v_segment_performance.csv")
    transform_step = build_transform_step(headers, SEGMENT_TYPES, '#"Promoted Headers"')
    
    template = """let
    Source = Csv.Document(File.Contents(DataFolder & "v_segment_performance.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
__TRANSFORM_STEP__,
    #"Filtered Zero Revenue" = Table.SelectRows(#"Changed Type", each ([is_zero_revenue_segment] <> 1)),
    #"Added Performance Label" = Table.AddColumn(#"Filtered Zero Revenue", "Performance_Label", each if [is_underperformer] = 1 then "Underperformer" else "OK", type text),
    #"Removed Other Columns" = Table.SelectColumns(#"Added Performance Label", {"hotel", "market_segment", "bookings", "cancel_rate_pct", "adr", "revenue_share_pct", "revenue_rank", "Performance_Label"}),
    #"Sorted Rows" = Table.Sort(#"Removed Other Columns", {{"hotel", Order.Ascending}, {"revenue_rank", Order.Ascending}})
in
    #"Sorted Rows"
"""
    return template.replace("__TRANSFORM_STEP__", transform_step)


def generate_q_cancel_drivers() -> str:
    headers = get_csv_headers("v_cancellation_drivers.csv")
    transform_step = build_transform_step(headers, CANCEL_TYPES, '#"Promoted Headers"')
    
    template = """let
    Source = Csv.Document(File.Contents(DataFolder & "v_cancellation_drivers.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
__TRANSFORM_STEP__,
    #"Filtered Rows" = Table.SelectRows(#"Changed Type", each ([hotel] = "All") and List.Contains({"lead_bucket", "deposit_type", "customer_type", "market_segment"}, [dimension])),
    #"Added Risk Level" = Table.AddColumn(#"Filtered Rows", "Risk_Level", each if [cancel_rate_vs_hotel_avg_pp] > 10 then "High" else if [cancel_rate_vs_hotel_avg_pp] > 0 then "Medium" else "Low", type text),
    #"Sorted Rows" = Table.Sort(#"Added Risk Level", {{"dimension", Order.Ascending}, {"sort_order", Order.Ascending}, {"cancel_rate_pct", Order.Descending}})
in
    #"Sorted Rows"
"""
    return template.replace("__TRANSFORM_STEP__", transform_step)


def generate_datafolder_param() -> str:
    """Return default parameter snippet."""
    sample_path = str(OUTPUTS_DIR) + "/"
    return f'"{sample_path}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n'


def main() -> None:
    PQ_DIR.mkdir(parents=True, exist_ok=True)
    
    queries = {
        "q_monthly_kpis.m": generate_q_monthly_kpis(),
        "q_segments.m": generate_q_segments(),
        "q_cancel_drivers.m": generate_q_cancel_drivers(),
        "DataFolder.m": generate_datafolder_param(),
    }
    
    print("=" * 70)
    print("GENERATING POWER QUERY M SCRIPTS FROM REAL CSV HEADERS")
    print("=" * 70)
    
    for filename, code in queries.items():
        file_path = PQ_DIR / filename
        file_path.write_text(code, encoding="utf-8")
        print(f"[OK] Wrote {filename:<25} ({len(code)} bytes) -> {file_path}")
        
    print("=" * 70)
    print("Power Query M scripts successfully generated in excel/power_query/")


if __name__ == "__main__":
    main()
