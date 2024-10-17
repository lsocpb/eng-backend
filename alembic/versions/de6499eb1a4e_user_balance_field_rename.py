"""user balance field rename

Revision ID: de6499eb1a4e
Revises: 6eebf48b8f46
Create Date: 2024-10-17 00:52:35.548429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'de6499eb1a4e'
down_revision: Union[str, None] = '6eebf48b8f46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('balance_total', sa.FLOAT(), nullable=False))
    op.drop_column('user', 'balance_available')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('balance_available', mysql.FLOAT(), nullable=False))
    op.drop_column('user', 'balance_total')
    # ### end Alembic commands ###