"""create address_id to users

Revision ID: d73862f52d44
Revises: 77a620f824f1
Create Date: 2023-01-15 22:26:25.288841

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd73862f52d44'
down_revision = '77a620f824f1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("address_id", sa.Integer, nullable=True))
    op.create_foreign_key("address_users_fk", source_table="users", referent_table="address",
                          local_cols=["address_id"], remote_cols=["id"], ondelete="CASCADE")


def downgrade():
    op.drop_constraint("address_users_fk", table_name="users")
    op.drop_column("users", "address_id")
