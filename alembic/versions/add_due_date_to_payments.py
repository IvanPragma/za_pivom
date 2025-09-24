"""add_due_date_to_payments

Revision ID: add_due_date_to_payments
Revises: add_referral_code_and_earned
Create Date: 2025-01-27 12:30:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_due_date_to_payments'
down_revision = 'add_referral_code_and_earned'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле due_date в таблицу payments
    op.add_column('payments', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Удаляем поле due_date
    op.drop_column('payments', 'due_date')
