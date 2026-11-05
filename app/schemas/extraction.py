"""抽取结果的数据结构。

这里定义的是「LLM 必须返回成什么样」，不是「数据库长什么样」。
两者分开的好处：换个模型、换个 prompt，这个文件不用动；
数据库加字段，这个文件也不用动。
"""

from pydantic import BaseModel, Field

from app.schemas.clause import ClauseCategory


class ExtractedClause(BaseModel):
    """一条被抽出来的条款。"""

    category: ClauseCategory
    clause_no: str | None = Field(None, description="如 3.2.1；没有就 null")
    text: str = Field(description="条款的规范表述，可以压缩，但不能加原文没有的内容")
    quote: str = Field(description="逐字摘自原文，一个字都不能改")
    page_no: int = Field(description="该条实际所在的 PDF 页码，从 1 开始")
    confidence: float = Field(ge=0, le=1)


class ClauseList(BaseModel):
    """一批页面的抽取结果。包一层是为了让模型输出固定的顶层结构。"""

    clauses: list[ExtractedClause]
