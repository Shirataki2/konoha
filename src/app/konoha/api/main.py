from fastapi import (
    FastAPI,
    Query,
    Header,
    Body,
    HTTPException
)
from aiohttp import ClientSession, ClientResponse
from typing import List
from discord import Embed

import konoha.models.crud as q
from konoha.core import config
from konoha.api.models import Permission

app = FastAPI(**{
    'title': 'Konoha API',
    'openapi_url': "/openapi.json",
    'docs_url': '/dev',
    'redoc_url': '/docs'
})

api_base = "https://discord.com/api"
cdn_base = "https://cdn.discordapp.com"


async def get_auth(authorization, guild_id):
    if authorization[:7] != 'Bearer ':
        raise HTTPException(401)
    user = await get_user(authorization[7:])
    if not user:
        raise HTTPException(401)
    try:
        perms, member, guild = await check_user_perms(user["id"], guild_id)
    except:
        raise HTTPException(401)
    return perms, member, guild


@app.get("/")
def ping():
    return {"status": "OK"}


@app.get("/reminders")
async def reminders(guild_id: int = Query(...), type: str = Query("future"), limit: int = Query(100, le=100), offset: int = Query(0), authorization: str = Header(...), sort_by: str = Query('start'), descending: bool = Query(False)):
    perms, member, guild = await get_auth(authorization, guild_id)
    reminders, count = await q.Reminder(guild_id).list(type=type, limit=limit, offset=offset, sort_by=sort_by, descending=descending)
    return {"reminders": reminders, "count": count}


@app.get("/month_reminders")
async def get_month_reminders(guild_id: int = Query(...), year: int = Query(2020), month: int = Query(1), authorization: str = Header(...)):
    perms, member, guild = await get_auth(authorization, guild_id)
    reminders = await q.Reminder(guild_id).monthly(year=year, month=month)
    return reminders


@app.post("/reminder", status_code=204)
async def new_reminder(guild_id: int = Query(...), authorization: str = Header(...), content: str = Body(...), start_at: str = Body(...)):
    perms, member, guild = await get_auth(authorization, guild_id)
    await q.Reminder(guild_id).create(user=member["user"]["id"], content=content, start_at=start_at)
    c = await q.Reminder(guild_id).get_config()
    embed = Embed(title=content, color=config.theme_color, inline=False)
    embed.add_field(name='日時', value=start_at)
    embed.add_field(name='作成者', value=f'<@{member["user"]["id"]}>')
    async with ClientSession() as session:
        session: ClientSession
        await session.post(
            f"{api_base}/channels/{c['channel']}/messages",
            json={
                "content": "新規リマインダーが登録されました",
                "embed": embed.to_dict()
            },
            headers={
                "Authorization": f"Bot {config.bot_token}"
            }
        )
    return


@app.patch("/reminder", status_code=204)
async def update_reminder(guild_id: int = Query(...), reminder_id: int = Query(...), authorization: str = Header(...), content: str = Body(...), start_at: str = Body(...)):
    perms, member, guild = await get_auth(authorization, guild_id)
    await q.Reminder(guild_id).set(reminder_id, content=content, start_at=start_at)
    c = await q.Reminder(guild_id).get_config()
    embed = Embed(title=content, color=config.theme_color, inline=False)
    embed.add_field(name='日時', value=start_at)
    embed.add_field(name='編集者', value=f'<@{member["user"]["id"]}>')
    async with ClientSession() as session:
        session: ClientSession
        await session.post(
            f"{api_base}/channels/{c['channel']}/messages",
            json={
                "content": "リマインダーが変更されました",
                "embed": embed.to_dict()
            },
            headers={
                "Authorization": f"Bot {config.bot_token}"
            }
        )
    return


