"""initial

Revision ID: f8b7b1c6161c
Revises:
Create Date: 2026-05-27 21:51:18.618689

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f8b7b1c6161c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TABLE IF NOT EXISTS users ("
               "id SERIAL PRIMARY KEY, "
               "email VARCHAR(255) NOT NULL UNIQUE, "
               "username VARCHAR(100) NOT NULL UNIQUE, "
               "hashed_password VARCHAR(255) NOT NULL, "
               "full_name VARCHAR(255), "
               "role VARCHAR(50) NOT NULL DEFAULT 'user', "
               "status VARCHAR(50) NOT NULL DEFAULT 'active', "
               "is_active BOOLEAN DEFAULT TRUE, "
               "password_reset_token VARCHAR(255), "
               "password_reset_expires TIMESTAMP WITH TIME ZONE, "
               "created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), "
               "updated_at TIMESTAMP WITH TIME ZONE, "
               "last_login TIMESTAMP WITH TIME ZONE"
               ")")

    op.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_username ON users (username)")

    op.execute("CREATE TABLE IF NOT EXISTS refresh_tokens ("
               "id SERIAL PRIMARY KEY, "
               "token VARCHAR(500) NOT NULL UNIQUE, "
               "user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, "
               "expires_at TIMESTAMP WITH TIME ZONE NOT NULL, "
               "created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), "
               "is_revoked BOOLEAN DEFAULT FALSE, "
               "revoked_at TIMESTAMP WITH TIME ZONE, "
               "revoked_reason VARCHAR(255), "
               "device_info VARCHAR(500), "
               "ip_address VARCHAR(45), "
               "user_agent VARCHAR(500)"
               ")")

    op.execute("CREATE INDEX IF NOT EXISTS ix_refresh_tokens_id ON refresh_tokens (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_refresh_tokens_token ON refresh_tokens (token)")


def downgrade() -> None:
    op.drop_index(op.f('ix_refresh_tokens_token'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')

    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
