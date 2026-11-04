"""手工跑一次 parse_pdf，不经过接口。

用法：python -m scripts.try_parse
"""

from pathlib import Path

from app.db.models import Document
from app.db.session import SessionLocal
from app.services.pdf import parse_pdf

PDF = Path("data/samples/_fixture-扫描件-10页.pdf")


def main() -> None:
    db = SessionLocal()
    doc = Document(
        tenant_id=1,
        tender_id=1,
        kind="tender",
        filename=PDF.name,
        storage_key="test",
        sha256="f" + "0" * 63,
        status="uploaded",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    print("document id =", doc.id)
    print("返回页数 =", parse_pdf(doc.id, PDF))


if __name__ == "__main__":
    main()
