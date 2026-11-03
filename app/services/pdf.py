import logging
from io import BytesIO
from pathlib import Path

import pymupdf
from sqlalchemy import delete

from app.db.models import DocPage, Document
from app.db.session import SessionLocal
from app.services.storage import make_key, storage

logger = logging.getLogger(__name__)

OCR_TEXT_THRESHOLD = 50
BATCH_SIZE = 10
IMAGE_DPI = 200

def parse_pdf(document_id:int,path:Path) -> int:
    with SessionLocal() as db:
        doc = db.get(Document, document_id)
        if doc is None:
            raise ValueError(f"Document {document_id} not found")

        doc.status = "parsing"
        db.commit()

        try:
            db.execute(delete(DocPage).where(DocPage.document_id == document_id))
            db.commit()

            batch: list[dict] = []
            page_count = 0

            with pymupdf.open(path) as pdf:
                for page_no,page in enumerate(pdf,start=1):
                    text = page.get_text("text") or ""
                    need_ocr = len(text.strip()) < OCR_TEXT_THRESHOLD


                    image_key = None
                    if need_ocr:
                        pix = page.get_pixmap(dpi=IMAGE_DPI)
                        image_key = make_key(doc.tenant_id,".png")
                        storage.save(image_key,BytesIO(pix.tobytes("png")))
                        pix = None

                    batch.append({
                        "document_id": document_id,
                        "page_no": page_no,
                        "text": text,
                        "ocr_used": need_ocr,
                        "image_key": image_key,
                    })
                    page_count = page_no
                    if len(batch) >= BATCH_SIZE:
                        db.bulk_insert_mappings(DocPage, batch)
                        db.commit()
                        batch.clear()
            print("处理完",page_count,"页，待入库",len(batch),"条")

            if batch :
                db.bulk_insert_mappings(DocPage, batch)
                db.commit()

            doc.page_count  = page_count
            doc.status = "parsed"
            db.commit()
            logger.info("doc %s 解析完成：%s 页",document_id,page_count)
            return page_count


        except Exception:
            db.rollback()
            doc.status = "failed"
            db.commit()
            raise