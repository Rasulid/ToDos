from fastapi import APIRouter

router = APIRouter(prefix="/auth",
                   tags=["Auth"],
                   responses={402: {"user": "not found"}})


@router.get('/')
async def get_user():
    return {"msg": "heloo"}
