"""create listings and regions tables

Revision ID: 892adf40f05b
Revises: 230997bcb4e0
Create Date: 2026-03-14 20:41:25.718373

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import logging

logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision: str = '892adf40f05b'
down_revision: Union[str, None] = '230997bcb4e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _pgvector_available() -> bool:
    """Check whether the connected PostgreSQL instance supports pgvector."""
    try:
        op.execute('CREATE EXTENSION IF NOT EXISTS vector;')
        return True
    except Exception:
        logger.warning(
            "pgvector extension not available — the embedding column will be "
            "skipped and semantic search will be disabled."
        )
        return False


def upgrade() -> None:
    has_pgvector = _pgvector_available()

    columns = [
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('region', sa.String(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('bedrooms', sa.Integer(), nullable=True),
        sa.Column('property_type', sa.String(), nullable=True),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    ]

    if has_pgvector:
        import pgvector.sqlalchemy
        columns.append(
            sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=384), nullable=True),
        )

    op.create_table('listings', *columns, sa.PrimaryKeyConstraint('id'))
    op.create_index(op.f('ix_listings_address'), 'listings', ['address'], unique=False)
    op.create_index(op.f('ix_listings_id'), 'listings', ['id'], unique=False)
    op.create_index(op.f('ix_listings_region'), 'listings', ['region'], unique=False)
    op.create_table('regions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('ons_code', sa.String(), nullable=False),
    sa.Column('median_salary', sa.Float(), nullable=True),
    sa.Column('median_rent', sa.Float(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_regions_id'), 'regions', ['id'], unique=False)
    op.create_index(op.f('ix_regions_name'), 'regions', ['name'], unique=True)
    op.create_index(op.f('ix_regions_ons_code'), 'regions', ['ons_code'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_index(op.f('ix_regions_ons_code'), table_name='regions')
    op.drop_index(op.f('ix_regions_name'), table_name='regions')
    op.drop_index(op.f('ix_regions_id'), table_name='regions')
    op.drop_table('regions')
    op.drop_index(op.f('ix_listings_region'), table_name='listings')
    op.drop_index(op.f('ix_listings_id'), table_name='listings')
    op.drop_index(op.f('ix_listings_address'), table_name='listings')
    op.drop_table('listings')
    try:
        op.execute('DROP EXTENSION IF EXISTS vector;')
    except Exception:
        pass
