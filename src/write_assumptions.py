"""
Write Analytical Assumptions to config/assumptions.yml
Reads parameters dynamically from PostgreSQL (hotel.window_params and hotel.capacity_derivation).
Never hardcodes or invents any values (Rule R1).
"""

import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.db import get_connection


def write_assumptions() -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Fetch Window Parameters
            cur.execute("""
                SELECT 
                    window_start::text,
                    window_end::text,
                    (window_end - window_start + 1)::integer AS total_days,
                    capacity_buffer::numeric
                FROM hotel.window_params;
            """)
            wp_row = cur.fetchone()
            if not wp_row:
                raise ValueError("hotel.window_params table is empty.")

            window_start, window_end, total_days, capacity_buffer = wp_row

            # 2. Fetch Capacity Derivation per Hotel
            cur.execute("""
                SELECT 
                    hotel,
                    peak_rooms_sold,
                    peak_date::text,
                    capacity,
                    avg_rooms_sold_per_night::numeric
                FROM hotel.capacity_derivation
                ORDER BY hotel;
            """)
            cap_rows = cur.fetchall()
            if not cap_rows:
                raise ValueError("hotel.capacity_derivation table is empty.")

        hotels_data = {}
        for r in cap_rows:
            hotel, peak_rooms, peak_date, capacity, avg_rooms = r
            hotels_data[hotel] = {
                "peak_rooms_sold": int(peak_rooms),
                "peak_date": str(peak_date),
                "capacity": int(capacity),
                "avg_rooms_sold_per_night": float(avg_rooms),
            }

        assumptions = {
            "window": {
                "start": str(window_start),
                "end": str(window_end),
                "days": int(total_days),
            },
            "capacity_buffer": float(capacity_buffer),
            "hotels": hotels_data,
        }

        output_path = REPO_ROOT / "config" / "assumptions.yml"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(assumptions, f, sort_keys=False, default_flow_style=False)

        print(f"Successfully wrote assumptions to {output_path}:")
        with open(output_path, "r", encoding="utf-8") as f:
            print(f.read())

        return assumptions

    finally:
        conn.close()


def main():
    write_assumptions()


if __name__ == "__main__":
    main()
