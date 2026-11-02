"""九张核心表。

Day 1 的取舍（都写在这里，免得三周后忘了为什么）：
1. 分类/状态一律用 String，不用 PG 原生 enum —— 原生 enum 改名要写迁移脚本，
   第 3 周加一种 severity 就能卡你半天。
2. 时间戳统一 DateTime(timezone=True) + server_default=now()，不靠 Python 侧生成。
3. 业务表全部带 tenant_id（doc_pages 例外，它通过 document_id 归属），
   Day 29 做多租户隔离时才不用回头改表。
4. vector(1024) 列今天只建列，不建 HNSW 索引 —— Day 8 说了，等上万条再建。
"""

from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ---------------------------------------------------------------- 租户与用户


class Tenant(TimestampMixin, Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(
        String(32), default="free", server_default="free", nullable=False
    )

    users: Mapped[list["User"]] = relationship(back_populates="tenant")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(16), default="viewer", server_default="viewer", nullable=False
    )  # owner / reviewer / viewer
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="users")


# ---------------------------------------------------------------- 项目与文件


class Tender(TimestampMixin, Base):
    """一个招标项目。tender 既是"招标文件"，也是审查的容器。"""

    __tablename__ = "tenders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    purchaser: Mapped[str | None] = mapped_column(String(200))  # 采购人
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(
        String(16), default="draft", server_default="draft", nullable=False
    )  # draft / reviewing / done

    documents: Mapped[list["Document"]] = relationship(back_populates="tender")


class Document(TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sha256", name="uq_documents_tenant_sha256"),
        Index("ix_documents_tender_kind", "tender_id", "kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    tender_id: Mapped[int] = mapped_column(
        ForeignKey("tenders.id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(String(8), nullable=False)  # tender / bid
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)  # 重复上传去重
    status: Mapped[str] = mapped_column(
        String(16), default="uploaded", server_default="uploaded", nullable=False
    )  # uploaded / parsing / parsed / failed
    outline: Mapped[dict[str, Any] | None] = mapped_column(JSONB)  # 章节树，Day 10 填

    tender: Mapped["Tender"] = relationship(back_populates="documents")


class DocPage(Base):
    """按页存原文。所有页码引用的源头就是这张表。"""

    __tablename__ = "doc_pages"
    __table_args__ = (UniqueConstraint("document_id", "page_no", name="uq_doc_pages_doc_page"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    page_no: Mapped[int] = mapped_column(Integer, nullable=False)  # PDF 索引页，从 1 开始
    text: Mapped[str] = mapped_column(Text, default="", server_default="", nullable=False)
    ocr_used: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    image_key: Mapped[str | None] = mapped_column(String(512))  # 扫描页的 PNG 存储 key
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ---------------------------------------------------------------- 条款与切片


class Clause(TimestampMixin, Base):
    """从招标文件里抽出来的条款，是审查的基本单位。"""

    __tablename__ = "clauses"
    __table_args__ = (Index("ix_clauses_tender_category", "tender_id", "category"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    tender_id: Mapped[int] = mapped_column(
        ForeignKey("tenders.id", ondelete="CASCADE"), index=True, nullable=False
    )
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    page_no: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(24), nullable=False)
    # qualification / disqualification / format / submission / scoring
    clause_no: Mapped[str | None] = mapped_column(String(32))  # "3.2.1"，没有就 NULL
    text: Mapped[str] = mapped_column(Text, nullable=False)  # 规范表述
    quote: Mapped[str] = mapped_column(Text, nullable=False)  # 逐字原文，报告里引用
    normalized: Mapped[str | None] = mapped_column(Text)  # 归一化后用于去重
    confidence: Mapped[float] = mapped_column(
        Float, default=0.0, server_default="0", nullable=False
    )


class Segment(TimestampMixin, Base):
    """投标文件的检索切片。第 2 周的主力表。"""

    __tablename__ = "segments"
    __table_args__ = (
        Index("ix_segments_tender_document", "tender_id", "document_id"),
        # HNSW 索引 Day 8 再加：数据量小的时候建了只会拖慢插入
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    tender_id: Mapped[int] = mapped_column(
        ForeignKey("tenders.id", ondelete="CASCADE"), index=True, nullable=False
    )
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    page_no: Mapped[int] = mapped_column(Integer, nullable=False)
    section_path: Mapped[str | None] = mapped_column(String(512))  # "第三章 资格证明文件/3.2 资质证书"
    order_no: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024))  # bge-m3


# ---------------------------------------------------------------- 判定与任务


class Finding(TimestampMixin, Base):
    """一条条款的判定结果。报告就是这张表的渲染。"""

    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    tender_id: Mapped[int] = mapped_column(
        ForeignKey("tenders.id", ondelete="CASCADE"), index=True, nullable=False
    )
    clause_id: Mapped[int] = mapped_column(
        ForeignKey("clauses.id", ondelete="CASCADE"), index=True, nullable=False
    )
    verdict: Mapped[str] = mapped_column(String(16), nullable=False)  # met / not_met / needs_review
    evidence_quote: Mapped[str | None] = mapped_column(Text)  # 必须能在 segments.text 里查到
    evidence_page: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float] = mapped_column(
        Float, default=0.0, server_default="0", nullable=False
    )
    reason: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(
        String(8), default="medium", server_default="medium", nullable=False
    )  # high / medium / low
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    trace: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)  # Agent 每轮决策，Day 12
    review_trace: Mapped[dict[str, Any] | None] = mapped_column(JSONB)  # 对抗复核轨迹，Day 16


class Job(TimestampMixin, Base):
    """异步任务。前端轮询的就是它。"""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)  # parse_document / check_tender
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(16), default="queued", server_default="queued", index=True, nullable=False
    )  # queued / running / done / failed
    progress: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    error: Mapped[str | None] = mapped_column(Text)


__all__ = [
    "Base",
    "Tenant",
    "User",
    "Tender",
    "Document",
    "DocPage",
    "Clause",
    "Segment",
    "Finding",
    "Job",
]
