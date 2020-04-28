"""empty message

Revision ID: fff23736b493
Revises: c4c99e5c0b57
Create Date: 2020-04-25 11:06:48.387472

"""
from alembic import op
import sqlalchemy as sa
from flask_web_app.models import ChoiceType


# revision identifiers, used by Alembic.
revision = 'fff23736b493'
down_revision = 'c4c99e5c0b57'
branch_labels = None
depends_on = None

roles = {
    'regular_user': "Usuario regular",
    'editor': "Editor",
    'admin': "Admin"
}

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role', ChoiceType(roles), nullable=True))
    op.create_index(op.f('ix_user_role'), 'user', ['role'], unique=False)
    op.drop_index('ix_user_is_admin', table_name='user')
    op.drop_column('user', 'is_admin')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.create_index('ix_user_is_admin', 'user', ['is_admin'], unique=False)
    op.drop_index(op.f('ix_user_role'), table_name='user')
    op.drop_column('user', 'role')
    # ### end Alembic commands ###