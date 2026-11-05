"""RQ 任务。

这个文件只做「任务生命周期」：推 jobs 表的状态 -> 调业务函数 -> 记录结果。
业务逻辑都在 services/ 里，这里不写实现。
"""

from pathlib import Path

from redis import Redis
from rq import Queue

from app.core.config import settings
from app.db.models import Job
from app.db.session import SessionLocal
from app.services.pdf import parse_pdf

queue = Queue(connection=Redis.from_url(settings.REDIS_URL))


def parse_document(task_id: int, document_id: int, path: str) -> int:
    """解析一份 PDF，同时把 jobs 表的状态推着走。

    两个参数上的讲究：
    1. path 用 str 不用 Path —— RQ 要把参数序列化进 Redis，Path 序列化不了
    2. 叫 task_id 不叫 job_id —— job_id 是 queue.enqueue() 的保留关键字，
       用它当函数参数会被 RQ 截走，还会报 "Job ID must be a string"
    """
    db = SessionLocal()
    try:
        job = db.get(Job, task_id)
        if job is None:
            raise ValueError(f"job {task_id} 不存在")

        job.status = "running"
        db.commit()

        n = parse_pdf(document_id, Path(path))

        job.status = "done"
        job.progress = 100
        db.commit()
        return n

    except Exception as e:
        db.rollback()
        # rollback 之后 job 可能已过期，重新取一次
        job = db.get(Job, task_id)
        if job is not None:
            job.status = "failed"
            job.error = str(e)[:1000]
            db.commit()
        raise

    finally:
        db.close()
