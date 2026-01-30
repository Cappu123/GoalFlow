"""add goals table

Revision ID: 3cc7d00502c2
Revises: 10d367dddbe8
Create Date: 2026-01-28 12:08:31.533692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cc7d00502c2'
down_revision: Union[str, Sequence[str], None] = '10d367dddbe8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
