"""add_referral_code_and_earned

Revision ID: add_referral_code_and_earned
Revises: add_referrer_id_to_users
Create Date: 2025-01-27 12:00:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_referral_code_and_earned'
down_revision = 'add_referrer_id_to_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле referral_code
    op.add_column('users', sa.Column('referral_code', sa.String(length=8), nullable=False, server_default=''))
    
    # Создаем уникальный индекс для referral_code
    op.create_index('ix_users_referral_code', 'users', ['referral_code'], unique=True)


def downgrade() -> None:
    # Удаляем индекс и колонку
    op.drop_index('ix_users_referral_code', table_name='users')
    op.drop_column('users', 'referral_code')
