"""create users table

Revision ID: eac8d99d29e5
Revises: 
Create Date: 2026-01-30 01:28:36.389512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eac8d99d29e5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, comment='用户唯一标识ID'),
        sa.Column('username', sa.String(length=50), nullable=False, comment='用户名，唯一且不能为空'),
        sa.Column('email', sa.String(length=100), nullable=False, comment='用户邮箱地址，唯一且不能为空'),
        sa.Column('password', sa.String(length=255), nullable=False, comment='用户密码（bcrypt哈希加密后存储）'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
