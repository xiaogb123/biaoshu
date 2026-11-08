"""去重逻辑自测。手写 5 条数据，不调模型、不连数据库。

除了断言，还把实测相似度打出来——让"阈值 90"变成看得见的数字。
"""

from rapidfuzz import fuzz

from app.schemas.clause import ClauseCategory
from app.schemas.extraction import ExtractedClause
from app.services.dedupe import dedupe
from app.services.normalize import normalize_text, squash

fails: list[str] = []


def check(label: str, got, want) -> None:
    ok = got == want
    print(f"[{'OK ' if ok else 'BAD'}] {label:20} got={got!r}")
    if not ok:
        print(f"       {'':20} want={want!r}")
        fails.append(label)


def mk(cat, quote, page, conf):
    return ExtractedClause(
        category=cat,
        clause_no=None,
        text=quote[:20],
        quote=quote,
        page_no=page,
        confidence=conf,
    )


items = [
    # 1 和 2：同一句话，页不同；2 更长（多了 \r\n）也更确信 → 应合并成 2
    mk(ClauseCategory.disqualification, "未按招标文件要求提交投标保证金的，其投标无效。", 12, 0.90),
    mk(ClauseCategory.disqualification, "未按招标文件要求提交投标保证金的，其\r\n投标无效。", 23, 0.95),
    # 3：同类，但说的是另一件事 → 不该合并
    mk(ClauseCategory.disqualification, "投标报价超过最高限价的，其投标无效。", 30, 0.90),
    # 4：和 1 字面像，但类别不同 → 不该合并
    mk(ClauseCategory.format, "投标保证金应按招标文件要求单独密封。", 12, 0.85),
    # 5：完全无关
    mk(ClauseCategory.scoring, "价格分采用低价优先法计算。", 40, 0.80),
]

print(f"输入 {len(items)} 条")
out = dedupe(items)
print(f"输出 {len(out)} 条\n")

for c in out:
    print(f"  {c.category.value:16} p{c.page_no:3} conf={c.confidence:.2f}  {c.quote[:36]!r}")

print("\n=== 相似度实测（阈值 90）===")
print(f"  {'':16} {'压空格':>8} {'抹空白':>8}   判定")
for label, a, b in [
    ("同一句+换行噪音", items[0].quote, items[1].quote),
    ("同类不同要求", items[0].quote, items[2].quote),
    ("跨类别", items[0].quote, items[3].quote),
    ("完全无关", items[0].quote, items[4].quote),
]:
    # 两列对照：这就是 squash() 存在的理由
    old = fuzz.token_set_ratio(normalize_text(a), normalize_text(b))
    new = fuzz.token_set_ratio(squash(a), squash(b))
    print(f"  {label:16} {old:8.1f} {new:8.1f}   {'合并' if new > 90 else '保留'}")

print()
check("条数 5→4", len(out), 4)
merged = [c for c in out if c.page_no == 23]
check("合并后只留 1 条 p23", len(merged), 1)
check("保留更长的那条", merged[0].quote if merged else None, items[1].quote)
check("confidence 取高", merged[0].confidence if merged else None, 0.95)
check("p12 的废标条已被合并掉", [c.page_no for c in out if c.category is ClauseCategory.disqualification], [23, 30])
check("空列表进空列表出", dedupe([]), [])

print()
if fails:
    print(f"失败 {len(fails)} 项: {fails}")
    raise SystemExit(1)
print("全部通过")
