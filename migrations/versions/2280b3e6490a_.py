"""empty message

Revision ID: 2280b3e6490a
Revises: e142077133aa
Create Date: 2020-04-24 15:19:07.376706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2280b3e6490a'
down_revision = 'e142077133aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('image_post_model', 'path',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('image_post_model', 'path',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
