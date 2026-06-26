from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.services.user import get_user_by_email


async def create_org(
    db: AsyncSession, name: str, slug: str, owner_user_id: str
) -> Organization:
    org = Organization(name=name, slug=slug)
    db.add(org)
    await db.flush()

    membership = Membership(
        user_id=owner_user_id, org_id=org.id, role="owner"
    )
    db.add(membership)
    await db.commit()
    await db.refresh(org)
    return org


async def get_org_by_id(db: AsyncSession, org_id: str) -> Organization | None:
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    return result.scalar_one_or_none()


async def get_org_by_slug(db: AsyncSession, slug: str) -> Organization | None:
    result = await db.execute(select(Organization).where(Organization.slug == slug))
    return result.scalar_one_or_none()


async def get_user_orgs(
    db: AsyncSession, user_id: str
) -> list[tuple[Organization, str]]:
    result = await db.execute(
        select(Organization, Membership.role)
        .join(Membership, Membership.org_id == Organization.id)
        .where(Membership.user_id == user_id)
    )
    return list(result.tuples().all())


async def get_membership(
    db: AsyncSession, org_id: str, user_id: str
) -> Membership | None:
    result = await db.execute(
        select(Membership).where(
            Membership.org_id == org_id, Membership.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def get_members(
    db: AsyncSession, org_id: str
) -> list[tuple[Membership, str]]:
    result = await db.execute(
        select(Membership, User.email)
        .join(User, Membership.user_id == User.id)
        .where(Membership.org_id == org_id)
        .order_by(Membership.created_at)
    )
    return list(result.tuples().all())


async def add_member_by_email(
    db: AsyncSession, org_id: str, email: str, role: str
) -> Membership | None:
    user = await get_user_by_email(db, email)
    if user is None:
        return None

    existing = await get_membership(db, org_id, user.id)
    if existing is not None:
        return None

    membership = Membership(user_id=user.id, org_id=org_id, role=role)
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


async def remove_member(db: AsyncSession, org_id: str, user_id: str) -> bool:
    membership = await get_membership(db, org_id, user_id)
    if membership is None:
        return False
    await db.delete(membership)
    await db.commit()
    return True


async def update_org(
    db: AsyncSession,
    org: Organization,
    name: str | None = None,
    slug: str | None = None,
) -> Organization:
    if name is not None:
        org.name = name
    if slug is not None:
        org.slug = slug
    await db.commit()
    await db.refresh(org)
    return org
