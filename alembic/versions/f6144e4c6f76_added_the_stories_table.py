"""Added the stories table

Revision ID: f6144e4c6f76
Revises: 8e3d19adf902
Create Date: 2017-12-11 16:03:56.604884

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6144e4c6f76'
down_revision = '8e3d19adf902'
branch_labels = None
depends_on = None

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('story_id', sa.Integer(), nullable=False),
    sa.Column('hackernews_user_id', sa.Integer(), nullable=False),
    sa.Column('url_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=512), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('time', sa.Integer(), nullable=False),
    sa.Column('descendants', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['hackernews_user_id'], ['hackernews_users.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['url_id'], ['urls.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('story_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stories')
    ### end Alembic commands ###
