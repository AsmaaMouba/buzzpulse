"""lastt

Revision ID: 0705058c5865
Revises: c9313bbb353f
Create Date: 2023-08-30 07:21:35.792268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0705058c5865'
down_revision = 'c9313bbb353f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('campaign', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=100), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('campaign', schema=None) as batch_op:
        batch_op.drop_column('status')

    # ### end Alembic commands ###
