from rapidocr_onnxruntime import RapidOCR

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = RapidOCR()
    return _engine

def ocr_image(img:bytes,min_score: float = 0.5) -> str:
    result,_= get_engine()(img)
    if not result:
        return ""
    # 注意：RapidOCR 返回的置信度是字符串，不是 float
    lines = [item[1] for item in result if float(item[2]) >= min_score]
    return "\n".join(lines)

