from datetime import datetime, timedelta

from app.models import Club, ClubFAQ, ClubActivityPost


CLUB_SEED_DATA = [
    {"name": "青年志愿者协会", "category": "公益", "intro": "组织校内外志愿服务活动，适合有同理心与执行力的同学。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "沟通,组织", "preferred_tags": "公益,社交,执行"},
    {"name": "吉他社", "category": "文艺", "intro": "围绕音乐演出、活动策划与校园文化建设展开。", "weekly_hours_min": 3, "weekly_hours_max": 8, "required_skills": "沟通,策划", "preferred_tags": "音乐,社交,创意"},
    {"name": "AI创新社", "category": "科技", "intro": "开展AI应用实践、黑客松与产品共创。", "weekly_hours_min": 4, "weekly_hours_max": 10, "required_skills": "编程,研究", "preferred_tags": "技术,创新,实践"},
    {"name": "辩论与演讲社", "category": "文艺", "intro": "以辩题训练与公众表达提升逻辑与口才。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "表达,沟通", "preferred_tags": "推理,社交,成长"},
    {"name": "摄影与视觉社", "category": "文艺", "intro": "进行摄影采风、后期修图和展览策划。", "weekly_hours_min": 2, "weekly_hours_max": 7, "required_skills": "设计,执行", "preferred_tags": "艺术创作,传媒,审美"},
    {"name": "舞蹈联盟", "category": "文艺", "intro": "组织街舞、爵士与舞台表演训练。", "weekly_hours_min": 3, "weekly_hours_max": 9, "required_skills": "执行,表达", "preferred_tags": "音乐,社交,舞台"},
    {"name": "话剧社", "category": "文艺", "intro": "开展剧本创作、排练与校园演出。", "weekly_hours_min": 3, "weekly_hours_max": 8, "required_skills": "写作,表达", "preferred_tags": "艺术创作,社交,协作"},
    {"name": "合唱团", "category": "文艺", "intro": "每周排练与校级演出，重视团队配合。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "沟通,执行", "preferred_tags": "音乐,社交,合作"},
    {"name": "电影评论社", "category": "文艺", "intro": "观影、影评写作与主题沙龙讨论。", "weekly_hours_min": 2, "weekly_hours_max": 5, "required_skills": "写作,研究", "preferred_tags": "艺术创作,推理,表达"},
    {"name": "国风文化社", "category": "传统文化", "intro": "策划汉服、礼仪与传统节庆活动。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "组织,策划", "preferred_tags": "传统文化,社交,传播"},
    {"name": "书法与篆刻社", "category": "传统文化", "intro": "开展书法训练、篆刻体验与展览。", "weekly_hours_min": 2, "weekly_hours_max": 5, "required_skills": "执行,设计", "preferred_tags": "传统文化,艺术创作,专注"},
    {"name": "国学研习社", "category": "传统文化", "intro": "经典阅读、主题导读与公开分享。", "weekly_hours_min": 2, "weekly_hours_max": 5, "required_skills": "研究,写作", "preferred_tags": "传统文化,推理,表达"},
    {"name": "历史探索社", "category": "传统文化", "intro": "历史专题研究与博物馆实践活动。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "研究,组织", "preferred_tags": "传统文化,学术,探究"},
    {"name": "创新创业协会", "category": "科技", "intro": "面向创业项目孵化与商业路演。", "weekly_hours_min": 3, "weekly_hours_max": 9, "required_skills": "策划,沟通", "preferred_tags": "科技,创新,执行"},
    {"name": "程序设计俱乐部", "category": "科技", "intro": "算法训练、工程实战与竞赛交流。", "weekly_hours_min": 4, "weekly_hours_max": 10, "required_skills": "编程,研究", "preferred_tags": "科技,推理,学习"},
    {"name": "机器人社", "category": "科技", "intro": "机器人结构设计、控制与比赛实训。", "weekly_hours_min": 4, "weekly_hours_max": 10, "required_skills": "编程,组织", "preferred_tags": "科技,创新,实践"},
    {"name": "数据科学社", "category": "科技", "intro": "做数据分析、可视化与建模项目。", "weekly_hours_min": 3, "weekly_hours_max": 9, "required_skills": "编程,研究", "preferred_tags": "科技,推理,实践"},
    {"name": "网络安全社", "category": "科技", "intro": "安全攻防训练与网络风险科普。", "weekly_hours_min": 3, "weekly_hours_max": 8, "required_skills": "编程,执行", "preferred_tags": "科技,推理,挑战"},
    {"name": "产品经理协会", "category": "科技", "intro": "从需求分析到原型设计的产品实战。", "weekly_hours_min": 3, "weekly_hours_max": 8, "required_skills": "策划,沟通", "preferred_tags": "科技,创新,组织"},
    {"name": "电竞社", "category": "体育", "intro": "组织校内电竞赛事与战术训练。", "weekly_hours_min": 2, "weekly_hours_max": 7, "required_skills": "沟通,执行", "preferred_tags": "体育,社交,竞技"},
    {"name": "篮球协会", "category": "体育", "intro": "常规训练与院系联赛组织。", "weekly_hours_min": 2, "weekly_hours_max": 7, "required_skills": "执行,组织", "preferred_tags": "体育,社交,团队"},
    {"name": "足球协会", "category": "体育", "intro": "组织训练、友谊赛与校联赛。", "weekly_hours_min": 2, "weekly_hours_max": 7, "required_skills": "执行,沟通", "preferred_tags": "体育,团队,竞技"},
    {"name": "羽毛球社", "category": "体育", "intro": "日常对练、技巧交流与比赛参与。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "执行,沟通", "preferred_tags": "体育,社交,健康"},
    {"name": "乒乓球社", "category": "体育", "intro": "技巧提升与校内友谊赛组织。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "执行,组织", "preferred_tags": "体育,社交,竞技"},
    {"name": "跑步与徒步社", "category": "体育", "intro": "晨跑打卡、城市徒步与耐力挑战。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "执行,组织", "preferred_tags": "体育,健康,社交"},
    {"name": "飞盘社", "category": "体育", "intro": "飞盘入门、战术训练与友谊赛。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "沟通,执行", "preferred_tags": "体育,社交,活力"},
    {"name": "登山社", "category": "体育", "intro": "周末登山与户外安全技能训练。", "weekly_hours_min": 2, "weekly_hours_max": 7, "required_skills": "组织,执行", "preferred_tags": "体育,探索,团队"},
    {"name": "滑板社", "category": "体育", "intro": "滑板技巧训练与街区文化交流。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "执行,表达", "preferred_tags": "体育,艺术创作,社交"},
    {"name": "融媒体中心", "category": "传媒", "intro": "负责校园新闻报道与多平台传播。", "weekly_hours_min": 3, "weekly_hours_max": 8, "required_skills": "写作,沟通", "preferred_tags": "传媒,社交,执行"},
    {"name": "新媒体运营社", "category": "传媒", "intro": "账号运营、内容策划与数据复盘。", "weekly_hours_min": 3, "weekly_hours_max": 8, "required_skills": "策划,写作", "preferred_tags": "传媒,创新,执行"},
    {"name": "播音主持社", "category": "传媒", "intro": "主持训练、配音练习与活动主持实践。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "表达,沟通", "preferred_tags": "传媒,社交,舞台"},
    {"name": "短视频创作社", "category": "传媒", "intro": "短视频选题、拍摄、剪辑全流程实践。", "weekly_hours_min": 3, "weekly_hours_max": 8, "required_skills": "设计,策划", "preferred_tags": "传媒,艺术创作,创新"},
    {"name": "校园电台", "category": "传媒", "intro": "节目策划、录制与音频内容制作。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "表达,写作", "preferred_tags": "传媒,音乐,社交"},
    {"name": "公益支教团", "category": "公益", "intro": "组织支教活动与教育资源支持。", "weekly_hours_min": 2, "weekly_hours_max": 7, "required_skills": "组织,沟通", "preferred_tags": "公益,执行,责任"},
    {"name": "环保行动社", "category": "公益", "intro": "推进校园环保倡议与实践活动。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "策划,执行", "preferred_tags": "公益,科技,行动"},
    {"name": "心理互助社", "category": "公益", "intro": "开展心理健康科普与同伴支持。", "weekly_hours_min": 2, "weekly_hours_max": 6, "required_skills": "沟通,研究", "preferred_tags": "公益,社交,关怀"},
    {"name": "红十字志愿服务队", "category": "公益", "intro": "急救培训、应急服务与公益行动。", "weekly_hours_min": 2, "weekly_hours_max": 7, "required_skills": "执行,组织", "preferred_tags": "公益,健康,责任"},
    {"name": "模拟联合国协会", "category": "学术", "intro": "围绕国际议题开展调研、写作与会议。", "weekly_hours_min": 3, "weekly_hours_max": 8, "required_skills": "研究,表达", "preferred_tags": "推理,社交,写作"},
    {"name": "商业分析社", "category": "学术", "intro": "行业分析、案例研讨与商业竞赛。", "weekly_hours_min": 3, "weekly_hours_max": 8, "required_skills": "研究,写作", "preferred_tags": "推理,科技,实践"},
    {"name": "创新设计工坊", "category": "学术", "intro": "跨学科设计思维与原型共创实践。", "weekly_hours_min": 3, "weekly_hours_max": 8, "required_skills": "设计,策划", "preferred_tags": "艺术创作,创新,科技"},
]


def seed_data(db):
    existing_clubs = db.query(Club).all()
    existing_names = {c.name for c in existing_clubs}

    missing_rows = [row for row in CLUB_SEED_DATA if row["name"] not in existing_names]
    if missing_rows:
        db.add_all([Club(**row) for row in missing_rows])
        db.flush()

    clubs_by_name = {c.name: c for c in db.query(Club).all()}

    if db.query(ClubFAQ).count() == 0:
        faq_seed = [
            ("青年志愿者协会", "每周要投入多久", "通常每周2-6小时，按项目排班。"),
            ("吉他社", "不会乐器可以加入吗", "可以，公关和策划方向不要求乐器基础。"),
            ("AI创新社", "零基础可以加入吗", "可以，我们有新手训练营和组队机制。"),
        ]
        faqs = [
            ClubFAQ(club_id=clubs_by_name[name].id, question=question, answer=answer)
            for name, question, answer in faq_seed
            if name in clubs_by_name
        ]
        if faqs:
            db.add_all(faqs)

    if db.query(ClubActivityPost).count() == 0:
        now = datetime.utcnow()
        posts = [
            ClubActivityPost(
                club_name="吉他社",
                title="草坪开放麦 · 新生专场",
                cover_url="https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=1200&q=80",
                event_time=now + timedelta(days=2, hours=11),
                location="东区草坪舞台",
                content="欢迎零基础同学来听、来唱、来玩，现场有学长学姐带你快速入门。",
                apply_link="https://example.com/guitar-open-mic",
            ),
            ClubActivityPost(
                club_name="青年志愿者协会",
                title="社区助老行动日",
                cover_url="https://images.unsplash.com/photo-1469571486292-b53601020f50?auto=format&fit=crop&w=1200&q=80",
                event_time=now + timedelta(days=4, hours=2),
                location="明德社区服务中心",
                content="参与社区探访、秩序维护和互动活动，可开具志愿服务时长证明。",
                apply_link="https://example.com/volunteer-day",
            ),
        ]
        db.add_all(posts)

    db.commit()
