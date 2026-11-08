"""文本归一化、条款编号提取、分类兜底。

三条铁律（写在这里，免得以后被人"优化"掉）：
1. quote 永远不归一化——它是报告里引用的原文证据，改了就不是证据了。
   归一化的结果只写进 clauses.normalized 列。
2. 编号从 quote 提，不从 text 提。text 是模型压缩过的，编号可能被删。
3. 分类兜底只做单向：只把"非废标"纠正成"废标"，绝不反向。
   "含废标关键词"是强信号；"不含"什么也说明不了。
"""

import re
import unicodedata

from app.schemas.clause import CATEGORY_KEYWORDS, ClauseCategory

# 连续的空白（空格、换行、制表符、全角空格）
WS = re.compile(r'\s+')
NO_WS = re.compile(r"\s+")

# 编号：第X章 / 第X条 / 第X节
NO_CHARACTER = re.compile(r"^第\s*([一二三四五六七八九十百0-9]+)\s*([条章节])")

# 编号：3.2 / 14.5 / 12.3.1 这种点分数字
# 每段限 1-2 位，避免把 "1000.5 万元" 里的数字当编号
NO_DOTTED = re.compile(r"^(\d{1,2}(?:[.．]\d{1,2}){1,3})")

def normalize_text(s:str) ->str:
    """NFKC 归一 + 空白折叠 + 去首尾空白。

       只用于去重比对和 clause_no 提取，不要拿它覆盖 quote。
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = WS.sub(" ", s)
    return s.strip()


def squash(s: str) -> str:
    """抹掉全部空白，只用于相似度比对。

    中文没有词边界，空格是 PDF 版式噪音。normalize_text 把空白压成一个空格，
    对"给人看"够用，但拿去分词会把一句话劈成两个 token，相似度虚低
    （实测同一句话仅差一个空格：ratio 97.9，token_set 只有 76.6）。
    """
    return NO_WS.sub("", normalize_text(s))


def extract_clause_no(quote:str) -> str | None:
    """从原文首行抠条款编号；抠不到返回 None。"""
    first_line = normalize_text((quote or "").split("\n",1)[0])

    m = NO_CHARACTER.match(first_line)
    if m:
        return f"第{m.group(1)}{m.group(2)}"[:32]

    m = NO_DOTTED.match(first_line)
    if m:
        return m.group(1).replace(". ",".")[:32]

    return None

DISQUALIFY_WORDS = CATEGORY_KEYWORDS[ClauseCategory.disqualification]

def fix_category(category:ClauseCategory,quote:str) -> ClauseCategory:
    """模型把废标条款标成别的类时，用关键词纠回来。"""
    if category is ClauseCategory.disqualification:
        return category

    q = normalize_text(quote)
    if any(w in q for w in DISQUALIFY_WORDS):
        return ClauseCategory.disqualification
    return category