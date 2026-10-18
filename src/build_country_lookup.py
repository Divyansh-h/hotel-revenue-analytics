"""
Build Country Lookup Table
Reads distinct country codes from PostgreSQL table hotel.bookings,
maps ISO 3166-1 alpha-3 codes using pycountry, handles known exceptions
('CN' -> China, 'TMP' -> Timor-Leste, 'Unknown' -> Unknown), and writes:
- excel/inputs/country_lookup.csv (columns: Code, Country_Name)
- excel/inputs/country_unmapped.csv (if any unmapped codes exist)

Validates that mapped codes cover at least 99.9% of all bookings.
Prints the 10 most frequent countries with names and shares.
"""

import sys
from pathlib import Path
import pandas as pd
import pycountry

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.db import get_engine

OUTPUT_DIR = REPO_ROOT / "excel" / "inputs"
MIN_MAPPED_SHARE_PCT = 99.9

KNOWN_EXCEPTIONS = {
    "CN": "China",
    "TMP": "Timor-Leste",
    "Unknown": "Unknown"
}


def build_country_lookup() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = get_engine()

    query = """
    SELECT
        country AS code,
        COUNT(*)::integer AS bookings
    FROM hotel.bookings
    GROUP BY country
    ORDER BY bookings DESC, country ASC;
    """
    df = pd.read_sql_query(query, engine)
    total_distinct_codes = len(df)
    total_bookings = df["bookings"].sum()

    mapped_rows = []
    unmapped_rows = []

    for _, row in df.iterrows():
        code = row["code"]
        bookings = row["bookings"]

        if code in KNOWN_EXCEPTIONS:
            country_name = KNOWN_EXCEPTIONS[code]
            mapped_rows.append({"Code": code, "Country_Name": country_name, "Bookings": bookings})
        else:
            match = pycountry.countries.get(alpha_3=code)
            if match:
                mapped_rows.append({"Code": code, "Country_Name": match.name, "Bookings": bookings})
            else:
                unmapped_name = f"Unmapped ({code})"
                unmapped_rows.append({"Code": code, "Bookings": bookings})
                mapped_rows.append({"Code": code, "Country_Name": unmapped_name, "Bookings": bookings})

    mapped_count = len([r for r in mapped_rows if not r["Country_Name"].startswith("Unmapped (")])
    unmapped_count = len(unmapped_rows)

    mapped_bookings = sum(r["Bookings"] for r in mapped_rows if not r["Country_Name"].startswith("Unmapped ("))
    mapped_share_pct = (mapped_bookings / total_bookings) * 100.0

    # Sort final lookup table alphabetically by Code
    lookup_df = pd.DataFrame(mapped_rows)[["Code", "Country_Name"]]
    lookup_df = lookup_df.sort_values("Code", ascending=True).reset_index(drop=True)

    lookup_file = OUTPUT_DIR / "country_lookup.csv"
    lookup_df.to_csv(lookup_file, index=False, encoding="utf-8")

    # Handle unmapped file
    unmapped_file = OUTPUT_DIR / "country_unmapped.csv"
    if unmapped_rows:
        unmapped_df = pd.DataFrame(unmapped_rows)[["Code", "Bookings"]]
        unmapped_df.to_csv(unmapped_file, index=False, encoding="utf-8")
    else:
        # Write empty template with headers if 0 unmapped
        pd.DataFrame(columns=["Code", "Bookings"]).to_csv(unmapped_file, index=False, encoding="utf-8")

    # Output report
    print("=" * 80)
    print("COUNTRY LOOKUP TABLE GENERATION REPORT")
    print("=" * 80)
    print(f"Total distinct country codes in database: {total_distinct_codes}")
    print(f"Successfully mapped codes:               {mapped_count}")
    print(f"Unmapped codes count:                    {unmapped_count}")
    print(f"Total bookings evaluated:                {total_bookings:,}")
    print(f"Bookings covered by mapped codes:        {mapped_bookings:,} ({mapped_share_pct:.4f}%)")
    print(f"Minimum required coverage:               {MIN_MAPPED_SHARE_PCT}%")
    print("-" * 80)

    if unmapped_rows:
        print("\nUNMAPPED CODES DETECTED:")
        for r in unmapped_rows:
            print(f"  - Code: {r['Code']}, Bookings: {r['Bookings']}")
    else:
        print("\nAll country codes were successfully mapped. Zero unmapped codes.")

    print("\nTOP 10 MOST FREQUENT COUNTRIES BY BOOKING VOLUME:")
    print("-" * 80)
    print(f"{'Rank':<5} | {'Code':<6} | {'Country Name':<28} | {'Bookings':<10} | {'Share %'}")
    print("-" * 80)
    top_10 = sorted(mapped_rows, key=lambda x: x["Bookings"], reverse=True)[:10]
    for idx, r in enumerate(top_10, 1):
        share = (r["Bookings"] / total_bookings) * 100.0
        print(f"{idx:<5} | {r['Code']:<6} | {r['Country_Name']:<28} | {r['Bookings']:<10,} | {share:>6.2f}%")
    print("-" * 80)

    # Validation check
    if mapped_share_pct < MIN_MAPPED_SHARE_PCT:
        print(f"\n[CRITICAL ERROR] Mapped coverage ({mapped_share_pct:.2f}%) is below {MIN_MAPPED_SHARE_PCT}%! STOPPING.")
        sys.exit(1)

    print(f"\n[SUCCESS] Wrote {len(lookup_df)} rows to {lookup_file}")
    print(f"[SUCCESS] Wrote unmapped registry to {unmapped_file}")
    print("=" * 80)


def main():
    build_country_lookup()


if __name__ == "__main__":
    main()
