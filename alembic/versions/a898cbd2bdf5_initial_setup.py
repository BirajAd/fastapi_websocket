"""Initial setup

Revision ID: a898cbd2bdf5
Revises: 
Create Date: 2022-10-10 21:00:02.538296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a898cbd2bdf5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('connection',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_connection_id'), 'connection', ['id'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sent_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('read_at', sa.DateTime(), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('connection', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['connection'], ['connection.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_id'), 'message', ['id'], unique=False)
    op.create_table('participance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conn_id', sa.Integer(), nullable=True),
    sa.Column('member', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['conn_id'], ['connection.id'], ),
    sa.ForeignKeyConstraint(['member'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_participance_id'), 'participance', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_participance_id'), table_name='participance')
    op.drop_table('participance')
    op.drop_index(op.f('ix_message_id'), table_name='message')
    op.drop_table('message')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_connection_id'), table_name='connection')
    op.drop_table('connection')
    # ### end Alembic commands ###
