"""Added the tokens table

Revision ID: 6276344586b8
Revises: 6cbf482e0583
Create Date: 2018-06-05 22:13:46.573942

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6276344586b8'
down_revision = '6cbf482e0583'
branch_labels = None
depends_on = None

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('value', sa.String(length=32), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tokens')
    ### end Alembic commands ###
