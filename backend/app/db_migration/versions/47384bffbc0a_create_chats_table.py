"""create chats table

Revision ID: 47384bffbc0a
Revises: 
Create Date: 2026-01-27 16:29:58.063922

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47384bffbc0a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'chats',
        sa.Column('id', sa.String(), nullable=False, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        #sa.Column('user_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('chats')
