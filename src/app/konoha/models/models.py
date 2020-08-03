from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

meta = MetaData()

guild = Table(
    "guild",
    meta,
    Column("id", String(64), nullable=False, primary_key=True),
    Column("prefix", String(255), server_default="!>", nullable=False)
)

hook = Table(
    "hook",
    meta,
    Column("guild", String(64), nullable=False),
    Column("channel", String(64), nullable=False),
    Column("tags", String(255), nullable=False),
    Column("hookurl", String(200), primary_key=True, nullable=False)
)

reminder_config = Table(
    "reminder_config",
    meta,
    Column("id", Integer, nullable=False, primary_key=True, autoincrement=True),
    Column("guild", String(64), nullable=False, unique=True),
    Column("channel", String(64), nullable=False)
)

reminder = Table(
    "reminder",
    meta,
    Column("id", Integer, nullable=False, primary_key=True, autoincrement=True),
    Column("config", Integer, ForeignKey("reminder_config.id"), nullable=False),
    Column("user", String(64), nullable=False),
    Column("content", String(100), nullable=False),
    Column("start_at", DateTime, nullable=False),
    Column("created_at", DateTime, nullable=False),
)
