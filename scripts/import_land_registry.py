import argparse
import csv
import io
import sys
import os
from datetime import datetime
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.models.listing import Listing
import uuid

YEARLY_URL = "https://price-paid-data.publicdata.landregistry.gov.uk/pp-{year}.csv"

# Map Land Registry property type codes to str
PROPERTY_TYPE_MAP = {
    "D": "detached",
    "S": "semi",
    "T": "terraced",
    "F": "flat",
    "O": "other",
}
COUNTY_TO_REGION = {
    "TYNE AND WEAR": "North East",
    "NORTHUMBERLAND": "North East",
    "COUNTY DURHAM": "North East",
    "DURHAM": "North East",
    "CLEVELAND": "North East",
    "GREATER MANCHESTER": "North West",
    "MERSEYSIDE": "North West",
    "LANCASHIRE": "North West",
    "CHESHIRE": "North West",
    "CUMBRIA": "North West",
    "WEST YORKSHIRE": "Yorkshire and The Humber",
    "SOUTH YORKSHIRE": "Yorkshire and The Humber",
    "NORTH YORKSHIRE": "Yorkshire and The Humber",
    "EAST YORKSHIRE": "Yorkshire and The Humber",
    "EAST RIDING OF YORKSHIRE": "Yorkshire and The Humber",
    "CITY OF KINGSTON UPON HULL": "Yorkshire and The Humber",
    "DERBYSHIRE": "East Midlands",
    "LEICESTERSHIRE": "East Midlands",
    "LINCOLNSHIRE": "East Midlands",
    "NORTHAMPTONSHIRE": "East Midlands",
    "NOTTINGHAMSHIRE": "East Midlands",
    "RUTLAND": "East Midlands",
    "WEST MIDLANDS": "West Midlands",
    "HEREFORDSHIRE": "West Midlands",
    "SHROPSHIRE": "West Midlands",
    "STAFFORDSHIRE": "West Midlands",
    "WARWICKSHIRE": "West Midlands",
    "WORCESTERSHIRE": "West Midlands", "BEDFORDSHIRE": "East of England",
    "CAMBRIDGESHIRE": "East of England",
    "ESSEX": "East of England",
    "HERTFORDSHIRE": "East of England",
    "NORFOLK": "East of England",
    "SUFFOLK": "East of England",
    "GREATER LONDON": "London",
    "BERKSHIRE": "South East",
    "BUCKINGHAMSHIRE": "South East",
    "EAST SUSSEX": "South East",
    "HAMPSHIRE": "South East",
    "ISLE OF WIGHT": "South East",
    "KENT": "South East",
    "OXFORDSHIRE": "South East",
    "SURREY": "South East",
    "WEST SUSSEX": "South East",
    "AVON": "South West",
    "BRISTOL": "South West",
    "CORNWALL": "South West",
    "DEVON": "South West",
    "DORSET": "South West",
    "GLOUCESTERSHIRE": "South West",
    "SOMERSET": "South West",
    "WILTSHIRE": "South West",
    "DYFED": "Wales",
    "GWENT": "Wales",
    "GWYNEDD": "Wales",
    "MID GLAMORGAN": "Wales",
    "POWYS": "Wales",
    "SOUTH GLAMORGAN": "Wales",
    "WEST GLAMORGAN": "Wales",
    "ISLE OF ANGLESEY": "Wales",
    "FLINTSHIRE": "Wales",
    "WREXHAM": "Wales",
    "CONWY": "Wales",
    "DENBIGHSHIRE": "Wales",
    "SWANSEA": "Wales",
    "CARDIFF": "Wales",
    "NEWPORT": "Wales",
    "PEMBROKESHIRE": "Wales",
    "MONMOUTHSHIRE": "Wales",
    "CEREDIGION": "Wales",
    "BRIDGEND": "Wales",
    "RHONDDA CYNON TAFF": "Wales",
    "NEATH PORT TALBOT": "Wales",
    "CAERPHILLY": "Wales",
    "MERTHYR TYDFIL": "Wales",
    "TORFAEN": "Wales",
    "ISLE OF WIGHT": "South East",
    "WINDSOR AND MAIDENHEAD": "South East",
    "WOKINGHAM": "South East",
    "BRACKNELL FOREST": "South East",
    "SLOUGH": "South East",
    "READING": "South East",
    "WEST BERKSHIRE": "South East",
    "MILTON KEYNES": "South East",
    "BRIGHTON AND HOVE": "South East",
    "SOUTHAMPTON": "South East",
    "PORTSMOUTH": "South East",
    "MEDWAY": "South East",
    "BOURNEMOUTH": "South West",
    "POOLE": "South West",
    "BOURNEMOUTH, CHRISTCHURCH AND POOLE": "South West",
    "SWINDON": "South West",
    "BATH AND NORTH EAST SOMERSET": "South West",
    "NORTH SOMERSET": "South West",
    "SOUTH GLOUCESTERSHIRE": "South West",
    "PLYMOUTH": "South West",
    "TORBAY": "South West",
    "THURROCK": "East of England",
    "SOUTHEND-ON-SEA": "East of England",
    "CENTRAL BEDFORDSHIRE": "East of England",
    "BEDFORD": "East of England",
    "PETERBOROUGH": "East of England",
    "LUTON": "East of England",
    "HEREFORDSHIRE": "West Midlands",
    "TELFORD AND WREKIN": "West Midlands",
    "STOKE-ON-TRENT": "West Midlands",
    "NOTTINGHAM": "East Midlands",
    "DERBY": "East Midlands",
    "LEICESTER": "East Midlands",
    "CHESHIRE EAST": "North West",
    "CHESHIRE WEST AND CHESTER": "North West",
    "HALTON": "North West",
    "BLACKBURN WITH DARWEN": "North West",
    "BLACKPOOL": "North West",
    "WARRINGTON": "North West",
    "YORK": "Yorkshire and The Humber",
    "NORTH EAST LINCOLNSHIRE": "Yorkshire and The Humber",
    "NORTH LINCOLNSHIRE": "Yorkshire and The Humber",
    "DARLINGTON": "North East",
    "HARTLEPOOL": "North East",
    "MIDDLESBROUGH": "North East",
    "REDCAR AND CLEVELAND": "North East",
    "STOCKTON-ON-TEES": "North East",
}

