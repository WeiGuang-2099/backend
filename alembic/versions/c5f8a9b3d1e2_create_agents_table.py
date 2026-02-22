"""create agents table

Revision ID: c5f8a9b3d1e2
Revises: eac8d99d29e5
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c5f8a9b3d1e2'
down_revision = '810de4eea248'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, comment="数字人唯一标识ID"),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True, comment="所属用户ID"),
        sa.Column('name', sa.String(100), nullable=False, comment="数字人名称"),
        sa.Column('description', sa.Text(), nullable=True, comment="数字人描述"),
        sa.Column('avatar_url', sa.String(500), nullable=True, comment="头像URL"),
        sa.Column('voice_id', sa.String(100), nullable=True, comment="语音ID"),
        sa.Column('voice_settings', sa.Text(), nullable=True, comment="语音设置"),
        sa.Column('appearance_settings', sa.Text(), nullable=True, comment="外观设置"),
        sa.Column('is_active', sa.Boolean(), default=True, comment="是否激活"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), comment="创建时间"),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), comment="更新时间"),
    )


def downgrade() -> None:
    op.drop_table('agents')
