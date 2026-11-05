"""验证分批结果：批数、每批字符数、估算 token。"""
from app.services.extract import BATCH_PAGES, load_page_batches, render_batch

for doc_id in (2, 5, 13):
    batches = load_page_batches(doc_id)
    if not batches:
        continue
    sizes = [len(render_batch(b)) for b in batches]
    print(f"doc {doc_id}: {sum(len(b) for b in batches)} 页 -> {len(batches)} 批（每批 {BATCH_PAGES} 页）")
    print(f"   字符/批: 最小 {min(sizes)} 最大 {max(sizes)} 平均 {sum(sizes)//len(sizes)}")
    print(f"   估算 token/批（中文约 1.6 字/token）: {max(sizes)//16*10}")

batches = load_page_batches(2)
sample = render_batch(batches[0])
print("\n--- 第 1 批的开头 200 字符 ---")
print(sample[:200])
