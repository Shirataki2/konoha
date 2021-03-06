import sqlalchemy as sa
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

meta = MetaData()

guild = Table(
    "guild",
    meta,
    Column("id", String(64), nullable=False, primary_key=True),
    Column("prefix", String(255), server_default=">", nullable=False),
    Column("gc_channel", String(255), nullable=True),
    Column("gc_url", String(255), nullable=True),
    Column("dice", Boolean, nullable=False, server_default=sa.sql.false()),
    Column("expand", Boolean, server_default=sa.sql.false(), nullable=True),
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
    Column("id", Integer, nullable=False,
           primary_key=True, autoincrement=True),
    Column("guild", String(64), nullable=False, unique=True),
    Column("channel", String(64), nullable=False)
)

reminder = Table(
    "reminder",
    meta,
    Column("id", Integer, nullable=False,
           primary_key=True, autoincrement=True),
    Column("config", Integer, ForeignKey(
        "reminder_config.id"), nullable=False),
    Column("user", String(64), nullable=False),
    Column("content", String(100), nullable=False),
    Column("start_at", DateTime, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

error_log = Table(
    "error_log",
    meta,
    Column("id", String(24), nullable=False),
    Column("guild", String(24)),
    Column("channel", String(24)),
    Column("message", String(24)),
    Column("user", String(24), nullable=False),
    Column("command", String(256), nullable=False),
    Column("name", String(24), nullable=False),
    Column("detail", String(512), nullable=False),
    Column("traceback", String(8192), nullable=False),
)

user_status = Table(
    "user_status",
    meta,
    Column("id", String(24), primary_key=True, nullable=False),
    Column("moderator", Boolean(), nullable=True),
    Column("muted", Boolean(), nullable=True, server_default=sa.sql.false()),
)

vote = Table(
    "vote",
    meta,
    Column("id", String(24), primary_key=True, nullable=False),
    Column("guild", String(24), nullable=False),
    Column("channel", String(24), nullable=False),
    Column("message", String(24), nullable=False),
    Column("user", String(24), nullable=False),
    Column("description", String(3000), nullable=False),
    Column("opov", Boolean, server_default=sa.sql.false()),
)


timer = Table(
    "timer",
    meta,
    Column("id", String(16), nullable=False,
           primary_key=True),
    Column("event", String(64), nullable=False),
    Column("payload", String(2048), nullable=False),
    Column("expire_at", DateTime, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

noun = Table(
    "noun",
    meta,
    Column("first", String(1)),
    Column("name", String(16)),
    Column("yomi", String(32)),
)

money = Table(
    "money",
    meta,
    Column("user", String(24), nullable=False),
    Column("guild", String(24), nullable=False),
    Column("amount", Integer),
    Column("turnip", Integer),
    Column("bonus", Integer),
)

starboard_config = Table(
    "starboard_config",
    meta,
    Column("guild", String(24), nullable=False),
    Column("channel", String(24), nullable=False),
    Column("require", Integer, server_default='1'),
    Column("enabled", Boolean, server_default=sa.sql.true()),
)

starboard = Table(
    "starboard",
    meta,
    Column("guild", String(24), nullable=False),
    Column("channel", String(24), nullable=False),
    Column("message", String(24), nullable=False),
    Column("user", String(24), nullable=False),
    Column("board_message", String(24), nullable=False),
)

rolepanel = Table(
    "rolepanel",
    meta,
    Column("id", String(16), nullable=False,
           primary_key=True),
    Column("guild", String(24), nullable=False),
    Column("channel", String(24), nullable=False),
    Column("message", String(24), nullable=False),
    Column("user", String(24), nullable=False),
    Column("payload", String(1000), nullable=False),
)

join_role = Table(
    "join_role",
    meta,
    Column("guild", String(24), nullable=False),
    Column("role", String(24), unique=True, nullable=False),
)
