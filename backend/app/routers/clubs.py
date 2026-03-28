from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Club, ClubActivityPost
from app.schemas import ClubOut, ClubChatRequest, ClubActivityPostCreate, ClubActivityPostOut
from app.services.llm_service import chat_with_club_ai, chat_with_global_ai
from app.services.match_service import parse_csv_tags

router = APIRouter(prefix="/clubs", tags=["clubs"])


@router.get("", response_model=list[ClubOut])
def list_clubs(db: Session = Depends(get_db)):
    clubs = db.query(Club).order_by(Club.id.asc()).all()
    return [
        ClubOut(
            id=c.id,
            name=c.name,
            category=c.category,
            intro=c.intro,
            weekly_hours_min=c.weekly_hours_min,
            weekly_hours_max=c.weekly_hours_max,
            required_skills=parse_csv_tags(c.required_skills),
            preferred_tags=parse_csv_tags(c.preferred_tags),
        )
        for c in clubs
    ]


@router.get("/activity-posts", response_model=list[ClubActivityPostOut])
def list_club_activities(db: Session = Depends(get_db)):
    posts = db.query(ClubActivityPost).order_by(ClubActivityPost.event_time.asc(), ClubActivityPost.id.desc()).all()
    return [
        ClubActivityPostOut(
            id=p.id,
            club_name=p.club_name,
            title=p.title,
            cover_url=p.cover_url,
            event_time=p.event_time,
            location=p.location,
            content=p.content,
            apply_link=p.apply_link,
            created_at=p.created_at,
        )
        for p in posts
    ]


@router.post("/activity-posts", response_model=ClubActivityPostOut)
def create_club_activity(payload: ClubActivityPostCreate, db: Session = Depends(get_db)):
    post = ClubActivityPost(
        club_name=payload.club_name.strip(),
        title=payload.title.strip(),
        cover_url=payload.cover_url.strip(),
        event_time=payload.event_time,
        location=payload.location.strip(),
        content=payload.content.strip(),
        apply_link=payload.apply_link.strip(),
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return ClubActivityPostOut(
        id=post.id,
        club_name=post.club_name,
        title=post.title,
        cover_url=post.cover_url,
        event_time=post.event_time,
        location=post.location,
        content=post.content,
        apply_link=post.apply_link,
        created_at=post.created_at,
    )


@router.post("/global-ask")
def ask_global_ai(payload: ClubChatRequest, db: Session = Depends(get_db)):
    messages = [{"role": m.role, "content": m.content} for m in (payload.messages or []) if m.content]
    if payload.question.strip():
        messages.append({"role": "user", "content": payload.question.strip()})

    if not messages:
        return {"answer": "你好，我是智能社团助手。你可以告诉我兴趣方向、每周时间、是否零基础，我会给你具体社团和联系建议。"}

    clubs = db.query(Club).order_by(Club.id.asc()).all()
    club_data = [
        {
            "id": c.id,
            "name": c.name,
            "category": c.category,
            "intro": c.intro,
            "required_skills": parse_csv_tags(c.required_skills),
            "preferred_tags": parse_csv_tags(c.preferred_tags),
        }
        for c in clubs
    ]

    answer = chat_with_global_ai(clubs=club_data, messages=messages)
    return {"answer": answer}


@router.get("/{club_id}", response_model=ClubOut)
def get_club(club_id: int, db: Session = Depends(get_db)):
    c = db.query(Club).filter(Club.id == club_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Club not found")
    return ClubOut(
        id=c.id,
        name=c.name,
        category=c.category,
        intro=c.intro,
        weekly_hours_min=c.weekly_hours_min,
        weekly_hours_max=c.weekly_hours_max,
        required_skills=parse_csv_tags(c.required_skills),
        preferred_tags=parse_csv_tags(c.preferred_tags),
    )


@router.post("/{club_id}/ask")
def ask_club_faq(club_id: int, payload: ClubChatRequest, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    messages = [{"role": m.role, "content": m.content} for m in (payload.messages or []) if m.content]
    if payload.question.strip():
        messages.append({"role": "user", "content": payload.question.strip()})

    if not messages:
        return {"answer": "欢迎来咨询！你可以问我面试准备、工作节奏或成长路径。"}

    answer = chat_with_club_ai(
        club_name=club.name,
        category=club.category,
        intro=club.intro,
        messages=messages,
    )
    return {"answer": answer}
