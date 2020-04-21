"""post_model

Revision ID: c077ddefcd69
Revises: 941d2c4008f8
Create Date: 2020-04-21 09:56:31.089721

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c077ddefcd69'
down_revision = '941d2c4008f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('post_text', sa.String(), nullable=True),
    sa.Column('post_date', sa.DateTime(), nullable=False),
    sa.Column('post_modified', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_model_post_date'), 'post_model', ['post_date'], unique=False)
    op.create_index(op.f('ix_post_model_post_modified'), 'post_model', ['post_modified'], unique=False)
    op.create_index(op.f('ix_post_model_post_text'), 'post_model', ['post_text'], unique=False)
    op.create_index(op.f('ix_post_model_title'), 'post_model', ['title'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_post_model_title'), table_name='post_model')
    op.drop_index(op.f('ix_post_model_post_text'), table_name='post_model')
    op.drop_index(op.f('ix_post_model_post_modified'), table_name='post_model')
    op.drop_index(op.f('ix_post_model_post_date'), table_name='post_model')
    op.drop_table('post_model')
    # ### end Alembic commands ###