"""OCR 冒烟检查：拿扫描件样本第 1 页，看能不能读出中文。

用法：python -m scripts.ocr_check
"""
import pymupdf

from app.services.ocr import ocr_image

PDF = "data/samples/_fixture-扫描件-10页.pdf"


def main() -> None:
    doc = pymupdf.open(PDF)
    pix = doc[0].get_pixmap(dpi=200)
    img = pix.tobytes("png")
    print("图片大小 KB:", len(img) // 1024)

    text = ocr_image(img)
    print("字符数:", len(text))
    print("-" * 40)
    print(text[:300])
    print("-" * 40)

    ok_len = len(text) > 20
    ok_kw = ("招标" in text) or ("项目" in text)
    print("字符数达标:", ok_len)
    print("关键词命中:", ok_kw)
    print("结论:", "通过" if (ok_len and ok_kw) else "不通过")


if __name__ == "__main__":
    main()
