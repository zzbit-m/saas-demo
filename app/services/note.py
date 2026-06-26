from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note


async def create_note(
    db: AsyncSession, org_id: str, title: str, body: str, created_by: str
) -> Note:
    note = Note(org_id=org_id, title=title, body=body, created_by=created_by)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def get_notes(db: AsyncSession, org_id: str) -> list[Note]:
    result = await db.execute(
        select(Note)
        .where(Note.org_id == org_id)
        .order_by(Note.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_note(db: AsyncSession, note_id: str) -> Note | None:
    result = await db.execute(select(Note).where(Note.id == note_id))
    return result.scalar_one_or_none()


async def update_note(
    db: AsyncSession, note: Note, title: str | None = None, body: str | None = None
) -> Note:
    if title is not None:
        note.title = title
    if body is not None:
        note.body = body
    note.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(note)
    return note


async def delete_note(db: AsyncSession, note_id: str) -> bool:
    note = await get_note(db, note_id)
    if note is None:
        return False
    await db.delete(note)
    await db.commit()
    return True
