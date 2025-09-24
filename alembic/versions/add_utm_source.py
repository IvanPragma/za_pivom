"""add_utm_source

Revision ID: add_utm_source
Revises: add_due_date_to_payments
Create Date: 2025-01-27 13:00:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_utm_source'
down_revision = 'add_due_date_to_payments'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле utm_source
    op.add_column('users', sa.Column('utm_source', sa.String(length=100), nullable=True))


def downgrade() -> None:
    # Удаляем поле utm_source
    op.drop_column('users', 'utm_source')
