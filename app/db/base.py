"""所有 ORM 模型的公共基类。

alembic/env.py 里 target_metadata = Base.metadata，
所以模型必须被 import 到（见 app/db/models.py 的 __all__）。
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
