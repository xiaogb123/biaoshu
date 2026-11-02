"""Alembic 运行环境。

两个关键点（Day 1 最容易踩的地方）：
1. 必须 import app.db.models —— 不 import，autogenerate 生成的迁移文件就是空的。
2. 连接串从 settings 取，不写死在 alembic.ini。
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import app.db.models  # noqa: F401  仅为让模型注册到 Base.metadata
from app.core.config import settings
from app.db.base import Base

config = context.config

# ini 里的 % 是 ConfigParser 的插值符号，密码里带 % 会炸，所以要转义
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """--sql 模式：只打印 SQL，不连库。没装 Postgres 时靠它自检。"""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
