"""条款查询接口。

GET /api/v1/tenders/{tender_id}/clauses?category=&page=1&page_size=20
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant
from app.db.models import Clause, Tenant, Tender
from app.db.session import get_db
from app.schemas.clause import ClauseCategory, ClauseOut, ClausePage

router = APIRouter(prefix="/api/v1/tenders",tags=["clauses"])

@router.get("/{tender_id}/clauses",response_model=ClausePage)
def list_clauses(
    tender_id: int,
    category: ClauseCategory | None = Query(None, description="按分类过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> ClausePage:
    tender = db.get(Tender,tender_id)
    if tender is None or tender.tenant_id != tenant.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND,"项目不存在")

    where = [Clause.tender_id == tender.id,Clause.tenant_id == tenant.id]
    if category is not None:
        where.append(Clause.category == category.value)

    total = db.scalar(select(func.count()).select_from(Clause).where(*where)) or 0
    rows = db.scalars(
        select(Clause)
        .where(*where)
        .order_by(Clause.page_no,Clause.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return ClausePage(
        items=[ClauseOut.model_validate(r) for r in rows],
        total = total,
        page = page,
        page_size = page_size,
    )
    