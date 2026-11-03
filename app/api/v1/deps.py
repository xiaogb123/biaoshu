from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Tenant
from app.db.session import get_db

DEV_TENANT_ID = 1

def get_current_tenant(db:Session = Depends(get_db)) -> Tenant:
    tenant = db.get(Tenant,DEV_TENANT_ID)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="开发租户不存在，先执行 python -m scripts.seed_dev",
        )
    return tenant