TARGET_YEARS = list(range(2015, 2025)) 
BATCH_SIZE = 1000  

_other_count = 0


def map_region(county: str, track_others: bool = True) -> str:
    """Map a Land Registry county name to an ONS region name."""
    global _other_count
    region = COUNTY_TO_REGION.get(county.upper().strip(), "Other")
    if region == "Other" and track_others:
        _other_count += 1
    return region


def parse_row(row: list) -> dict | None:
    """
    Parse a single Land Registry CSV row.
    Returns a dict of field values, or None if the row should be skipped.
    """
    if len(row) < 16:
        return None

    try:
        price = int(row[1])
        # Skip 0-price transactions
        if price <= 0:
            return None

        transaction_date = datetime.strptime(row[2].split(" ")[0], "%Y-%m-%d").date()

        #build address
        address_parts = [p.strip() for p in [row[7], row[8], row[9], row[10], row[11]] if p.strip()]
        address = ", ".join(address_parts) if address_parts else "Unknown"

        county = row[13]
        region = map_region(county)

        property_type = PROPERTY_TYPE_MAP.get(row[4], None)

        return {
            "id": str(uuid.uuid4()),
            "address": address,
            "region": region,
            "price": price,
            "bedrooms": None,  # Land Registry does not include bedroom count
            "property_type": property_type,
            "transaction_date": transaction_date,
        }
    except (ValueError, IndexError):
        return None


def import_year(year: int, db, dry_run: bool = False) -> int:
    """Download and import a single year of Land Registry data. Returns count of rows imported."""
    url = YEARLY_URL.format(year=year)
    print(f"  Downloading {year} data from {url} ...")

    try:
        print(f"    (downloading full file, this may take a moment...)")
        response = requests.get(url, timeout=300)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  ERROR: Failed to download {year} data: {e}")
        return 0

    print(f"    Download complete ({len(response.content) / 1024 / 1024:.1f} MB). Parsing...")

    batch = []
    total = 0
    skipped = 0

    reader = csv.reader(io.StringIO(response.text))

    for row in reader:
        parsed = parse_row(row)
        if not parsed:
            skipped += 1
            continue

        if not dry_run:
            batch.append(Listing(**parsed))

        total += 1

        if not dry_run and len(batch) >= BATCH_SIZE:
            db.bulk_save_objects(batch)
            db.commit()
            batch = []
            print(f"    ... {total:,} rows imported", end="\r", flush=True)

    if not dry_run and batch:
        db.bulk_save_objects(batch)
        db.commit()

    global _other_count
    print(f"  Year {year}: {total:,} rows imported, {skipped:,} skipped. ({_other_count:,} fell into 'Other' region)")
    # Reset for next call if run in loop
    _other_count = 0
    return total


def run(years: list[int], dry_run: bool = False):
    db = SessionLocal()
    grand_total = 0
    try:
        for year in years:
            print(f"\n[{year}]")
            count = import_year(year, db, dry_run=dry_run)
            grand_total += count
    finally:
        db.close()

    print(f"\nDone. Total rows imported: {grand_total:,}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Land Registry Price Paid data (2015-2024)")
    parser.add_argument("--year", type=int, help="Import a single year (default: all 2015-2024)")
    parser.add_argument("--dry-run", action="store_true", help="Parse rows without writing to DB")
    args = parser.parse_args()

    years = [args.year] if args.year else TARGET_YEARS
    print(f"Land Registry Importer — years: {years}, dry_run: {args.dry_run}")
    run(years, dry_run=args.dry_run)
