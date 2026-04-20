"""cascade alerts on file delete + index

Revision ID: a1b2c3d4e5f6
Revises: 0d6439d2e79f
Create Date: 2026-04-20 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "0d6439d2e79f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing FK and recreate it with ON DELETE CASCADE so removing a
    # file automatically clears its alert history.
    op.drop_constraint("alerts_file_id_fkey", "alerts", type_="foreignkey")
    op.create_foreign_key(
        "alerts_file_id_fkey",
        "alerts",
        "files",
        ["file_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_alerts_file_id", "alerts", ["file_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_alerts_file_id", table_name="alerts")
    op.drop_constraint("alerts_file_id_fkey", "alerts", type_="foreignkey")
    op.create_foreign_key(
        "alerts_file_id_fkey",
        "alerts",
        "files",
        ["file_id"],
        ["id"],
    )
