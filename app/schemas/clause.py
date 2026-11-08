"""条款分类体系。

只做五类，别贪多——每多一类，抽取的准确率就掉一点，
第 2 周的检索和判定也要多写一套规则。

分类的边界（写清楚，否则模型会乱放）：
- qualification    资格要求：营业执照、资质证书、业绩、人员
- disqualification 废标/否决：出现"投标无效""否决其投标""不予受理"
- format           格式要求：装订、密封、签字盖章、份数
- submission       递交要求：截止时间、地点、保证金
- scoring          评分办法：分值、加分项、评审因素
"""

from enum import Enum


class ClauseCategory(str, Enum):
    qualification = "qualification"
    disqualification = "disqualification"
    format = "format"
    submission = "submission"
    scoring = "scoring"


# 关键词兜底：模型分类漂移时用它纠偏（Day 5 用）
CATEGORY_KEYWORDS: dict[ClauseCategory, tuple[str, ...]] = {
    ClauseCategory.disqualification: ("废标", "无效投标", "投标无效", "否决", "不予受理", "取消投标资格"),
    ClauseCategory.format: ("密封", "装订", "签字", "盖章", "正本", "副本", "份数"),
    ClauseCategory.submission: ("截止时间", "递交", "提交地点", "保证金", "开标"),
    ClauseCategory.scoring: ("评分", "分值", "得分", "加分", "评审因素", "权重"),
}
