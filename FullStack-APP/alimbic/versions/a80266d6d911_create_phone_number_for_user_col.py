"""create phone number for user col

Revision ID: a80266d6d911
Revises: 
Create Date: 2023-01-15 17:17:05.953003

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a80266d6d911'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'phone_number')
