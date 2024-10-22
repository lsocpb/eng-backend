"""billing test

Revision ID: d441a50de37b
Revises: a6d8d03e44ee
Create Date: 2024-10-21 20:51:53.628358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd441a50de37b'
down_revision: Union[str, None] = 'a6d8d03e44ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company_billing',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_details', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['billing.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_billing',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('details', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['billing.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('buyer', sa.Column('billing_details_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'buyer', 'billing', ['billing_details_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'buyer', type_='foreignkey')
    op.drop_column('buyer', 'billing_details_id')
    op.drop_table('user_billing')
    op.drop_table('company_billing')
    # ### end Alembic commands ###
