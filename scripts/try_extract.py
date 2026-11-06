"""单批抽测试：跑一批，把结果打出来人眼看。"""
import time

from app.services.extract import extract_batch, load_page_batches

batches = load_page_batches(2)
batch = batches[2]
print("本批页数:",len(batch),"页码范围：",batch[0]["page_no"],"-",batch[-1]["page_no"])

t0 = time.time()
clauses = extract_batch(batch)
print(f"耗时 {time.time() - t0:.1f}s,抽出 {len(clauses)} 条\n")

for i,c in enumerate(clauses,1):
    print(f"[{i}] {c.category.value} p{c.page_no} conf={c.confidence:.2f} no={c.clause_no}")
    print(f"    text : {c.text[:60]}")
    print(f"    quote: {c.quote[:60]}")
    print()