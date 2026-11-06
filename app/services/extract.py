"""把 doc_pages 的文本切成批次，拼成带页码标记的字符串。

今天只做「切」和「拼」，不调模型——这样这层可以单独验证，
不用烧 token 也能确认分页和页码标记是对的。
"""
import json
import urllib.request

from app.core.config import settings
from app.schemas.extraction import ClauseList, ExtractedClause
from app.services.prompts import SYSTEM_PROMPT
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

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

def _chat(message:list[dict]) -> str:
    """发一次请求，返回模型输出的原始字符串。"""
    body = json.dumps(
        {
            "model":MODEL,
            "messages":message,
            "temperature":0,
            "response_format": {"type":"json_object"},
        },
        ensure_ascii=False,

    ).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req,timeout=120) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"]

def extract_batch(batch:list[dict],retry: int = 1) -> list[ExtractedClause]:
    """从一批页面里抽条款。"""
    batch_text = render_batch(batch)
    valid_pages = {p["page_no"] for p in batch }

    messages:list[dict] = [
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":batch_text},
    ]

    last_err: Exception | None = None
    for _ in range(retry + 1):
        raw = _chat(messages)
        try:
            parsed = ClauseList.model_validate_json(raw)
        except Exception as e:
            last_err = e
            messages.append({"role":"assistant","content":raw})
            messages.append({
                "role":"user",
                "content": f"上面的输出不符合要求：{e}\n请只输出修正后的 JSON 对象，不要任何解释。",
            })
            continue

        return [c for c in parsed.clauses if c.page_no in valid_pages]
    raise ValueError(f"重试 {retry} 次仍未通过校验：{last_err}")
