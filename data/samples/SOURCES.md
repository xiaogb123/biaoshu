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
## 第三批（2026-11-09，投标文件 + 广东监理）

| 文件名 | 项目 | 页数 | 类型 | 来源 |
|---|---|---|---|---|
| 广东-2025-电白园区监理-文字版 | 茂名市电白产业转移工业园扩园及基础设施配套项目（二期）监理 | 115 | 文字版（104/115 页有文字层，6.2 万字） | https://ygp.gdzwfw.gov.cn/ggzy-portal/base/sys-file/download/v3/8a0342b0-8665-4dd9-abb5-6ed27aad5320--3C14 |
| 广东-2026-茂名园区监理-投标-扫描版 | 茂名国家高新区化工园区基础设施配套项目(二期)--道路及市政管线建设工程监理【投标文件】 | 94 | **扫描为主**（23/94 页有文字层，1.3 万字） | https://www.gdgczb.com/jydt/003005/20261107/tbgs-3cd98c1a-c18c-4c8d-a8bb-530677bc79e7.html |

**累计 13 份**：河北 4 / 陕西 3 / 北京 2 / 贵州 1 / 四川 1 / 广东 2，覆盖 6 个省。
**投标文件只有 1 份**（广东-2026-茂名园区监理-投标-扫描版），且以扫描件为主。

### 投标文件为什么难找（实测结论）

1. **政府采购不公开投标文件**。投标文件属于投标人的商业文件，招标公告只挂招标文件。
2. **工程建设类有"投标文件公示"制度**，广东省招投标平台（gdgczb.com）确实公开中标候选人的投标文件，但：
   - 施工类：160 页 / 110 MB / 前 40 页只有 1~4 页有文字层，**纯扫描件**，超上传上限；
   - 监理类：94 页 / 15 MB / 24% 有文字层，**能上传**，但文字量只有 1.3 万字，做检索评测不够。
3. **gdgczb 的列表页 403**（`/jydt/003005/`，带 Referer 也不行），只能靠搜索引擎索引到具体公示页。
4. **gdgczb 的招标公告页（`/jydt/003001/`）不挂附件**，招标文件拿不到配对的。
5. 广东省政务云（ygp.gdzwfw.gov.cn）有招标文件直链，是这条路里唯一拿到**文字版**的入口。

### 下一步数据策略

- 招标文件侧已经够用（13 份、6 个省）；
- 投标文件侧缺"文字版 + 体量适中"的样本，短期内靠：
  (a) 从招标文件的「第X章 投标文件格式」章节里切出骨架；
  (b) 自造带缺陷的投标文件（评测集反正要人工标注，造的反而是唯一有标准答案的）。


