"""条款落库（幂等）。

两个必须写下来的决策：

1. tenant_id / tender_id 从 documents 表反查，不让调用方传。
   Clause 表里这两个都是 NOT NULL，调用方要凑齐三个 id，
   早晚会出现 "document 2 配 tender 3" 这种组合，而且查起来极难。

2. 先 DELETE 再 INSERT，两步在同一个事务里。
   重跑同一份文件，行数不变——这是 Day 5 的第一条验收。
   同事务保证中途崩溃时不会留下"删了但没插进去"的空表。
"""

from typing import Any

from sqlalchemy import delete, insert

from app.db.models import Clause, Document
from app.db.session import SessionLocal
from app.schemas.extraction import ExtractedClause
from app.services.normalize import extract_clause_no, fix_category, normalize_text

def prepare(raw: list[ExtractedClause]) -> list[ExtractedClause]:
    """落库前的最后一道加工：分类兜底 + 补编号。

        用 model_copy 而不是直接改属性：不改调用方手里那份数据，
        同一条原始结果可以拿去落两次、做对比。
    """
    out: list[ExtractedClause] = []
    for c in raw:
        out.append(
            c.model_copy(
                update={
                    "category":fix_category(c.category,c.quote),
                    "clause_no":c.clause_no or extract_clause_no(c.quote),
                }
            )
        )
    return out

def save_clauses(document_id:int,clauses:list[ExtractedClause]) -> int:
    """按 document 幂等写入，返回写入条数。

    空列表直接抛错：调用方"抽到 0 条"绝大多数是上游失败（网络抖动、
    超时、模型返回空），这时候执行 DELETE 会把已有条款静默清空。
    万一某份文件真的没有条款，调用方显式跳过落库即可。
    """
    if not clauses:
        raise ValueError(f"document {document_id} 抽取结果为空，拒绝清库")

    with SessionLocal() as db:
        doc = db.get(Document,document_id)
        if doc is None:
            raise ValueError(f"Document {document_id} 不存在")

        db.execute(delete(Clause).where(Clause.document_id == document_id))

        rows: list[dict[str, Any]] = [
            {
                "tenant_id": doc.tenant_id,
                "tender_id": doc.tender_id,
                "document_id": doc.id,
                "page_no": c.page_no,
                "category": c.category.value,
                "clause_no": c.clause_no,
                "text": c.text,
                "quote": c.quote,
                "normalized": normalize_text(c.quote),
                "confidence": c.confidence,
            }
            for c in clauses
        ]

        if rows:
            db.execute(insert(Clause), rows)
        db.commit()
        return len(rows)