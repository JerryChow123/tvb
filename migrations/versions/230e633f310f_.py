"""empty message

Revision ID: 230e633f310f
Revises: f82e2f04d8a8
Create Date: 2022-04-20 13:07:51.399435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '230e633f310f'
down_revision = 'f82e2f04d8a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('root', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'root')
    # ### end Alembic commands ###
