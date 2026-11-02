"""engine / SessionLocal / get_db。

同步 Session 就够了：FastAPI 的 def 路由跑在线程池里，
异步 ORM 只会让第 2 周的上传接口多一层坑。
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 长时间空闲后连接被服务端掐断，靠它自动重连
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # commit 后还能读对象属性，接口里少写一次 refresh
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
