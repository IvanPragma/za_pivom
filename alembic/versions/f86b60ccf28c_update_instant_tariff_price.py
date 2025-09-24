"""update instant tariff price

Revision ID: f86b60ccf28c
Revises: cf76df9598ee
Create Date: 2025-09-22 22:20:07.821434+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f86b60ccf28c'
down_revision = 'cf76df9598ee'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Обновляем цену моментального тарифа
    op.execute("""
        UPDATE payment_plans 
        SET price_total = 4400 
        WHERE name = 'Моментальный тариф'
    """)


def downgrade() -> None:
    # Откатываем к предыдущей цене
    op.execute("""
        UPDATE payment_plans 
        SET price_total = 4200 
        WHERE name = 'Моментальный тариф'
    """)
