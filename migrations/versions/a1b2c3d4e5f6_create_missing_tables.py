"""create missing tables (post_edit_requests, post_revisions, site_settings,
location_reports, comments, chat_messages, chat_presences, discussion_posts,
discussion_comments, discussion_tags, discussion_post_tags)

Revision ID: a1b2c3d4e5f6
Revises: 93d267453bf0
Create Date: 2026-03-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "93d267453bf0"
branch_labels = None
depends_on = None


def upgrade():
    # ── site_settings ────────────────────────────────────────────────────────
    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.UniqueConstraint("key"),
    )

    # ── location_reports ─────────────────────────────────────────────────────
    op.create_table(
        "location_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # ── post_revisions ───────────────────────────────────────────────────────
    op.create_table(
        "post_revisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("editor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("editor_label", sa.String(length=60), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("province", sa.String(length=120), nullable=True),
        sa.Column("municipality", sa.String(length=120), nullable=True),
        sa.Column("repressor_name", sa.String(length=160), nullable=True),
        sa.Column("other_type", sa.String(length=160), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("polygon_geojson", sa.Text(), nullable=True),
        sa.Column("links_json", sa.Text(), nullable=True),
        sa.Column("media_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # ── post_edit_requests ───────────────────────────────────────────────────
    op.create_table(
        "post_edit_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("editor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("editor_label", sa.String(length=60), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("province", sa.String(length=120), nullable=True),
        sa.Column("municipality", sa.String(length=120), nullable=True),
        sa.Column("repressor_name", sa.String(length=160), nullable=True),
        sa.Column("other_type", sa.String(length=160), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("polygon_geojson", sa.Text(), nullable=True),
        sa.Column("links_json", sa.Text(), nullable=True),
        sa.Column("media_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # ── comments ─────────────────────────────────────────────────────────────
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("author_label", sa.String(length=60), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("upvotes", sa.Integer(), nullable=True),
        sa.Column("downvotes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # ── chat_messages ────────────────────────────────────────────────────────
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("author_label", sa.String(length=80), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True, index=True),
    )

    # ── chat_presences ───────────────────────────────────────────────────────
    op.create_table(
        "chat_presences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("nickname", sa.String(length=80), nullable=False),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_chat_presences_session_id", "chat_presences", ["session_id"], unique=True)
    op.create_index("ix_chat_presences_last_seen",  "chat_presences", ["last_seen"],  unique=False)

    # ── posts: columnas extra ────────────────────────────────────────────────
    with op.batch_alter_table("posts") as batch_op:
        batch_op.add_column(sa.Column("province",       sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("municipality",   sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("repressor_name", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("other_type",     sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("polygon_geojson",sa.Text(),             nullable=True))
        batch_op.add_column(sa.Column("links_json",     sa.Text(),             nullable=True))
        batch_op.add_column(sa.Column("verify_count",   sa.Integer(),          nullable=True))

    # ── Enum hidden/deleted en post_status ───────────────────────────────────
    # PostgreSQL no permite ALTER TYPE dentro de una transacción fácilmente,
    # así que recreamos el enum con los nuevos valores.
    op.execute("ALTER TYPE post_status ADD VALUE IF NOT EXISTS 'hidden'")
    op.execute("ALTER TYPE post_status ADD VALUE IF NOT EXISTS 'deleted'")

    # ── discussion_tags ──────────────────────────────────────────────────────
    op.create_table(
        "discussion_tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_discussion_tags_slug", "discussion_tags", ["slug"], unique=True)

    # ── discussion_posts ─────────────────────────────────────────────────────
    op.create_table(
        "discussion_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("body_html", sa.Text(), nullable=False),
        sa.Column("links_json", sa.Text(), nullable=True),
        sa.Column("images_json", sa.Text(), nullable=True),
        sa.Column("author_label", sa.String(length=80), nullable=False),
        sa.Column("upvotes", sa.Integer(), nullable=True),
        sa.Column("downvotes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # ── discussion_post_tags (join table) ────────────────────────────────────
    op.create_table(
        "discussion_post_tags",
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("discussion_posts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id",  sa.Integer(), sa.ForeignKey("discussion_tags.id",  ondelete="CASCADE"), primary_key=True),
    )

    # ── discussion_comments ──────────────────────────────────────────────────
    op.create_table(
        "discussion_comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id",   sa.Integer(), sa.ForeignKey("discussion_posts.id"),    nullable=False),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("discussion_comments.id", ondelete="CASCADE"), nullable=True),
        sa.Column("body",        sa.Text(), nullable=False),
        sa.Column("body_html",   sa.Text(), nullable=False),
        sa.Column("author_label",sa.String(length=80), nullable=False),
        sa.Column("upvotes",   sa.Integer(), nullable=True),
        sa.Column("downvotes", sa.Integer(), nullable=True),
        sa.Column("created_at",sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table("discussion_comments")
    op.drop_table("discussion_post_tags")
    op.drop_table("discussion_posts")
    op.drop_index("ix_discussion_tags_slug", table_name="discussion_tags")
    op.drop_table("discussion_tags")
    op.drop_table("comments")
    op.drop_index("ix_chat_presences_last_seen",  table_name="chat_presences")
    op.drop_index("ix_chat_presences_session_id", table_name="chat_presences")
    op.drop_table("chat_presences")
    op.drop_table("chat_messages")
    op.drop_table("post_edit_requests")
    op.drop_table("post_revisions")
    op.drop_table("location_reports")
    op.drop_table("site_settings")
