"""Added the hackernews_users tablee

Revision ID: 7c65717fdf7f
Revises: a442f4daf893
Create Date: 2017-12-11 15:46:32.802698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c65717fdf7f'
down_revision = 'a442f4daf893'
branch_labels = None
depends_on = None

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hackernews_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=40), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hackernews_users')
    ### end Alembic commands ###