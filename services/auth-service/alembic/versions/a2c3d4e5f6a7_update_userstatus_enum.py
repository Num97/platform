"""update_userstatus_enum

Revision ID: a2c3d4e5f6a7
Revises: f8b7b1c6161c
Create Date: 2026-05-27 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'a2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'f8b7b1c6161c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE users SET status = 'ACTIVE' WHERE status NOT IN ('ACTIVE', 'INACTIVE')")

    op.execute("ALTER TYPE userstatus RENAME TO userstatus_old")

    op.execute("CREATE TYPE userstatus AS ENUM ('ACTIVE', 'INACTIVE')")

    op.execute("""
        ALTER TABLE users ALTER COLUMN status
        TYPE userstatus USING status::text::userstatus
    """)

    op.execute("DROP TYPE userstatus_old")


def downgrade() -> None:
    op.execute("ALTER TYPE userstatus RENAME TO userstatus_new")

    op.execute("CREATE TYPE userstatus AS ENUM ('ACTIVE', 'INACTIVE', 'BANNED', 'PENDING')")

    op.execute("""
        ALTER TABLE users ALTER COLUMN status
        TYPE userstatus USING status::text::userstatus
    """)

    op.execute("DROP TYPE userstatus_new")
