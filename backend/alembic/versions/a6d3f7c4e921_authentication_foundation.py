"""add authentication foundation

Revision ID: a6d3f7c4e921
Revises: 6caf9f38df6e
Create Date: 2026-11-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a6d3f7c4e921"
down_revision: Union[str, None] = "6caf9f38df6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "password_changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "email = lower(btrim(email))",
            name="ck_users_email_normalized",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "platform_roles",
        sa.Column("key", sa.String(length=32), nullable=False),
        sa.Column("description", sa.String(length=160), nullable=False),
        sa.Column(
            "is_registration_assignable",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "key <> 'admin' OR is_registration_assignable = false",
            name="ck_platform_roles_admin_not_registration_assignable",
        ),
        sa.PrimaryKeyConstraint("key"),
    )
    op.create_table(
        "user_platform_roles",
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("role_key", sa.String(length=32), nullable=False),
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_key"],
            ["platform_roles.key"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_key"),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("family_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_session_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("device_name", sa.String(length=120), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(
            ["replaced_by_session_id"],
            ["auth_sessions.id"],
            name="fk_auth_sessions_replaced_by_session_id_auth_sessions",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "replaced_by_session_id",
            name="uq_auth_sessions_replaced_by_session_id",
        ),
        sa.UniqueConstraint("token_hash", name="uq_auth_sessions_token_hash"),
    )
    op.create_index("ix_auth_sessions_family_id", "auth_sessions", ["family_id"])
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])

    platform_roles = sa.table(
        "platform_roles",
        sa.column("key", sa.String(length=32)),
        sa.column("description", sa.String(length=160)),
        sa.column("is_registration_assignable", sa.Boolean()),
    )
    op.bulk_insert(
        platform_roles,
        [
            {
                "key": "member",
                "description": "Standard authenticated account",
                "is_registration_assignable": True,
            },
            {
                "key": "admin",
                "description": "Platform administrator",
                "is_registration_assignable": False,
            },
        ],
    )

    op.add_column(
        "musician_profiles",
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_musician_profiles_user_id_users",
        "musician_profiles",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_unique_constraint(
        "uq_musician_profiles_user_id",
        "musician_profiles",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_musician_profiles_user_id",
        "musician_profiles",
        type_="unique",
    )
    op.drop_constraint(
        "fk_musician_profiles_user_id_users",
        "musician_profiles",
        type_="foreignkey",
    )
    op.drop_column("musician_profiles", "user_id")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_family_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_table("user_platform_roles")
    op.drop_table("platform_roles")
    op.drop_table("users")
