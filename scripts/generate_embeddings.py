"""
Generate embeddings for property listings and store them in the `embedding` column.

By default embeds a random sample of 50,000 listings so /search works quickly.
Use --limit to change the sample size, or --all to embed everything (slow!).

Usage (inside Docker):
    docker compose exec api python scripts/generate_embeddings.py
    docker compose exec api python scripts/generate_embeddings.py --limit 10000
    docker compose exec api python scripts/generate_embeddings.py --all
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.models.listing import Listing
from app.embeddings import embed_listing

BATCH_SIZE = 256  # embeddings generated per model call
DEFAULT_SAMPLE = 50_000


def run(limit: int | None, skip_existing: bool = True):
    db = SessionLocal()
    try:
        query = db.query(Listing)
        if skip_existing:
            query = query.filter(Listing.embedding == None)  # noqa: E711

        total_eligible = query.count()
        if limit:
            rows = query.order_by(Listing.id).limit(limit).all()
        else:
            rows = query.order_by(Listing.id).all()

        total = len(rows)
        print(f"Eligible rows (no embedding yet): {total_eligible:,}")
        print(f"Will embed: {total:,} rows in batches of {BATCH_SIZE}")

        done = 0
        for i in range(0, total, BATCH_SIZE):
            batch = rows[i: i + BATCH_SIZE]
            for listing in batch:
                listing.embedding = embed_listing(listing)
            db.commit()
            done += len(batch)
            pct = done / total * 100
            print(f"  {done:,}/{total:,} ({pct:.1f}%) embedded...", end="\r", flush=True)

        print(f"\nDone. {done:,} embeddings written.")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate pgvector embeddings for listings")
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_SAMPLE,
        help=f"Number of listings to embed (default: {DEFAULT_SAMPLE:,}). Ignored if --all is set.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Embed ALL listings (very slow for 10M rows — expect several hours).",
    )
    parser.add_argument(
        "--re-embed",
        action="store_true",
        help="Re-generate embeddings even for rows that already have one.",
    )
    args = parser.parse_args()

    limit = None if args.all else args.limit
    skip_existing = not args.re_embed

    if args.all:
        print("WARNING: --all selected. This will embed ~10M rows and may take several hours.")
    else:
        print(f"Generating embeddings for up to {limit:,} listings...")

    run(limit=limit, skip_existing=skip_existing)
