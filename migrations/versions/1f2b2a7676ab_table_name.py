"""table name

Revision ID: 1f2b2a7676ab
Revises: e382faca0e28
Create Date: 2020-04-19 13:10:40.217047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f2b2a7676ab'
down_revision = 'e382faca0e28'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('gender', sa.Enum('hombre', 'mujer', name='genderderenum'), nullable=True),
    sa.Column('information', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_first_name'), 'user', ['first_name'], unique=False)
    op.create_index(op.f('ix_user_gender'), 'user', ['gender'], unique=False)
    op.create_index(op.f('ix_user_information'), 'user', ['information'], unique=False)
    op.create_index(op.f('ix_user_last_name'), 'user', ['last_name'], unique=False)
    op.create_index(op.f('ix_user_location'), 'user', ['location'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.drop_index('ix_usuario_email', table_name='usuario')
    op.drop_index('ix_usuario_first_name', table_name='usuario')
    op.drop_index('ix_usuario_gender', table_name='usuario')
    op.drop_index('ix_usuario_information', table_name='usuario')
    op.drop_index('ix_usuario_last_name', table_name='usuario')
    op.drop_index('ix_usuario_location', table_name='usuario')
    op.drop_index('ix_usuario_username', table_name='usuario')
    op.drop_table('usuario')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('usuario',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(), nullable=False),
    sa.Column('first_name', sa.VARCHAR(), nullable=True),
    sa.Column('last_name', sa.VARCHAR(), nullable=True),
    sa.Column('email', sa.VARCHAR(), nullable=False),
    sa.Column('password_hash', sa.VARCHAR(), nullable=False),
    sa.Column('location', sa.VARCHAR(), nullable=True),
    sa.Column('gender', sa.VARCHAR(length=6), nullable=True),
    sa.Column('information', sa.VARCHAR(), nullable=True),
    sa.CheckConstraint("gender IN ('hombre', 'mujer')", name='genderderenum'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_usuario_username', 'usuario', ['username'], unique=1)
    op.create_index('ix_usuario_location', 'usuario', ['location'], unique=False)
    op.create_index('ix_usuario_last_name', 'usuario', ['last_name'], unique=False)
    op.create_index('ix_usuario_information', 'usuario', ['information'], unique=False)
    op.create_index('ix_usuario_gender', 'usuario', ['gender'], unique=False)
    op.create_index('ix_usuario_first_name', 'usuario', ['first_name'], unique=False)
    op.create_index('ix_usuario_email', 'usuario', ['email'], unique=1)
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_location'), table_name='user')
    op.drop_index(op.f('ix_user_last_name'), table_name='user')
    op.drop_index(op.f('ix_user_information'), table_name='user')
    op.drop_index(op.f('ix_user_gender'), table_name='user')
    op.drop_index(op.f('ix_user_first_name'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###