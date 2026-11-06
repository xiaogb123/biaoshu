"""校验抽取结果：全文档跑一遍，量三个数。

A 整批命中    quote 在这 8 页文本里吗   → 模型有没有「照抄」
B 本页严格    quote 在它自己标的那页吗   → 页码对不对
C 本页去空白  抹掉所有空白后再比         → 页码对不对（排除换行差异）
"""
import re
import time
from collections import Counter

from app.services.extract import extract_batch, load_page_batches, render_batch

WS = re.compile(r"\s+")


def squeeze(s: str) -> str:
    """删掉所有空白字符，用于忽略换行位置差异。"""
    return WS.sub("", s)


def rate(n: int, d: int) -> str:
    return f"{n}/{d} ({n * 100 // max(1, d)}%)"


doc_id = 2
batches = load_page_batches(doc_id)
print(f"文档 {doc_id}: {len(batches)} 批, {sum(len(b) for b in batches)} 页\n")

t0 = time.time()
total = a_ok = b_ok = 0
soft, bad = [], []
cats = Counter()

for i, batch in enumerate(batches, 1):
    page_text = {p["page_no"]: p["text"] for p in batch}
    batch_text = render_batch(batch)

    clauses = extract_batch(batch)
    total += len(clauses)

    for c in clauses:
        cats[c.category.value] += 1

        if not c.quote.strip():
            bad.append(c)          # 空 quote 会让 in 永远成立，必须排除
            continue

        if c.quote in batch_text:
            a_ok += 1

        own = page_text.get(c.page_no, "")
        if c.quote in own:
            b_ok += 1
        elif squeeze(c.quote) in squeeze(own):
            soft.append(c)         # 页码对，只是换行位置偏了
        else:
            bad.append(c)          # 页码真错

    print(f"[{i:2}/{len(batches)}] {len(clauses):3} 条")

print(f"\n合计 {total} 条, 耗时 {time.time() - t0:.0f}s\n")

print("A 严格命中(受PDF折行干扰,仅参考):", rate(a_ok, total))
print("B 去空白命中(真实忠实度)      :", rate(b_ok, total))
print("C 本页去空白:", rate(b_ok + len(soft), total))
print(f"  ├ 仅换行不同: {len(soft)} 条")
print(f"  └ 页码真错  : {len(bad)} 条")

print("\n分类分布:")
for cat, n in cats.most_common():
    print(f"  {cat:18} {n}")

if bad:
    print("\n页码对不上的前 10 条:")
    for c in bad[:10]:
        print(f"  p{c.page_no} {c.category.value}: {c.quote[:60]!r}")