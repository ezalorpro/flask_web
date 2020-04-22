"""wtf

Revision ID: 85664cd33531
Revises: e032cee1827b
Create Date: 2020-04-22 15:44:45.018749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85664cd33531'
down_revision = 'e032cee1827b'
branch_labels = None
depends_on = None


# Enum 'type' for PostgreSQL
enum_name = 'genderderenum'
# Set temporary enum 'type' for PostgreSQL
tmp_enum_name = 'tmp_' + enum_name

# Options for Enum
old_options = ('hombre', 'mujer')
new_options = ('nulo', 'hombre', 'mujer')

# Create enum fields
old_type = sa.Enum(*old_options, name=enum_name)
new_type = sa.Enum(*new_options, name=enum_name)

def upgrade():
    # Rename current enum type to tmp_
    op.execute('ALTER TYPE ' + enum_name + ' RENAME TO ' + tmp_enum_name)
    # Create new enum type in db
    new_type.create(op.get_bind())
    # Update column to use new enum type
    op.execute('ALTER TABLE public."user" ALTER COLUMN gender TYPE ' + enum_name + ' USING gender::text::' + enum_name)
    # Drop old enum type
    op.execute('DROP TYPE ' + tmp_enum_name)


def downgrade():
    # Instantiate db query
    audit = sa.sql.table('user', sa.Column('gender', new_type, nullable=False))
    # Rename enum type to tmp_
    op.execute('ALTER TYPE ' + enum_name + ' RENAME TO ' + tmp_enum_name)
    # Create enum type using old values
    old_type.create(op.get_bind())
    # Set enum type as type for event_type column
    op.execute('ALTER TABLE public."user"  ALTER COLUMN gender TYPE ' + enum_name + ' USING gender::text::' + enum_name)
    # Drop temp enum type
    op.execute('DROP TYPE ' + tmp_enum_name)

