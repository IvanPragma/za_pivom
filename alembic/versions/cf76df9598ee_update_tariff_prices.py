"""update tariff prices

Revision ID: cf76df9598ee
Revises: 6b2afca66c99
Create Date: 2025-09-22 21:32:22.465095+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf76df9598ee'
down_revision = '6b2afca66c99'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Обновляем цены тарифов
    op.execute("""
        UPDATE payment_plans 
        SET price_total = 4200 
        WHERE name = 'Моментальный тариф'
    """)
    
    op.execute("""
        UPDATE payment_plans 
        SET price_total = 4900 
        WHERE name = '2 месяца'
    """)
    
    op.execute("""
        UPDATE payment_plans 
        SET price_total = 5100 
        WHERE name = '3 месяца'
    """)
    
    op.execute("""
        UPDATE payment_plans 
        SET price_total = 5280 
        WHERE name = '6 месяцев'
    """)


def downgrade() -> None:
    # Откатываем к старым ценам
    op.execute("""
        UPDATE payment_plans 
        SET price_total = 3799 
        WHERE name = 'Моментальный тариф'
    """)
    
    op.execute("""
        UPDATE payment_plans 
        SET price_total = 3900 
        WHERE name = '2 месяца'
    """)
    
    op.execute("""
        UPDATE payment_plans 
        SET price_total = 4050 
        WHERE name = '3 месяца'
    """)
    
    op.execute("""
        UPDATE payment_plans 
        SET price_total = 4800 
        WHERE name = '6 месяцев'
    """)
