from datetime import datetime, timedelta

from app.models import Club, ClubFAQ, ClubActivityPost


def seed_data(db):
    clubs = db.query(Club).order_by(Club.id.asc()).all()
    if not clubs:
        clubs = [
            Club(
                name="青年志愿者协会",
                category="公益",
                intro="组织校内外志愿服务活动，适合有同理心与执行力的同学。",
                weekly_hours_min=2,
                weekly_hours_max=6,
                required_skills="沟通,组织",
                preferred_tags="公益,社交,执行",
            ),
            Club(
                name="吉他社",
                category="文艺",
                intro="围绕音乐演出、活动策划与校园文化建设展开。",
                weekly_hours_min=3,
                weekly_hours_max=8,
                required_skills="沟通,策划",
                preferred_tags="音乐,社交,创意",
            ),
            Club(
                name="AI创新社",
                category="科技",
                intro="开展AI应用实践、黑客松与产品共创。",
                weekly_hours_min=4,
                weekly_hours_max=10,
                required_skills="编程,学习能力",
                preferred_tags="技术,创新,实践",
            ),
        ]
        db.add_all(clubs)
        db.flush()

    if db.query(ClubFAQ).count() == 0 and len(clubs) >= 3:
        faqs = [
            ClubFAQ(club_id=clubs[0].id, question="每周要投入多久", answer="通常每周2-6小时，按项目排班。"),
            ClubFAQ(club_id=clubs[1].id, question="不会乐器可以加入吗", answer="可以，公关和策划方向不要求乐器基础。"),
            ClubFAQ(club_id=clubs[2].id, question="零基础可以加入吗", answer="可以，我们有新手训练营和组队机制。"),
        ]
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
