"""条款去重。

重复的三个来源：
1. 同一条要求在《投标人须知》和《评标办法》各写一遍；
2. 条款跨页，第 N 批和第 N+1 批都抽到了；
3. 模型自己在一批里吐了两条几乎一样的。

去重范围（今天先这么定，跨文档合并留到后面）：
只在"本次抽取结果内部"去重，不跨 document 比对。
原因是 clauses 落库是"按 document 先删再插"，跨文档比对要另写一套逻辑。
"""

from rapidfuzz import fuzz

from app.schemas.clause import ClauseCategory
from app.schemas.extraction import ExtractedClause
from app.services.normalize import squash

# 相似度阈值。90 是经验值：再低会把"应当提供营业执照"和
# "应当提供资质证书"这种不同要求误合。
THRESHOLD = 90

def dedupe(items:list[ExtractedClause]) -> list[ExtractedClause]:
    """同 category 内两两比，相似的合并成一条。"""
    kept: list[ExtractedClause] = []
    # category -> [(归一化文本, 在 kept 里的下标)]
    index : dict[ClauseCategory, list[tuple[str,int]]] = {}

    for c in items:
        norm = squash(c.quote)
        bucket = index.setdefault(c.category, [])

        dup_at = -1
        for prev_norm,pos in bucket:
            if fuzz.token_set_ratio(norm,prev_norm) > THRESHOLD:
                dup_at = pos
                break

        if dup_at<0:
            bucket.append((norm,len(kept)))
            kept.append(c)
            continue

        old = kept[dup_at]
        longer = c if len(c.quote) > len(old.quote) else old
        kept[dup_at] = longer.model_copy(
            update={
                "confidence":max(c.confidence,old.confidence)
            }
        )
    return kept