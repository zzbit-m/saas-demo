from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_org_membership
from app.models.membership import Membership
from app.models.user import User
from app.schemas.note import CreateNoteRequest, NoteResponse, UpdateNoteRequest
from app.services.note import create_note, delete_note, get_note, get_notes, update_note

router = APIRouter(tags=["notes"])


@router.get(
    "/organizations/{org_id}/notes",
    response_model=list[NoteResponse],
)
async def list_notes(
    membership: Membership = Depends(get_org_membership),
    db: AsyncSession = Depends(get_db),
) -> list[NoteResponse]:
    notes = await get_notes(db, membership.org_id)
    return [NoteResponse.model_validate(n) for n in notes]


@router.post(
    "/organizations/{org_id}/notes",
    response_model=NoteResponse,
    status_code=201,
)
async def create_note_endpoint(
    body: CreateNoteRequest,
    membership: Membership = Depends(get_org_membership),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    note = await create_note(
        db, membership.org_id, body.title, body.body, current_user.id
    )
    return NoteResponse.model_validate(note)


@router.get(
    "/organizations/{org_id}/notes/{note_id}",
    response_model=NoteResponse,
)
async def get_note_endpoint(
    note_id: str,
    membership: Membership = Depends(get_org_membership),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    note = await get_note(db, note_id)
    if note is None or note.org_id != membership.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    return NoteResponse.model_validate(note)


@router.patch(
    "/organizations/{org_id}/notes/{note_id}",
    response_model=NoteResponse,
)
async def update_note_endpoint(
    note_id: str,
    body: UpdateNoteRequest,
    membership: Membership = Depends(get_org_membership),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    note = await get_note(db, note_id)
    if note is None or note.org_id != membership.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    if note.created_by != current_user.id and membership.role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author or an admin can update this note",
        )
    note = await update_note(db, note, title=body.title, body=body.body)
    return NoteResponse.model_validate(note)


@router.delete(
    "/organizations/{org_id}/notes/{note_id}",
    status_code=204,
)
async def delete_note_endpoint(
    note_id: str,
    membership: Membership = Depends(get_org_membership),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    note = await get_note(db, note_id)
    if note is None or note.org_id != membership.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    if note.created_by != current_user.id and membership.role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author or an admin can delete this note",
        )
    await delete_note(db, note.id)
