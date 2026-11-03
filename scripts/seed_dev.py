"""建一个开发用的租户和一个项目。

Day 2 的上传接口要填 tenant_id 和 tender_id，但鉴权和项目管理接口都还没做。
先把这两行数据弄出来，上传接口才有外键可填。

用法（在项目根目录）：
    python -m scripts.seed_dev

重复执行不会产生重复数据，按 name 查重。
"""

from sqlalchemy import select

from app.db.models import Tender, Tenant
from app.db.session import SessionLocal


def main() -> None:
    with SessionLocal() as db:
        tenant = db.scalars(select(Tenant).where(Tenant.name == "dev")).first()
        if tenant is None:
            tenant = Tenant(name="dev", plan="free")
            db.add(tenant)
            db.flush()  # 拿自增 id，但还没提交
            print(f"created tenant id={tenant.id}")
        else:
            print(f"tenant exists id={tenant.id}")

        tender = db.scalars(
            select(Tender).where(
                Tender.tenant_id == tenant.id, Tender.name == "样本项目"
            )
        ).first()
        if tender is None:
            tender = Tender(tenant_id=tenant.id, name="样本项目", status="draft")
            db.add(tender)
            db.flush()
            print(f"created tender id={tender.id}")
        else:
            print(f"tender exists id={tender.id}")

        db.commit()

    print("")
    print("记下来，明天写接口要用：")
    print(f"  DEV_TENANT_ID={tenant.id}")
    print(f"  DEV_TENDER_ID={tender.id}")


if __name__ == "__main__":
    main()
