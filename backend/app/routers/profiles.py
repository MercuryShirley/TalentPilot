from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import StudentProfile
from app.schemas import ChatProfileRequest, ModelInfoOut, StudentProfileOut
from app.services.llm_service import assess_personality_from_cards, extract_profile_from_chat
from app.services.match_service import parse_csv_tags

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _build_personality_code(personality_choices: list[str]) -> str:
    tags = set(personality_choices)
    dim1 = "E" if "外向" in tags else "I"
    dim2 = "C" if "认真细致" in tags else "I"
    dim3 = "P" if "计划导向" in tags else "A"
    return f"{dim1}{dim2}{dim3}"


def _build_resume_summary(
    name: str,
    major_category: str,
    personality_code: str,
    personality_insight: str,
    interests: list[str],
    skills: list[str],
) -> str:
    top_interests = "、".join(interests[:3]) if interests else "待探索"
    top_skills = "、".join(skills[:3]) if skills else "待补充"
    return (
        f"{name}（{major_category}）画像：{personality_code} 型，"
        f"兴趣偏向 {top_interests}，能力偏向 {top_skills}。"
        f"{personality_insight}"
    )


@router.get("/model-info", response_model=ModelInfoOut)
def get_model_info():
    return ModelInfoOut(
        provider=settings.llm_provider,
        model=settings.llm_model,
        ready=bool(settings.llm_api_key.strip()),
    )


@router.post("/chat-extract", response_model=StudentProfileOut)
def chat_extract(payload: ChatProfileRequest, db: Session = Depends(get_db)):
    extracted = extract_profile_from_chat(payload.chat_messages) if payload.chat_messages else {}

    interests = payload.interests or extracted.get("interests", ["社交"])
    skills = payload.skills or extracted.get("skills", ["沟通"])

    if payload.assessment_answers:
        assessed = assess_personality_from_cards(payload.assessment_answers)
        personality_tags = assessed.get("personality_tags", [])
        personality_insight = assessed.get("personality_insight", "")
    else:
        personality_tags = payload.personality_choices or extracted.get("personality_tags", ["外向", "认真细致", "计划导向"])
        personality_insight = "你具备较好的社团适配潜力。"

    weekly_hours = int(payload.weekly_hours or extracted.get("weekly_hours", 4))

    personality_code = _build_personality_code(personality_tags)
    summary = _build_resume_summary(
        payload.student_name,
        payload.major_category or "未选择",
        personality_code,
        personality_insight,
        interests,
        skills,
    )

    profile = StudentProfile(
        student_name=payload.student_name,
        major=payload.major_category,
        interests=",".join(interests),
        skills=",".join(skills),
        personality_tags=",".join(personality_tags),
        weekly_hours=weekly_hours,
        chat_summary=summary,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return StudentProfileOut(
        id=profile.id,
        student_name=profile.student_name,
        major_category=profile.major,
        interests=parse_csv_tags(profile.interests),
        skills=parse_csv_tags(profile.skills),
        personality_tags=parse_csv_tags(profile.personality_tags),
        personality_code=personality_code,
        personality_insight=personality_insight,
        weekly_hours=profile.weekly_hours,
        resume_summary=profile.chat_summary,
    )


@router.get("/{profile_id}", response_model=StudentProfileOut)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    personality_tags = parse_csv_tags(profile.personality_tags)
    personality_code = _build_personality_code(personality_tags)
    return StudentProfileOut(
        id=profile.id,
        student_name=profile.student_name,
        major_category=profile.major,
        interests=parse_csv_tags(profile.interests),
        skills=parse_csv_tags(profile.skills),
        personality_tags=personality_tags,
        personality_code=personality_code,
        personality_insight="你具备较好的社团适配潜力。",
        weekly_hours=profile.weekly_hours,
        resume_summary=profile.chat_summary,
    )
