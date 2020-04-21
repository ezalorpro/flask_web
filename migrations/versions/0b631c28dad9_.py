"""empty message

Revision ID: 0b631c28dad9
Revises: 1f2b2a7676ab
Create Date: 2020-04-20 10:32:01.446848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b631c28dad9'
down_revision = '1f2b2a7676ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_user_is_admin'), 'user', ['is_admin'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_is_admin'), table_name='user')
    op.drop_column('user', 'is_admin')
    # ### end Alembic commands ###