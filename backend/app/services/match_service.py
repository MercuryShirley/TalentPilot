import re


def parse_csv_tags(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _tokenize(text: str) -> set[str]:
    chunks = re.split(r"[^\w\u4e00-\u9fa5]+", text.lower())
    return {c for c in chunks if c}


def _coverage_ratio(user_tokens: set[str], club_tokens: set[str]) -> float:
    if not user_tokens:
        return 0.0
    return len(user_tokens & club_tokens) / len(user_tokens)


def _expand_interest_tokens(interests: list[str]) -> set[str]:
    mapping = {
        "科技": ["科技", "技术", "ai", "数据", "算法", "编程", "创新", "学术"],
        "音乐": ["音乐", "乐队", "声乐", "演艺"],
        "公益": ["公益", "志愿", "支教", "环保", "救助"],
        "体育": ["体育", "竞技", "飞盘", "登山", "乒乓", "击剑", "滑板"],
        "传媒": ["传媒", "视频", "播音", "主持", "内容", "融媒体"],
        "传统文化": ["传统", "文化", "国学", "汉服", "礼仪"],
        "推理": ["推理", "谜题", "剧本", "逻辑", "解谜"],
        "艺术创作": ["艺术", "创作", "戏剧", "摄影", "影评", "编导"],
        "社交": ["社交", "沟通", "外联", "交流", "活动"],
    }

    tokens: set[str] = set()
    for interest in interests:
        tokens.update(_tokenize(interest))
        tokens.update(mapping.get(interest, []))
    return tokens


def _expand_skill_tokens(skills: list[str]) -> set[str]:
    mapping = {
        "沟通": ["沟通", "外联", "主持", "谈判", "表达"],
        "组织": ["组织", "统筹", "执行", "会务", "协调"],
        "写作": ["写作", "文案", "影评", "剧本", "研报"],
        "策划": ["策划", "运营", "活动", "方案"],
        "编程": ["编程", "算法", "数据", "python", "开发", "技术"],
        "设计": ["设计", "视觉", "审美", "创意"],
        "表达": ["表达", "演讲", "播音", "口才"],
        "研究": ["研究", "分析", "调研", "学术", "行研"],
        "执行": ["执行", "落地", "推进", "纪律"],
    }

    tokens: set[str] = set()
    for skill in skills:
        tokens.update(_tokenize(skill))
        tokens.update(mapping.get(skill, []))
    return tokens


def _major_bonus(major_category: str, club_category: str, club_text: str) -> float:
    major = major_category.strip()
    text = f"{club_category} {club_text}"

    if major in ["工科", "理科"] and any(key in text for key in ["学术科技", "技术", "算法", "数据", "创新"]):
        return 8.0
    if major == "商科" and any(key in text for key in ["金融", "咨询", "商业", "行研", "战略"]):
        return 8.0
    if major == "文科" and any(key in text for key in ["文化艺术", "传媒", "写作", "口才", "辩论"]):
        return 8.0
    if major == "艺术" and any(key in text for key in ["文化艺术", "音乐", "戏剧", "摄影", "舞蹈"]):
        return 8.0
    if major == "医学" and any(key in text for key in ["志愿公益", "救助", "心理", "健康"]):
        return 8.0

    return 0.0


def _personality_score(tags: set[str]) -> float:
    score = 0.0
    if "外向" in tags:
        score += 2.0
    if "认真细致" in tags:
        score += 2.0
    if "计划导向" in tags:
        score += 1.5
    if "天马行空" in tags:
        score += 1.5
    if "灵活应变" in tags:
        score += 1.5
    return score


def compute_match_details(profile: dict, club: dict) -> dict:
    interests = profile.get("interests", [])
    skills = profile.get("skills", [])
    personality_tags = set(profile.get("personality_tags", []))
    weekly_hours = int(profile.get("weekly_hours", 0))
    major_category = profile.get("major_category", "")

    club_text = " ".join(
        club.get("preferred_tags", [])
        + club.get("required_skills", [])
        + [club.get("name", ""), club.get("category", ""), club.get("intro", "")]
    )
    club_tokens = _tokenize(club_text)

    interest_tokens = _expand_interest_tokens(interests)
    skill_tokens = _expand_skill_tokens(skills)

    tag_score = 52 * _coverage_ratio(interest_tokens, club_tokens)
    skill_score = 28 * _coverage_ratio(skill_tokens, club_tokens)

    min_h = int(club.get("weekly_hours_min", 0))
    max_h = int(club.get("weekly_hours_max", 99))
    if min_h <= weekly_hours <= max_h:
        time_score = 6.0
    else:
        gap = min(abs(weekly_hours - min_h), abs(weekly_hours - max_h))
        time_score = max(0.0, 6.0 - gap)

    personality_bonus = _personality_score(personality_tags)
    major_fit_bonus = _major_bonus(major_category, club.get("category", ""), club_text)

    total = round(min(100.0, tag_score + skill_score + time_score + personality_bonus + major_fit_bonus), 2)
    return {"score": total}
