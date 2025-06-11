"""Altera admission_date para datetime

Revision ID: f964040a6aa3
Revises: a387e7e48b78
Create Date: 2025-06-11 09:07:54.674295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f964040a6aa3'
down_revision: Union[str, None] = 'a387e7e48b78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'employee',
        'admission_date',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="admission_date::timestamp"
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'employee',
        'admission_date',
        existing_type=sa.DateTime(),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using="admission_date::text"
    )

