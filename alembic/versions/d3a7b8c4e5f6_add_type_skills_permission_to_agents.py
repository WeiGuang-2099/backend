"""add type, skills, permission to agents

Revision ID: d3a7b8c4e5f6
Revises: c5f8a9b3d1e2
Create Date: 2024-01-20 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd3a7b8c4e5f6'
down_revision = 'c5f8a9b3d1e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('agents', sa.Column('agent_type', sa.String(50), nullable=True, comment="数字人类型"))
    op.add_column('agents', sa.Column('skills', sa.Text(), nullable=True, comment="技能列表"))
    op.add_column('agents', sa.Column('permission', sa.String(50), default='private', comment="权限设置"))


def downgrade() -> None:
    op.drop_column('agents', 'permission')
    op.drop_column('agents', 'skills')
    op.drop_column('agents', 'agent_type')
