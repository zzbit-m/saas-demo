from datetime import datetime

from pydantic import BaseModel, EmailStr


class CreateOrgRequest(BaseModel):
    name: str
    slug: str


class OrgResponse(BaseModel):
    id: str
    name: str
    slug: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrgMemberResponse(BaseModel):
    user_id: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: str = "member"


class UpdateOrgRequest(BaseModel):
    name: str | None = None
    slug: str | None = None
