from fastapi import APIRouter, Depends

from modules.user.service import get_user_profile
from shared.auth_middleware import AuthUser, get_current_user
from shared.database import get_db, AsyncSession

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/profile")
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    profile = await get_user_profile(db, current_user.uid)

    return profile
