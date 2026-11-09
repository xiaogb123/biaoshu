"""落库幂等自测：手写数据，不调模型。

三条断言：
1. 空列表必须抛错（防止抽取失败时静默清库）
2. 写两次行数不翻倍（幂等）
3. 旧数据被清掉（DELETE + INSERT 在同一个事务里）

跑完会把 doc 13 清空，不留垃圾。
"""

from sqlalchemy import delete, func, select

from app.db.models import Clause, Document
from app.db.session import SessionLocal
from app.schemas.clause import ClauseCategory
from app.schemas.extraction import ExtractedClause
from app.services.persist import prepare, save_clauses

DOC = 13  # 5 页的小样件，不碰 doc 2

fails: list[str] = []


def check(label: str, got, want) -> None:
    ok = got == want
    print(f"[{'OK ' if ok else 'BAD'}] {label:34} got={got!r}")
    if not ok:
        print(f"       {'':34} want={want!r}")
        fails.append(label)


def count() -> int:
    with SessionLocal() as db:
        return db.scalar(select(func.count()).select_from(Clause).where(Clause.document_id == DOC)) or 0


def seed(n: int) -> None:
    """预置 n 条"旧数据"，模拟重跑前库里已有内容。"""
    with SessionLocal() as db:
        db.execute(delete(Clause).where(Clause.document_id == DOC))
        db.commit()
    with SessionLocal() as db:
        doc = db.get(Document, DOC)
        db.add_all([
            Clause(tenant_id=doc.tenant_id, tender_id=doc.tender_id, document_id=DOC,
                   page_no=900 + i, category="format", clause_no=None,
                   text="old", quote="old", normalized="old", confidence=0.1)
            for i in range(n)
        ])
        db.commit()


items = [
    ExtractedClause(category=ClauseCategory.format, clause_no=None,
                    text="未按要求密封的，其投标无效。",
                    quote="未按要求密封的，其投标无效。",
                    page_no=1, confidence=0.90),
    ExtractedClause(category=ClauseCategory.submission, clause_no=None,
                    text="递交截止时间为 9 时。",
                    quote="14.2 递交截止时间为 9 时。",
                    page_no=2, confidence=0.80),
]
prepared = prepare(items)

# 1) 空列表守卫
try:
    save_clauses(DOC, [])
    print("[BAD] 空列表没抛错")
    fails.append("空列表守卫")
except ValueError as e:
    print(f"[OK ] 空列表抛错: {e}")

# 2) 幂等：库里有 4 条旧数据，写 2 条后应该只剩 2 条
seed(4)
check("预置旧数据", count(), 4)
n1 = save_clauses(DOC, prepared)
check("第 1 次写 2 条（旧数据应清掉）", count(), 2)
n2 = save_clauses(DOC, prepared)
check("第 2 次写 2 条（没翻倍）", count(), 2)
check("返回值等于条数", (n1, n2), (2, 2))

with SessionLocal() as db:
    rows = db.scalars(select(Clause).where(Clause.document_id == DOC).order_by(Clause.page_no)).all()
    for r in rows:
        print(f"      p{r.page_no} {r.category:16} no={str(r.clause_no):9} {r.text[:16]!r}")

by_page = {r.page_no: r for r in rows}
check("分类兜底 format→disq", by_page[1].category, "disqualification")
check("编号从 quote 提出来", by_page[2].clause_no, "14.2")
check("normalized 已填", bool(by_page[1].normalized), True)

# 清场
with SessionLocal() as db:
    db.execute(delete(Clause).where(Clause.document_id == DOC))
    db.commit()
check("清场", count(), 0)

print()
if fails:
    print(f"失败 {len(fails)} 项: {fails}")
    raise SystemExit(1)
print("全部通过")