@app.delete("/reminder", status_code=204)
async def delete_reminder(guild_id: int = Query(...), reminder_id: int = Query(...), authorization: str = Header(...)):
    perms, member, guild = await get_auth(authorization, guild_id)
    reminder = await q.Reminder(guild_id).get(reminder_id)
    await q.Reminder(guild_id).delete(reminder_id)
    c = await q.Reminder(guild_id).get_config()
    embed = Embed(title=reminder["content"],
                  color=config.theme_color, inline=False)
    embed.add_field(name='日時', value=reminder["start_at"])
    embed.add_field(name='編集者', value=f'<@{member["user"]["id"]}>')
    async with ClientSession() as session:
        session: ClientSession
        await session.post(
            f"{api_base}/channels/{c['channel']}/messages",
            json={
                "content": "リマインダーが削除されました",
                "embed": embed.to_dict()
            },
            headers={
                "Authorization": f"Bot {config.bot_token}"
            }
        )
    return


@app.get("/prefix")
async def get_prefix(guild_id: int = Query(...), authorization: str = Header(...)):
    config = await q.Guild(guild_id).get()
    try:
        return config["prefix"]
    except:
        raise HTTPException(404)


@app.patch("/prefix", status_code=204)
async def patch_prefix(guild_id: int = Query(...), authorization: str = Header(...), prefix: str = Query(..., max_length=8)):
    config = await q.Guild(guild_id).get()
    try:
        config["prefix"]
    except:
        raise HTTPException(404)
    perms, member, guild = await get_auth(authorization, guild_id)
    perm_check = False
    if perms.owner or perms.manage_guild or perms.administrator:
        perm_check = True
    if not perm_check:
        raise HTTPException(401)
    try:
        await q.Guild(guild_id).set(prefix=prefix)
    except:
        raise HTTPException(503)


@app.get("/guilds")
async def guilds(token: str = Query(...)):
    async with ClientSession() as session:
        session: ClientSession
        async with session.get(api_base + "/users/@me/guilds", headers={
            "Authorization": f"Bearer {token}"
        }) as resp:
            resp: ClientResponse
            guilds = list(filter(lambda g: g["permissions"] & 32, await resp.json(encoding="utf-8")))
            guilds2 = list(filter(lambda g: not (g["permissions"] & 32), await resp.json(encoding="utf-8")))
    for guild in guilds:
        if await q.Guild(guild["id"]).get(verbose=2):
            guild["joined"] = 1
        else:
            guild["joined"] = 0
        if guild["icon"]:
            guild["icon_url"] = cdn_base + \
                f"/icons/{guild['id']}/{guild['icon']}"
    for guild in guilds2:
        if await q.Guild(guild["id"]).get(verbose=2):
            guild["joined"] = 1
        else:
            guild["joined"] = 0
        if guild["icon"]:
            guild["icon_url"] = cdn_base + \
                f"/icons/{guild['id']}/{guild['icon']}"
    return guilds, list(filter(lambda g: g["joined"] == 1, guilds2))


@app.get("/guild")
async def guild(guild_id: int = Query(...), authorization: str = Header(...)):
    perms, member, guild = await get_auth(authorization, guild_id)
    if perms in [401, 404]:
        raise HTTPException(perms)
    async with ClientSession() as session:
        session: ClientSession
        async with session.get(api_base + f"/guilds/{guild_id}?with_counts=true", headers={
            "Authorization": f"Bot {config.bot_token}"
        }) as resp:
            resp: ClientResponse
            guild = await resp.json()
            if guild["icon"]:
                guild["icon_url"] = cdn_base + \
                    f"/icons/{guild['id']}/{guild['icon']}"
        guild["user"] = member
        guild["user"]["permissions"] = perms.to_json()
        return guild


@app.get("/members")
async def members(guild_id: int = Query(...), authorization: str = Header(...), limit: int = Query(2), offset: int = Query(0)):
    perms, member, guild = await get_auth(authorization, guild_id)
    return await get_users_with_perms(guild_id, limit, offset)


def get_highest_role(perms: Permission, member, guild):
    is_owner = perms.owner
    perm_pos = -1
    if is_owner:
        perm_pos = int(1e7)
        r = None
    else:
        for user_role in member["roles"]:
            for guild_role in guild["roles"]:
                if user_role == guild_role["id"]:
                    if perm_pos < guild_role["position"]:
                        perm_pos = guild_role["position"]
                        r = guild_role
    return perm_pos, r


