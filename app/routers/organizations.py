from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_org_membership
from app.models.membership import Membership
from app.models.user import User
from app.schemas.organization import (
    CreateOrgRequest,
    InviteMemberRequest,
    OrgMemberResponse,
    OrgResponse,
    UpdateOrgRequest,
)
from app.services.organization import (
    add_member_by_email,
    create_org,
    get_members,
    get_org_by_id,
    get_org_by_slug,
    get_user_orgs,
    remove_member,
    update_org,
)

router = APIRouter(tags=["organizations"])


@router.post("/organizations", response_model=OrgResponse, status_code=201)
async def create_organization(
    body: CreateOrgRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrgResponse:
    existing = await get_org_by_slug(db, body.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization with this slug already exists",
        )
    org = await create_org(db, body.name, body.slug, current_user.id)
    return OrgResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        role="owner",
        created_at=org.created_at,
    )


@router.get("/organizations", response_model=list[OrgResponse])
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[OrgResponse]:
    orgs = await get_user_orgs(db, current_user.id)
    return [
        OrgResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            role=role,
            created_at=org.created_at,
        )
        for org, role in orgs
    ]


@router.get("/organizations/{org_id}", response_model=OrgResponse)
async def get_organization(
    membership: Membership = Depends(get_org_membership),
    db: AsyncSession = Depends(get_db),
) -> OrgResponse:
    org = await get_org_by_id(db, membership.org_id)
    return OrgResponse(
        id=org.id,  # type: ignore[union-attr]
        name=org.name,  # type: ignore[union-attr]
        slug=org.slug,  # type: ignore[union-attr]
        role=membership.role,
        created_at=org.created_at,  # type: ignore[union-attr]
    )


@router.patch("/organizations/{org_id}", response_model=OrgResponse)
async def update_organization(
    body: UpdateOrgRequest,
    membership: Membership = Depends(get_org_membership),
    db: AsyncSession = Depends(get_db),
) -> OrgResponse:
    if membership.role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can update the organization",
        )
    if body.slug is not None:
        existing = await get_org_by_slug(db, body.slug)
        if existing and existing.id != membership.org_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization with this slug already exists",
            )
    org = await get_org_by_id(db, membership.org_id)
    org = await update_org(db, org, name=body.name, slug=body.slug)  # type: ignore[arg-type]
    return OrgResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        role=membership.role,
        created_at=org.created_at,
    )


@router.get(
    "/organizations/{org_id}/members",
    response_model=list[OrgMemberResponse],
)
async def list_members(
    membership: Membership = Depends(get_org_membership),
    db: AsyncSession = Depends(get_db),
) -> list[OrgMemberResponse]:
    rows = await get_members(db, membership.org_id)
    return [
        OrgMemberResponse(
            user_id=mem.user_id,
            email=email,
            role=mem.role,
            created_at=mem.created_at,
        )
        for mem, email in rows
    ]


@router.post(
    "/organizations/{org_id}/members",
    response_model=OrgMemberResponse,
    status_code=201,
)
async def invite_member(
    body: InviteMemberRequest,
    membership: Membership = Depends(get_org_membership),
    db: AsyncSession = Depends(get_db),
) -> OrgMemberResponse:
    if membership.role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can invite members",
        )
    result = await add_member_by_email(db, membership.org_id, body.email, body.role)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or already a member",
        )
    return OrgMemberResponse(
        user_id=result.user_id,
        email=body.email,
        role=result.role,
        created_at=result.created_at,
    )


@router.delete(
    "/organizations/{org_id}/members/{user_id}",
    status_code=204,
)
async def delete_member(
    user_id: str,
    membership: Membership = Depends(get_org_membership),
    db: AsyncSession = Depends(get_db),
) -> None:
    if membership.role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can remove members",
        )
    removed = await remove_member(db, membership.org_id, user_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )
