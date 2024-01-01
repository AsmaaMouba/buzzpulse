"""initial_migration

Revision ID: ed702f2e1679
Revises: 0705058c5865
Create Date: 2023-12-15 19:44:25.530325

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ed702f2e1679'
down_revision = '0705058c5865'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_index('ix_events_sender_id')

    op.drop_table('events')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('sender_id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('type_name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('timestamp', mysql.FLOAT(), nullable=True),
    sa.Column('intent_name', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('action_name', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('data', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.create_index('ix_events_sender_id', ['sender_id'], unique=False)

    # ### end Alembic commands ###
