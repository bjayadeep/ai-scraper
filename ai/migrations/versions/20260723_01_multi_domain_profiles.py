"""add multi-domain job profiles and observation timestamps

Revision ID: 20260723_01
Revises:
Create Date: 2026-07-23
"""
import datetime
from zoneinfo import ZoneInfo

from alembic import op
import sqlalchemy as sa


revision = "20260723_01"
down_revision = None
branch_labels = None
depends_on = None


PROFILES = (
    ("cybersecurity", "Cybersecurity", "US cybersecurity roles from the rolling previous 24 hours.", "rolling_24h"),
    ("java-developer", "Java Developer", "US Java developer roles posted or discovered today in America/New_York.", "calendar_day"),
    ("dotnet-developer", ".NET Developer", "US .NET and C# developer roles posted or discovered today in America/New_York.", "calendar_day"),
)


def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if not inspector.has_table("jobs"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(length=255), nullable=False, unique=True),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("role", sa.String(length=50), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_users_id", "users", ["id"])
        op.create_index("ix_users_email", "users", ["email"], unique=True)
        op.create_table(
            "companies",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False, unique=True),
            sa.Column("ats", sa.String(length=50), nullable=False),
            sa.Column("token", sa.String(length=255), nullable=True),
            sa.Column("careers_url", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_companies_id", "companies", ["id"])
        op.create_index("ix_companies_name", "companies", ["name"], unique=True)
        op.create_index("ix_companies_token", "companies", ["token"])
        op.create_table(
            "jobs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("company", sa.String(length=255), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("location", sa.String(length=255), nullable=True),
            sa.Column("experience_metadata", sa.Text(), nullable=True),
            sa.Column("apply_link", sa.Text(), nullable=False, unique=True),
            sa.Column("date_posted", sa.String(length=50), nullable=True),
            sa.Column("scraped_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_jobs_id", "jobs", ["id"])
        op.create_index("ix_jobs_company", "jobs", ["company"])
        op.create_index("ix_jobs_apply_link", "jobs", ["apply_link"], unique=True)
        op.create_table(
            "activity_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("action", sa.String(length=255), nullable=False),
            sa.Column("details", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_activity_logs_id", "activity_logs", ["id"])
        op.create_table(
            "settings",
            sa.Column("key", sa.String(length=255), primary_key=True),
            sa.Column("value", sa.Text(), nullable=True),
        )
        op.create_index("ix_settings_key", "settings", ["key"], unique=True)

    op.create_table(
        "job_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("window_type", sa.String(length=50), nullable=False),
        sa.Column("timezone", sa.String(length=100), nullable=False, server_default="America/New_York"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_job_profiles_id", "job_profiles", ["id"])
    op.create_index("ix_job_profiles_slug", "job_profiles", ["slug"])

    with op.batch_alter_table("jobs") as batch_op:
        batch_op.add_column(sa.Column("source_posted_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "job_profile_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("job_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("classification_reason", sa.Text(), nullable=True),
        sa.Column("matched_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("job_id", "profile_id", name="uq_job_profile_match"),
    )
    op.create_index("ix_job_profile_matches_job_id", "job_profile_matches", ["job_id"])
    op.create_index("ix_job_profile_matches_profile_id", "job_profile_matches", ["profile_id"])

    now = datetime.datetime.now(datetime.timezone.utc)
    profiles = sa.table(
        "job_profiles",
        sa.column("slug", sa.String), sa.column("name", sa.String),
        sa.column("description", sa.Text), sa.column("enabled", sa.Boolean),
        sa.column("window_type", sa.String), sa.column("timezone", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)), sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(profiles, [
        {"slug": slug, "name": name, "description": description, "enabled": True,
         "window_type": window_type, "timezone": "America/New_York", "created_at": now, "updated_at": now}
        for slug, name, description, window_type in PROFILES
    ])

    jobs = sa.table(
        "jobs", sa.column("id", sa.Integer), sa.column("date_posted", sa.String),
        sa.column("created_at", sa.DateTime), sa.column("scraped_at", sa.DateTime),
        sa.column("source_posted_at", sa.DateTime(timezone=True)),
        sa.column("first_seen_at", sa.DateTime(timezone=True)), sa.column("last_seen_at", sa.DateTime(timezone=True)),
    )
    rows = connection.execute(sa.select(jobs.c.id, jobs.c.date_posted, jobs.c.created_at, jobs.c.scraped_at)).all()
    for row in rows:
        first_seen = row.created_at or row.scraped_at or now
        last_seen = row.scraped_at or row.created_at or now
        if first_seen.tzinfo is None:
            first_seen = first_seen.replace(tzinfo=datetime.timezone.utc)
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=datetime.timezone.utc)
        source_posted = None
        if row.date_posted:
            try:
                source_posted = datetime.datetime.fromisoformat(row.date_posted[:10]).replace(
                    tzinfo=ZoneInfo("America/New_York")
                ).astimezone(datetime.timezone.utc)
            except ValueError:
                pass
        connection.execute(
            jobs.update().where(jobs.c.id == row.id).values(
                source_posted_at=source_posted, first_seen_at=first_seen, last_seen_at=last_seen
            )
        )

    cybersecurity_id = connection.execute(
        sa.text("SELECT id FROM job_profiles WHERE slug = 'cybersecurity'")
    ).scalar_one()
    connection.execute(sa.text(
        "INSERT INTO job_profile_matches (job_id, profile_id, classification_reason, matched_at) "
        "SELECT id, :profile_id, 'Backfilled existing cybersecurity job', :matched_at FROM jobs"
    ), {"profile_id": cybersecurity_id, "matched_at": now})

    with op.batch_alter_table("jobs") as batch_op:
        batch_op.alter_column("first_seen_at", existing_type=sa.DateTime(timezone=True), nullable=False)
        batch_op.alter_column("last_seen_at", existing_type=sa.DateTime(timezone=True), nullable=False)


def downgrade():
    op.drop_table("job_profile_matches")
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.drop_column("last_seen_at")
        batch_op.drop_column("first_seen_at")
        batch_op.drop_column("source_updated_at")
        batch_op.drop_column("source_posted_at")
    op.drop_table("job_profiles")
