from fastapi import (
    APIRouter,
    Query,
    Header,
    HTTPException
)
from discord import Embed
import konoha.models.crud as q
from konoha.core import config
from konoha.api.discord.client import Discord

router = APIRouter()
api = Discord()


@router.get("")
async def get_prefix(
    authorization: str = Header(...),
    guild_id: int = Query(...),
):
    config = await q.Guild(guild_id).get()
    try:
        return config["prefix"]
    except:
        raise HTTPException(404)


@router.patch("", status_code=204)
async def change_prefix(
    authorization: str = Header(...),
    guild_id: int = Query(...),
    prefix: str = Query(..., max_length=8)
):
    perms, member, guild = await api.get_user_info(authorization, guild_id)
    if not perms.can_manage_guild:
        raise HTTPException(403)
    config = await q.Guild(guild_id).get()
    try:
        await q.Guild(guild_id).set(prefix=prefix)
    except:
        raise HTTPException(503)
