"""add new fields to agents

Revision ID: f8e9a0b1c2d3
Revises: d3a7b8c4e5f6
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f8e9a0b1c2d3'
down_revision = 'd3a7b8c4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('agents', sa.Column('short_description', sa.String(200), nullable=True, comment="简短描述"))
    op.add_column('agents', sa.Column('conversation_style', sa.String(50), nullable=True, comment="对话风格"))
    op.add_column('agents', sa.Column('personality', sa.String(100), nullable=True, comment="个性特征"))
    op.add_column('agents', sa.Column('temperature', sa.Float(), default=0.7, comment="AI温度参数"))
    op.add_column('agents', sa.Column('max_tokens', sa.Integer(), default=2048, comment="最大token数"))
    op.add_column('agents', sa.Column('system_prompt', sa.Text(), nullable=True, comment="系统提示词"))


def downgrade() -> None:
    op.drop_column('agents', 'system_prompt')
    op.drop_column('agents', 'max_tokens')
    op.drop_column('agents', 'temperature')
    op.drop_column('agents', 'personality')
    op.drop_column('agents', 'conversation_style')
    op.drop_column('agents', 'short_description')
