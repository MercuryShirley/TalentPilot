from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(50))
    intro: Mapped[str] = mapped_column(Text)
    weekly_hours_min: Mapped[int] = mapped_column(Integer)
    weekly_hours_max: Mapped[int] = mapped_column(Integer)
    required_skills: Mapped[str] = mapped_column(String(255), default="")
    preferred_tags: Mapped[str] = mapped_column(String(255), default="")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_name: Mapped[str] = mapped_column(String(100))
    major: Mapped[str] = mapped_column(String(100), default="")
    interests: Mapped[str] = mapped_column(String(255), default="")
    skills: Mapped[str] = mapped_column(String(255), default="")
    personality_tags: Mapped[str] = mapped_column(String(255), default="")
    weekly_hours: Mapped[int] = mapped_column(Integer, default=4)
    chat_summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"))
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"))
    score: Mapped[float] = mapped_column(Float)
    reason_text: Mapped[str] = mapped_column(Text)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"), index=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="submitted")
    profile_snapshot: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ClubFAQ(Base):
    __tablename__ = "club_faqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), index=True)
    question: Mapped[str] = mapped_column(String(255))
    answer: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ClubActivityPost(Base):
    __tablename__ = "club_activity_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    club_name: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(200))
    cover_url: Mapped[str] = mapped_column(String(500), default="")
    event_time: Mapped[datetime] = mapped_column(DateTime)
    location: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(Text)
    apply_link: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
