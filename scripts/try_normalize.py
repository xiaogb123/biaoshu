"""归一化 / 编号提取 / 分类兜底的自测。

纯函数，不连数据库、不调模型，跑完不到 1 秒。
改完 normalize.py 就重跑这个，别靠眼睛看。
"""

from app.schemas.clause import ClauseCategory
from app.services.normalize import extract_clause_no, fix_category, normalize_text

fails: list[str] = []


def check(label: str, got, want) -> None:
    ok = got == want
    mark = "OK " if ok else "BAD"
    print(f"[{mark}] {label:24} got={got!r}")
    if not ok:
        print(f"       {'':24} want={want!r}")
        fails.append(label)


print("=== 1. normalize_text ===")
check("全角括号+全角数字", normalize_text("（１）投标人"), "(1)投标人")
check("换行压成空格", normalize_text("并视\n情况追究"), "并视 情况追究")
check("去首尾空白", normalize_text("  多余空白   "), "多余空白")
check("全角字母数字", normalize_text("Ａ４打印纸"), "A4打印纸")
check("空字符串", normalize_text(""), "")
check("只有空白", normalize_text("  \n\t "), "")

print("\n=== 2. extract_clause_no ===")
check("点分编号", extract_clause_no("14.5 投标人应…"), "14.5")
check("多级点分", extract_clause_no("12.3.1 上述材料"), "12.3.1")
check("第X章", extract_clause_no("第三章 评标办法"), "第三章")
check("第X条", extract_clause_no("第5条 投标人应…"), "第5条")
check("金额不是编号", extract_clause_no("1000.5 万元以下的为中型企业"), None)
check("无编号", extract_clause_no("投标人应当具备…"), None)
check("编号在第二行不算", extract_clause_no("正文开头\n14.5 后续"), None)
check("全角点分编号", extract_clause_no("１２．５ 投标人应…"), "12.5")
check("PDF 的 \\r\\n 噪音", extract_clause_no("14.5\r\n投标人应…"), "14.5")

print("\n=== 3. fix_category ===")
check(
    "格式→废标",
    fix_category(ClauseCategory.format, "未按要求密封的，其投标无效。"),
    ClauseCategory.disqualification,
)
check(
    "纯格式不动",
    fix_category(ClauseCategory.format, "投标文件应装订成册。"),
    ClauseCategory.format,
)
check(
    "已是废标不动",
    fix_category(ClauseCategory.disqualification, "投标人应提供营业执照。"),
    ClauseCategory.disqualification,
)
check(
    "评分不动",
    fix_category(ClauseCategory.scoring, "价格分 30 分。"),
    ClauseCategory.scoring,
)

print()
if fails:
    print(f"失败 {len(fails)} 项: {fails}")
    raise SystemExit(1)
print("全部通过")
