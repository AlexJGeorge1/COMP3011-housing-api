"""
ONS Data Importer
==================
Populates the `regions` table with:
  - ONS Annual Survey of Hours and Earnings (ASHE) — median salary by region
  - ONS Private Rental Market Summary (PRMS) — median rent by region

ONS provides these as Excel/CSV downloads. This script uses hard-coded
authoritative 2023 figures (the most recent complete year available).

To update with the latest ONS release, replace the values in the
SALARY_DATA and RENT_DATA dictionaries below and change DATA_YEAR.

Data sources:
  ASHE: https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoceasonallyadjusted
  PRS:  https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/privaterentalmarketsummarystatisticsinengland

Usage:
  python scripts/import_ons_data.py
  python scripts/import_ons_data.py --dry-run
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.models.region import Region
import uuid

DATA_YEAR = 2023

# ONS ASHE Table 8 — median gross annual salary (£) by UK region, 2023
# Source: ONS ASHE 2023, Table 8.7a, full-time employees
SALARY_DATA = {
    "North East":                  29_768,
    "North West":                  31_694,
    "Yorkshire and The Humber":    31_060,
    "East Midlands":               31_298,
    "West Midlands":               31_749,
    "East of England":             34_126,
    "London":                      44_370,
    "South East":                  36_959,
    "South West":                  31_805,
    "Wales":                       30_580,
    "Scotland":                    33_800,
    "Northern Ireland":            29_900,
}

# ONS Private Rental Market Summary — median monthly rent (£) by region, 2023
# Source: ONS PRMS 2023, Table 2.2 — England and regions
RENT_DATA = {
    "North East":                  525,
    "North West":                  699,
    "Yorkshire and The Humber":    650,
    "East Midlands":               725,
    "West Midlands":               750,
    "East of England":             925,
    "London":                     1_950,
    "South East":                 1_100,
    "South West":                   875,
    "Wales":                        625,
    "Scotland":                     800,
    "Northern Ireland":             650,
}

# ONS region codes (ITL1 codes for England, standard for Wales/Scotland/NI)
ONS_CODES = {
    "North East":                  "TLC",
    "North West":                  "TLD",
    "Yorkshire and The Humber":    "TLE",
    "East Midlands":               "TLF",
    "West Midlands":               "TLG",
    "East of England":             "TLH",
    "London":                      "TLI",
    "South East":                  "TLJ",
    "South West":                  "TLK",
    "Wales":                       "TLL",
    "Scotland":                    "TLM",
    "Northern Ireland":            "TLN",
}


def run(dry_run: bool = False):
    db = SessionLocal()
    inserted = 0
    updated = 0

    try:
        for region_name, salary in SALARY_DATA.items():
            rent = RENT_DATA.get(region_name)
            ons_code = ONS_CODES.get(region_name, "UNKNOWN")

            existing = db.query(Region).filter(Region.name == region_name).first()

            if existing:
                if not dry_run:
                    existing.median_salary = salary
                    existing.median_rent = rent
                    existing.year = DATA_YEAR
                    db.commit()
                print(f"  UPDATED  {region_name}: salary=£{salary:,}/yr, rent=£{rent}/mo")
                updated += 1
            else:
                if not dry_run:
                    region = Region(
                        id=str(uuid.uuid4()),
                        name=region_name,
                        ons_code=ons_code,
                        median_salary=float(salary),
                        median_rent=float(rent),
                        year=DATA_YEAR,
                    )
                    db.add(region)
                    db.commit()
                print(f"  INSERTED {region_name}: salary=£{salary:,}/yr, rent=£{rent}/mo")
                inserted += 1

    finally:
        db.close()

    print(f"\nDone. {inserted} inserted, {updated} updated. dry_run={dry_run}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import ONS salary and rent data into regions table")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to DB")
    args = parser.parse_args()

    print(f"ONS Importer — data year: {DATA_YEAR}, dry_run: {args.dry_run}")
    run(dry_run=args.dry_run)
