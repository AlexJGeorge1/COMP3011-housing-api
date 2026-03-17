"""add_composite_indexes_for_analytics

Revision ID: a1b2c3d4e5f6
Revises: 892adf40f05b
Create Date: 2026-03-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '892adf40f05b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_listings_region_price', 'listings', ['region', 'price'])
    op.create_index('ix_listings_region_date', 'listings', ['region', 'transaction_date'])


def downgrade() -> None:
    op.drop_index('ix_listings_region_date', table_name='listings')
    op.drop_index('ix_listings_region_price', table_name='listings')
