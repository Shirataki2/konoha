import discord
import asyncio
import secrets
import jwt
from konoha.core import config
from konoha.core.abc import Singleton
from konoha.api.discord.session import Session
from konoha.api.models import Permission
from konoha.api.session import get_data, set_data

client_session = Session()
nil = NotImplemented


class Discord(Singleton):
    def __init__(self):
        self.token = config.bot_token

    @client_session.run("/users/@me")
    async def get_me(self, get=nil, url=nil, *, token):
        async with get(url, headers={'Authorization': f"Bearer {token}"}) as resp:
            resp.raise_for_status()
            data = await resp.json()
        return data

    @client_session.run("/users/@me/guilds")
    async def get_my_guilds(self, get=nil, url=nil, *, token):
        async with get(url, headers={'Authorization': f"Bearer {token}"}) as resp:
            resp.raise_for_status()
            data = await resp.json()
        return data

    @client_session.run("/guilds/{guild_id}?with_counts=true", auth=True)
    async def get_guild(self, get=nil, url=nil, *, guild_id):
        url = url.format(guild_id=guild_id)
        async with get(url) as resp:
            resp.raise_for_status()
            data = await resp.json()
        return data

    @client_session.run("/guilds/{guild_id}/members/{user_id}", auth=True)
    async def get_member(self, get=nil, url=nil, *, guild_id, user_id):
        url = url.format(guild_id=guild_id, user_id=user_id)
        async with get(url) as resp:
            resp.raise_for_status()
            data = await resp.json()
        return data

    @client_session.run("/guilds/{guild_id}/members", auth=True)
    async def get_members(self, get=nil, url=nil, *, guild_id, limit, after):
        url = url.format(guild_id=guild_id)
        async with get(url, params={"limit": limit, "after": after}) as resp:
            resp.raise_for_status()
            data = await resp.json()
        return data

    @client_session.run("/channels/{channel_id}/messages", method="post", auth=True)
    async def send_message(self, post=nil, url=nil, *, channel_id, **kwargs):
        url = url.format(channel_id=channel_id)
        async with post(url=url, json=kwargs) as resp:
            resp.raise_for_status()
            data = await resp.json()

    async def get_user_info(self, token, guild_id, session=None, response=None):
        token = token.lstrip("Bearer ")
        if session and session["key"].split(".")[0] == str(guild_id):
            data = get_data(session["key"])
            if data is not None:
                perms = Permission.from_json(data["perms"])
                member = data["member"]
                guild = data["guild"]
                return perms, member, guild
        else:
            session = None
        user = await self.get_me(token=token)
        member, guild = await asyncio.gather(
            self.get_member(guild_id=guild_id, user_id=user["id"]),
            self.get_guild(guild_id=guild_id)
        )
        perm = 0
        for role in member["roles"]:
            for r in guild["roles"]:
                if r["id"] == role:
                    perm |= r["permissions"]
                elif r["name"] == "@everyone":
                    perm |= r["permissions"]
        if guild["owner_id"] == user["id"]:
            perm |= 1 << 31
        if session is None:
            key = secrets.token_hex(64)
            payload = {
                "perms": Permission(perm).to_json(),
                "member": member,
                "guild": guild
            }
            jwt_token = jwt.encode({
                "sub": user["id"],
                "key": str(guild["id"]) + '.' + key
            }, config.session_key).decode('utf-8')
            set_data(str(guild["id"]) + '.' + key, payload)
            member["session_id"] = jwt_token
        return Permission(perm), member, guild
