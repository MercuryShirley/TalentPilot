from datetime import datetime
from pydantic import BaseModel, Field


class ChatProfileRequest(BaseModel):
    student_name: str = Field(..., min_length=1)
    major_category: str = ""
    interests: list[str] = []
    skills: list[str] = []
    personality_choices: list[str] = []
    assessment_answers: list[str] = []
    weekly_hours: int = 4
    chat_messages: list[str] = []


class ClubChatMessage(BaseModel):
    role: str
    content: str


class StudentProfileOut(BaseModel):
    id: int
    student_name: str
    major_category: str
    interests: list[str]
    skills: list[str]
    personality_tags: list[str]
    personality_code: str
    personality_insight: str
    weekly_hours: int
    resume_summary: str


class ModelInfoOut(BaseModel):
    provider: str
    model: str
    ready: bool


class ClubOut(BaseModel):
    id: int
    name: str
    category: str
    intro: str
    weekly_hours_min: int
    weekly_hours_max: int
    required_skills: list[str]
    preferred_tags: list[str]


class RecommendationOut(BaseModel):
    club: ClubOut
    score: float
    reasons: list[str]


class ApplicationCreate(BaseModel):
    profile_id: int
    club_id: int


class ApplicationOut(BaseModel):
    id: int
    profile_id: int
    club_id: int
    status: str


class FAQAskRequest(BaseModel):
    question: str


class ClubChatRequest(BaseModel):
    messages: list[ClubChatMessage] = []
    question: str = ""


class ClubActivityPostCreate(BaseModel):
    club_name: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    cover_url: str = ""
    event_time: datetime
    location: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    apply_link: str = Field(..., min_length=1)


class ClubActivityPostOut(BaseModel):
    id: int
    club_name: str
    title: str
    cover_url: str
    event_time: datetime
    location: str
    content: str
    apply_link: str
    created_at: datetime
