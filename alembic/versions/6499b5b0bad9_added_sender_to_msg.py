"""added sender to msg

Revision ID: 6499b5b0bad9
Revises: 
Create Date: 2022-10-17 20:01:37.073169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6499b5b0bad9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sender', sa.Integer(), nullable=False))
        batch_op.create_foreign_key("fk_message_sender", 'user', ['sender'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message', schema=None) as batch_op:
        # batch_op.drop_column('sender')
        batch_op.drop_constraint("fk_message_sender", type_='foreignkey')

    # ### end Alembic commands ###
