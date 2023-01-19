"""add apt num col

Revision ID: d792f9619c25
Revises: d73862f52d44
Create Date: 2023-01-16 11:33:29.028629

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd792f9619c25'
down_revision = 'd73862f52d44'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("address", sa.Column("apt_num", sa.Integer, nullable=True))


def downgrade():
    op.drop_column("address", "apt_num")