def check_roles_changeable(highest, roles, guild):
    for role in roles:
        for r in guild["roles"]:
            if role == r["id"]:
                if r["position"] >= highest:
                    return False
    return True


@app.patch('/userrole', status_code=204)
async def userrole(
    guild_id: int = Query(...),
    user_id: int = Query(...),
    authorization: str = Header(...),
    roles: List[str] = Body(None)
):
    perms, member, guild = await get_auth(authorization, guild_id)
    highest, r = get_highest_role(perms, member, guild)
    perm_check = False
    if perms.owner or perms.manage_roles or perms.administrator:
        perm_check = True
    if not perm_check:
        raise HTTPException(401)
    if not check_roles_changeable(highest, roles, guild):
        raise HTTPException(401)
    if r:
        roles.append(r["id"])
    async with ClientSession() as session:
        session: ClientSession
        async with session.patch(
            api_base + f"/guilds/{guild_id}/members/{user_id}",
            json={
                "roles": roles
            },
            headers={
                "Authorization": f"Bot {config.bot_token}"
            }
        ) as resp:
            resp: ClientResponse
            if resp.status == 204:
                return
            else:
                raise HTTPException(403)


async def get_user(token):
    try:
        async with ClientSession() as session:
            session: ClientSession
            async with session.get(api_base + f"/users/@me", headers={
                "Authorization": f"Bearer {token}"
            }) as resp:
                resp: ClientResponse
                data = await resp.json()
        return data if data is not None else None
    except:
        return None


async def check_user_perms(user_id, guild_id):
    try:
        async with ClientSession() as session:
            session: ClientSession
            async with session.get(api_base + f"/guilds/{guild_id}/members/{user_id}", headers={
                "Authorization": f"Bot {config.bot_token}"
            }) as resp:
                resp: ClientResponse
                user = await resp.json()
        if user.get('code') == 10007:
            return 404
        async with ClientSession() as session:
            async with session.get(api_base + f"/guilds/{guild_id}", headers={
                "Authorization": f"Bot {config.bot_token}"
            }) as resp:
                resp: ClientResponse
                guild = await resp.json()
        perm = 0
        for role in user["roles"]:
            for r in guild["roles"]:
                if r["id"] == role:
                    perm |= r["permissions"]
        if guild["owner_id"] == user_id:
            perm |= 1 << 31
        try:
            for r in guild["roles"]:
                if r["name"] == "@everyone":
                    perm |= r["permissions"]
        except:
            return 401
        user_perm = Permission(perm)
        return user_perm, user, guild
    except KeyboardInterrupt:
        return 401


async def get_users_with_perms(guild_id, limit=25, offset_id=0):
    try:
        async with ClientSession() as session:
            session: ClientSession
            async with session.get(
                api_base + f"/guilds/{guild_id}/members",
                params={
                    "limit": limit,
                    "after": offset_id
                },
                headers={
                    "Authorization": f"Bot {config.bot_token}"
                }
            ) as resp:
                resp: ClientResponse
                users = await resp.json()
        # if users.get('code') == 10007:
        #     return 404
        def_perm = 0
        async with ClientSession() as session:
            async with session.get(api_base + f"/guilds/{guild_id}", headers={
                "Authorization": f"Bot {config.bot_token}"
            }) as resp:
                resp: ClientResponse
                guild = await resp.json()
        try:
            for r in guild["roles"]:
                if r["name"] == "@everyone":
                    def_perm |= r["permissions"]
        except:
            return 401
        for user in users:
            perm = def_perm
            for role in user["roles"]:
                for r in guild["roles"]:
                    if r["id"] == role:
                        perm |= r["permissions"]
            if guild["owner_id"] == user["user"]["id"]:
                perm |= 1 << 31
            user["permissions"] = Permission(perm).to_json()
        return users
    except:
        return 401
