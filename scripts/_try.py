import traceback
from pathlib import Path
from app.services.pdf import parse_pdf

try:
    n = parse_pdf(1, Path("data/samples/北京-2025-丰台法院电子卷宗-文字版.pdf"))
    print("返回页数:", n)
except Exception:
    traceback.print_exc()
