"""文档上传与解析。

Day 2 是同步解析：请求进来 -> 落盘 -> 解析 -> 返回。
Day 3 改成投递 RQ 任务、立刻返回 job_id。
"""

import hashlib
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant
from app.core.config import settings
from app.db.models import Document, Tenant
from app.db.session import get_db
from app.schemas.document import DocumentOut
from app.services.pdf import parse_pdf
from app.services.storage import make_key, storage

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

CHUNK_SIZE = 1024 * 1024
MAX_BYTES = settings.MAX_UPLOAD_MB * 1024 * 1024


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    tender_id: int = Form(...),
    kind: str = Form("tender"),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> Document:
    filename = file.filename or "unnamed.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "只接受 .pdf 文件")
    if kind not in {"tender", "bid"}:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "kind 只能是 tender 或 bid")

    tmp_dir = settings.UPLOAD_DIR / "_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / f"{uuid4().hex}.pdf"

    sha = hashlib.sha256()
    size = 0
    try:
        with tmp_path.open("wb") as out:
            first = True
            while chunk := file.file.read(CHUNK_SIZE):
                if first:
                    if not chunk.startswith(b"%PDF"):
                        raise HTTPException(status.HTTP_400_BAD_REQUEST, "文件内容不是 PDF")
                    first = False

                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(
                        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        f"文件超过 {settings.MAX_UPLOAD_MB}MB",
                    )
                sha.update(chunk)
                out.write(chunk)

        if size == 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "空文件")

        digest = sha.hexdigest()

        existing = db.scalars(
            select(Document).where(
                Document.tenant_id == tenant.id,
                Document.sha256 == digest,
            )
        ).first()
        if existing is not None:
            return existing

        key = make_key(tenant.id)
        with tmp_path.open("rb") as src:
            storage.save(key, src)

        doc = Document(
            tenant_id=tenant.id,
            tender_id=tender_id,
            kind=kind,
            filename=filename,
            storage_key=key,
            sha256=digest,
            status="uploaded",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        parse_pdf(doc.id, tmp_path)
        db.refresh(doc)
        return doc

    finally:
        tmp_path.unlink(missing_ok=True)
