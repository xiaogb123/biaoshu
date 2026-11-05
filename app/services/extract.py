"""把 doc_pages 的文本切成批次，拼成带页码标记的字符串。

今天只做「切」和「拼」，不调模型——这样这层可以单独验证，
不用烧 token 也能确认分页和页码标记是对的。
"""

from sqlalchemy import select

from app.db.models import DocPage
from app.db.session import SessionLocal

# 每批几页。8 页约 6k token，在 DeepSeek-V3 的 64K 里留足余量。
BATCH_PAGES = 8


def load_page_batches(document_id: int, batch_size: int = BATCH_PAGES) -> list[list[dict]]:
    """读出该文档的所有页，按 batch_size 切成若干批。

    返回 [[{page_no, text}, ...], ...]，外层是批，内层是页。
    """
    with SessionLocal() as db:
        rows = db.execute(
            select(DocPage.page_no, DocPage.text)
            .where(DocPage.document_id == document_id)
            .order_by(DocPage.page_no)
        ).all()

    pages = [{"page_no": r.page_no, "text": r.text or ""} for r in rows]
    return [pages[i : i + batch_size] for i in range(0, len(pages), batch_size)]


def render_batch(batch: list[dict]) -> str:
    """把一批页拼成一段文本，每页前面加 <PAGE n> 标记。

    页码标记是整个项目页码准确率的命脉：模型看不到 XML 结构，
    只能靠这个显式的分隔符知道"下面这段是第几页"。
    """
    parts: list[str] = []
    for page in batch:
        parts.append(f"<PAGE {page['page_no']}>")
        parts.append(page["text"])
    return "\n".join(parts)
