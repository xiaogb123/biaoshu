# 样本文件来源

第 1 周的开发样本。评测集必须用真实项目文件，所以每一份都记录来路——
第 2 周要 50 份，第 4 周出评测报告，到时候"这份数据哪来的"是要能答的。

| 文件名 | 项目 | 页数 | 类型 | 来源 |
|---|---|---|---|---|
| 河北-2026-市政设施管护-文字版 | 涿州高新区市政设施管护 | 75 | 文字版 | http://ccgp-hebei.gov.cn/BidDingAnncFiles/cc8af0ce-d426-495b-83b1-d096877c0b92.pdf |
| 陕西-2024-财政厅物业管理-文字版 | 陕西省财政厅 2024 年物业管理服务 | 85 | 文字版 | http://www.ccgp-shaanxi.gov.cn/gpx-bid-file/ZF_JGBM_000003/610001/2023/11/17/8a69c5a18b676330018b92fbba9e097d/gpx-template/8a69c0d08b02824c018bdade382d2663.pdf |
| 北京-2025-丰台法院电子卷宗-文字版 | 丰台区人民法院电子卷宗随案生成 | 115 | 文字版 | http://www.ccgp-beijing.gov.cn/content_file/xxgg/sjxxgg/zbggs/2025/4/ac2aa125c7464fd39a18962f8d9dc6cf.pdf |
| 北京-2025-公园中心信息化-文字版 | 北京市公园管理中心信息化能力 | 79 | 文字版 | http://www.ccgp-beijing.gov.cn/content_file/xxgg/sjxxgg/zbggs/2025/11/13cee2f4a06a46129c17bef836274a40.pdf |
| 贵州-2025-安顺区域医疗中心-文字版 | 安顺市省级区域医疗中心 | 63 | 文字版 | https://ggzy.guizhou.gov.cn/hallweb/hall/attach/nosession/download?attachId=8a8bb7459768d6f20197a64971e95854 |

**还缺**：一份扫描件（图片型 PDF）。第 3 天的 OCR 兜底需要一个真实样本，
否则 `need_ocr` 的判断没有东西可测。

## 找数据的一条结论

全国平台（ccgp.gov.cn）的公告页**基本不挂招标文件附件**，翻 40 条公告只出 1 份。
真正的文件在省级站点的直链上（河北 ccgp-hebei、陕西 ccgp-shaanxi、
北京 ccgp-beijing、贵州 ggzy.guizhou）。

所以下次找文件的正确姿势不是"点公告看附件"，而是直接搜 PDF 直链。
