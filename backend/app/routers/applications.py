from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, Club, StudentProfile
from app.schemas import ApplicationCreate, ApplicationOut

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == payload.profile_id).first()
    club = db.query(Club).filter(Club.id == payload.club_id).first()
    if not profile or not club:
        raise HTTPException(status_code=400, detail="Invalid profile_id or club_id")

    exists = (
        db.query(Application)
        .filter(Application.profile_id == payload.profile_id, Application.club_id == payload.club_id)
        .first()
    )
    if exists:
        return ApplicationOut(
            id=exists.id,
            profile_id=exists.profile_id,
            club_id=exists.club_id,
            status=exists.status,
        )

    snapshot = f"name={profile.student_name}; interests={profile.interests}; skills={profile.skills}"
    app = Application(
        profile_id=payload.profile_id,
        club_id=payload.club_id,
        status="submitted",
        profile_snapshot=snapshot,
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    return ApplicationOut(id=app.id, profile_id=app.profile_id, club_id=app.club_id, status=app.status)


@router.get("/profile/{profile_id}", response_model=list[ApplicationOut])
def list_my_applications(profile_id: int, db: Session = Depends(get_db)):
    rows = db.query(Application).filter(Application.profile_id == profile_id).order_by(Application.id.desc()).all()
    return [
        ApplicationOut(id=r.id, profile_id=r.profile_id, club_id=r.club_id, status=r.status)
        for r in rows
    ]


@router.get("/club/{club_id}", response_model=list[ApplicationOut])
def list_club_candidates(club_id: int, db: Session = Depends(get_db)):
    rows = db.query(Application).filter(Application.club_id == club_id).order_by(Application.id.desc()).all()
    return [
        ApplicationOut(id=r.id, profile_id=r.profile_id, club_id=r.club_id, status=r.status)
        for r in rows
    ]


@router.patch("/{application_id}/status", response_model=ApplicationOut)
def update_status(application_id: int, status: str, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = status
    db.commit()
    db.refresh(app)
    return ApplicationOut(id=app.id, profile_id=app.profile_id, club_id=app.club_id, status=app.status)
