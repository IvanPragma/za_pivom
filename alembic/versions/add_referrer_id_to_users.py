"""add referrer_id to users

Revision ID: add_referrer_id_to_users
Revises: f86b60ccf28c
Create Date: 2025-01-27 12:00:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_referrer_id_to_users'
down_revision = 'f86b60ccf28c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле referrer_id в таблицу users
    op.add_column('users', sa.Column('referrer_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_referrer_id', 'users', 'users', ['referrer_id'], ['id'])


def downgrade() -> None:
    # Удаляем поле referrer_id из таблицы users
    op.drop_constraint('fk_users_referrer_id', 'users', type_='foreignkey')
    op.drop_column('users', 'referrer_id')
