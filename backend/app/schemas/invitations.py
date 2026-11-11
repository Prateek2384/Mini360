import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class InvitationCreate(BaseModel):
    emails: list[EmailStr] = Field(min_length=1, max_length=20)


class InvitationLink(BaseModel):
    id: uuid.UUID
    rater_email: str
    invite_url: str
    expires_at: datetime


class InvitationCreateResult(BaseModel):
    invitations: list[InvitationLink]
