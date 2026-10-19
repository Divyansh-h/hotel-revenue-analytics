"""
Phase 4: Generate Power Query M scripts for Power BI Star Schema ingestion.
Reads the REAL CSV headers from powerbi/data/*.csv to prevent column drift.

Generates:
- powerbi/power_query/dim_date.m
- powerbi/power_query/dim_hotel.m
- powerbi/power_query/dim_profile.m
- powerbi/power_query/fact_bookings.m
- powerbi/power_query/fact_stay_nights.m
- powerbi/power_query/fact_capacity.m
- powerbi/power_query/parameters.m (DataFolder text parameter)
"""

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "powerbi" / "data"
PQ_DIR = REPO_ROOT / "powerbi" / "power_query"


def get_csv_headers(filename: str) -> list[str]:
    """Read the real header row from a CSV in powerbi/data/."""
    csv_path = DATA_DIR / filename
    if not csv_path.exists():
        raise FileNotFoundError(f"Required CSV not found: {csv_path}")
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
    return [h.strip() for h in headers if h.strip()]


# Authoritative type maps adhering to prompt specifications:
# - keys, counts and flags as Int64.Type
# - dates as type date
# - adr and room_revenue as type number
# - text columns as type text
TYPE_MAPS = {
    "dim_date.csv": {
        "date_key": "type date",
        "year": "Int64.Type",
        "quarter": "Int64.Type",
        "month_num": "Int64.Type",
        "month_short": "type text",
        "month_name": "type text",
        "month_start": "type date",
        "year_month": "type text",
    },
    "dim_hotel.csv": {
        "hotel_key": "Int64.Type",
        "hotel": "type text",
        "rooms_capacity": "Int64.Type",
    },
    "dim_profile.csv": {
        "profile_key": "Int64.Type",
        "market_segment": "type text",
        "distribution_channel": "type text",
        "customer_type": "type text",
        "deposit_type": "type text",
    },
    "fact_bookings.csv": {
        "booking_id": "Int64.Type",
        "hotel_key": "Int64.Type",
        "profile_key": "Int64.Type",
        "arrival_date": "type date",
        "is_canceled": "Int64.Type",
        "is_no_show": "Int64.Type",
        "reservation_status": "type text",
        "lead_time": "Int64.Type",
        "lead_bucket": "type text",
        "lead_bucket_order": "Int64.Type",
        "total_nights": "Int64.Type",
        "total_guests": "Int64.Type",
        "country": "type text",
        "adr": "type number",
        "room_revenue": "type number",
        "is_repeated_guest": "Int64.Type",
        "previous_cancellations": "Int64.Type",
        "booking_changes": "Int64.Type",
        "special_requests": "Int64.Type",
        "room_type_mismatch": "Int64.Type",
        "days_cancelled_before_arrival": "Int64.Type",
        "cancel_timing_bucket": "type text",
        "cancel_timing_order": "Int64.Type",
        "is_duplicate_row": "Int64.Type",
    },
    "fact_stay_nights.csv": {
        "booking_id": "Int64.Type",
        "hotel_key": "Int64.Type",
        "profile_key": "Int64.Type",
        "stay_date": "type date",
        "adr": "type number",
    },
    "fact_capacity.csv": {
        "hotel_key": "Int64.Type",
        "date_key": "type date",
        "rooms_available": "Int64.Type",
    },
}


def build_transform_step(headers: list[str], type_map: dict[str, str], step_input: str) -> str:
    """Build Table.TransformColumnTypes step covering every header."""
    for h in headers:
        if h not in type_map:
            raise ValueError(f"Header '{h}' missing from type map!")

    transform_lines = [f'        {{"{h}", {type_map[h]}}}' for h in headers]
    transforms_str = ",\n".join(transform_lines)
    return (
        f'    #"Changed Type" = Table.TransformColumnTypes({step_input}, {{\n'
        f'{transforms_str}\n'
        f'    }}, "en-US")'
    )


def generate_table_m_script(csv_filename: str) -> str:
    """Generate exact M script reading from DataFolder & filename with explicit types."""
    headers = get_csv_headers(csv_filename)
    type_map = TYPE_MAPS[csv_filename]

    # Verify no header mismatch
    missing_headers = set(headers) - set(type_map.keys())
    extra_headers = set(type_map.keys()) - set(headers)
    if missing_headers or extra_headers:
        raise ValueError(
            f"Schema mismatch for {csv_filename}: missing={missing_headers}, extra={extra_headers}"
        )

    transform_step = build_transform_step(headers, type_map, '#"Promoted Headers"')

    script_template = (
        'let\n'
        f'    Source = Csv.Document(File.Contents(DataFolder & "{csv_filename}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n'
        '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n'
        f'{transform_step}\n'
        'in\n'
        '    #"Changed Type"\n'
    )
    return script_template


def generate_parameters_m() -> str:
    """Generate parameters.m defining DataFolder parameter with trailing slash."""
    sample_path = str(DATA_DIR) + "/"
    return f'"{sample_path}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n'


def main() -> None:
    PQ_DIR.mkdir(parents=True, exist_ok=True)

    scripts = {
        "dim_date.m": generate_table_m_script("dim_date.csv"),
        "dim_hotel.m": generate_table_m_script("dim_hotel.csv"),
        "dim_profile.m": generate_table_m_script("dim_profile.csv"),
        "fact_bookings.m": generate_table_m_script("fact_bookings.csv"),
        "fact_stay_nights.m": generate_table_m_script("fact_stay_nights.csv"),
        "fact_capacity.m": generate_table_m_script("fact_capacity.csv"),
        "parameters.m": generate_parameters_m(),
    }

    print("=" * 80)
    print("POWER BI M SCRIPT GENERATOR: powerbi/power_query/*.m")
    print("=" * 80)

    for filename, code in scripts.items():
        out_path = PQ_DIR / filename
        out_path.write_text(code, encoding="utf-8")
        print(f"[OK] Wrote {filename:<22} ({len(code):>5} bytes) -> {out_path}")

    print("=" * 80)
    print(f"Successfully generated {len(scripts)} M scripts in {PQ_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
