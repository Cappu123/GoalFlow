"""add the messages table

Revision ID: 10d367dddbe8
Revises: 47384bffbc0a
Create Date: 2026-01-28 10:33:56.188096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10d367dddbe8'
down_revision: Union[str, Sequence[str], None] = '47384bffbc0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "messages",
        sa.Column("id", sa.String(), nullable=False, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("chat_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), 
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"], ondelete="CASCADE"
    )
    )
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('messages')   
