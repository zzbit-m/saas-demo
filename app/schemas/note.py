from datetime import datetime

from pydantic import BaseModel


class CreateNoteRequest(BaseModel):
    title: str
    body: str = ""


class UpdateNoteRequest(BaseModel):
    title: str | None = None
    body: str | None = None


class NoteResponse(BaseModel):
    id: str
    org_id: str
    title: str
    body: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
