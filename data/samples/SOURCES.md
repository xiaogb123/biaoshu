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

## 第二批（2026-11-09 补充，6 份）

| 文件名 | 项目 | 页数 | 类型 | 来源 |
|---|---|---|---|---|
| 河北-2023-雄安施工统筹-文字版 | 2023 年度雄安新区建设工程项目施工统筹 | 82 | 文字版 | http://www.ccgp-hebei.gov.cn/BidWinAnncFiles/54c733df-4874-44fb-826d-ddab42b3fef7.pdf |
| 河北-2024-唐县设备图书-文字版 | 唐县薄弱环节能力提升设备及图书购置 | 57 | 文字版 | http://ccgp-hebei.gov.cn/BidWinAnncFiles/ecb3a071-ee27-4bd2-a1f0-6034fa96dcce.pdf |
| 河北-2025-保定妇幼试剂采购-文字版 | 保定市妇幼保健院 2025 年消除母婴传播试剂采购 | 88 | 文字版（"双盲"评审示范文本） | http://www.ccgp-hebei.gov.cn/BidWinAnncFiles/bf712738-1e23-a1ac-4b29-42082a82c881.pdf |
| 陕西-2024-西安远东一中改造-文字版 | 西安市远东第一中学校园改造工程 | 119 | 文字版 | http://www.ccgp-shaanxi.gov.cn/gpx-bid-file/ZF_JGBM_000003/610104/2024/10/16/8a69c85191b241d9019293500315283c/gpx-template/8a69c25092d1e2940193054de6c94e99.pdf |
| 陕西-2025-未央市政桥梁检测-文字版 | 2024 年未央区市政道路桥梁安全检测项目 | 91 | 文字版 | https://www.ccgp-shaanxi.gov.cn/gpx-bid-file/ZF_JGBM_000003/zone/2025/1/12/project/gpx-template/8a69c5e496f5255e01971ed6bafd44d1.pdf |
| 四川-2025-大竹县食堂食材-采购需求 | 大竹县 2025 年学校食堂大宗食材采购 | 15 | 文字版（采购需求书，非招标文件） | https://gpx.ccgp-sichuan.gov.cn/gpx-bid-file/ZF_JGBM_000008/zone/2024/12/15/project/gpx-template/8a69ced7950238660195024485892a68.pdf |

**累计 11 份**（fixture 不算）：河北 4 / 陕西 3 / 北京 2 / 贵州 1 / 四川 1，覆盖 5 个省。

### 第二批踩到的三个坑

1. 陕西的直链带 `?accessCode=...`，**必须整条保留**，去掉 query 参数会 403。
2. 四川的直链**必须走 https 并带 Referer**，少了 Referer 返回 502 网关错误：
   `Invoke-WebRequest -Uri <https地址> -Headers @{Referer='http://www.ccgp-sichuan.gov.cn/'}`
3. 山东（sdgp.sdcz.gov.cn）的 pdf 直链现在返回一段 HTML，用 JS 跳转到
   https://www.ccgp-shandong.gov.cn ，命令行拿不到真文件，暂时放弃。

