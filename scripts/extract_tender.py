"""一键抽取：读库 → 分批抽 → 归一化 → 去重 → 落库。

用法：
    python -m scripts.extract_tender        # 默认 doc 2
    python -m scripts.extract_tender 7      # 指定 doc
"""

import sys
import time
from collections import Counter

from app.services.dedupe import dedupe
from app.services.extract import extract_batch, load_page_batches

from app.services.persist import prepare, save_clauses

def run(doc_id:int) -> None:
    batches = load_page_batches(doc_id)
    pages = sum(len(b) for b in batches)
    print(f"文档 {doc_id}: {len(batches)} 批,{pages}页\n")

    t0 = time.time()
    raw = []
    for i,b in enumerate(batches,1):
        cs = extract_batch(b)
        raw.extend(cs)
        print(f"  [{i:2}/{len(batches)}] p{b[0]['page_no']:3}-{b[-1]['page_no']:3}: {len(cs):3} 条")
    t_extract = time.time() - t0

    prepared = prepare(raw)
    unique = dedupe(prepared)
    merged = len(prepared) - len(unique)

    t1 = time.time()
    n = save_clauses(doc_id,unique)
    t_write = time.time() - t1

    print(f"\n抽取   {len(raw):4} 条   {t_extract:5.1f}s")
    print(f"去重后 {len(unique):4} 条   合并掉 {merged} 条   保留率 {len(unique) * 100 // max(1, len(prepared))}%")
    print(f"入库   {n:4} 条   {t_write:5.1f}s")
    print("\n分类分布:", dict(Counter(c.category.value for c in unique).most_common()))


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
