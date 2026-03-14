"""Create tasks table

Revision ID: 001_create_tasks_table
Revises: 
Create Date: 2026-02-13 10:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = '001_create_tasks_table'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tasks table
    op.create_table(
        'task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_user_id', 'task', ['user_id'])
    op.create_index('idx_user_completed', 'task', ['user_id', 'completed'])
    op.create_index('idx_due_date', 'task', ['due_date'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_due_date', table_name='task')
    op.drop_index('idx_user_completed', table_name='task')
    op.drop_index('idx_user_id', table_name='task')
    
    # Drop tasks table
    op.drop_table('task')