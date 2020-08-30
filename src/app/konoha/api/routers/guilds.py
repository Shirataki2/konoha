from fastapi import (
    APIRouter,
    Query,
    Header,
    Path,
    Depends,
    Response
)
from discord import Embed
from typing import Optional
import konoha.models.crud as q
from konoha.core import config
from konoha.api.discord.client import Discord, client_session
from konoha.api.session import get_current_user, get_data, set_data

router = APIRouter()
api = Discord()


@router.get("/me")
async def get_guilds(
    authorization: str = Header(...)
):
    guilds = await api.get_my_guilds(token=authorization.lstrip("Bearer "))
    for guild in guilds:
        if await q.Guild(guild["id"]).get(verbose=0):
            guild["joined"] = 1
        else:
            guild["joined"] = 0
        if guild["icon"]:
            guild["icon_url"] = client_session._cdn_endpoint + \
                f"/icons/{guild['id']}/{guild['icon']}"
    guilds_with_admin = list(
        filter(lambda g: g["permissions"] & 32, guilds)
    )
    guilds_without_admin = list(
        filter(lambda g: not (g["permissions"] & 32)
               and g["joined"] == 1, guilds)
    )
    return guilds_with_admin, guilds_without_admin


@router.get("/{guild_id}")
async def get_guild(
    guild_id: int = Path(...),
    authorization: str = Header(...),
):
    perms, member, guild = await api.get_user_info(authorization, guild_id)
    guild["user"] = member
    guild["user"]["permissions"] = perms.to_json()
    if guild["icon"]:
        guild["icon_url"] = client_session._cdn_endpoint + \
            f"/icons/{guild['id']}/{guild['icon']}"
    return guild


@router.get("/{guild_id}/members", deprecated=True)
async def get_guild_members(
    authorization: str = Header(...),
    guild_id: int = Path(...),
    limit: int = Query(10),
    offset: int = Query(0),
):
    perms, member, guild = await api.get_user_info(authorization, guild_id)
    return guild
