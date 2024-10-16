"""default value2

Revision ID: 15b2e9c4f312
Revises: 17fb04d2ef65
Create Date: 2024-10-16 18:12:07.442385

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '15b2e9c4f312'
down_revision: Union[str, None] = '17fb04d2ef65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bid', 'current_bid_winner_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bid', 'current_bid_winner_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###