"""投递一个解析任务到 RQ，验证 worker 能接住。

用法：python -m scripts.try_enqueue
"""

from pathlib import Path
from uuid import uuid4

from app.db.models import Document, Job
from app.db.session import SessionLocal
from app.workers.tasks import parse_document, queue

PDF = Path("data/samples/_fixture-扫描件-10页.pdf")


def main() -> None:
    db = SessionLocal()

    doc = Document(
        tenant_id=1,
        tender_id=1,
        kind="tender",
        filename=PDF.name,
        storage_key="test",
        # 每次跑用不同的假哈希，避开 (tenant_id, sha256) 唯一约束
        sha256=uuid4().hex.ljust(64, "0"),
        status="uploaded",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    job = Job(
        tenant_id=1,
        kind="parse_document",
        payload={"document_id": doc.id},
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    rq_job = queue.enqueue(
        parse_document,
        task_id=job.id,
        document_id=doc.id,
        path=str(PDF.resolve()),
    )

    print("documents.id =", doc.id)
    print("jobs.id      =", job.id)
    print("rq job id    =", rq_job.id)


if __name__ == "__main__":
    main()
