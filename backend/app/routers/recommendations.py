from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Club, MatchResult, StudentProfile
from app.schemas import ClubOut, RecommendationOut
from app.services.llm_service import generate_match_reasons
from app.services.match_service import compute_match_details, parse_csv_tags

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{profile_id}", response_model=list[RecommendationOut])
def get_recommendations(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    clubs = db.query(Club).all()
    student_data = {
        "major_category": profile.major,
        "interests": parse_csv_tags(profile.interests),
        "skills": parse_csv_tags(profile.skills),
        "personality_tags": parse_csv_tags(profile.personality_tags),
        "weekly_hours": profile.weekly_hours,
    }

    scored_clubs: list[dict] = []
    for c in clubs:
        club_data = {
            "name": c.name,
            "category": c.category,
            "intro": c.intro,
            "preferred_tags": parse_csv_tags(c.preferred_tags),
            "required_skills": parse_csv_tags(c.required_skills),
            "weekly_hours_min": c.weekly_hours_min,
            "weekly_hours_max": c.weekly_hours_max,
        }
        score = compute_match_details(student_data, club_data)["score"]
        scored_clubs.append({"club": c, "club_data": club_data, "score": score})

    top_scored = sorted(scored_clubs, key=lambda item: item["score"], reverse=True)[:3]

    results: list[RecommendationOut] = []
    for item in top_scored:
        c = item["club"]
        score = item["score"]
        reasons = generate_match_reasons(student_data, item["club_data"], score)

        db.add(
            MatchResult(
                profile_id=profile.id,
                club_id=c.id,
                score=score,
                reason_text=" | ".join(reasons),
            )
        )

        results.append(
            RecommendationOut(
                club=ClubOut(
                    id=c.id,
                    name=c.name,
                    category=c.category,
                    intro=c.intro,
                    weekly_hours_min=c.weekly_hours_min,
                    weekly_hours_max=c.weekly_hours_max,
                    required_skills=parse_csv_tags(c.required_skills),
                    preferred_tags=parse_csv_tags(c.preferred_tags),
                ),
                score=score,
                reasons=reasons,
            )
        )

    db.commit()
    return results
