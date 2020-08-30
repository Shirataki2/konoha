from fastapi import (
    APIRouter,
    Query,
    Header,
    Body
)
from discord import Embed
import konoha.models.crud as q
from konoha.core import config
from konoha.api.discord.client import Discord

router = APIRouter()
api = Discord()


@router.get("")
async def get_reminders(
    authorization: str = Header(...),
    guild_id: int = Query(...),
    limit: int = Query(100, le=100),
    offset: int = Query(0),
    sort_by: str = Query('start'),
    descending: bool = Query(False),
):
    perms, member, guild = await api.get_user_info(authorization, guild_id)
    reminders, count = await q.Reminder(guild_id).list(type=type, limit=limit, offset=offset, sort_by=sort_by, descending=descending)
    return {"reminders": reminders, "count": count}


@router.post("", status_code=204)
async def create_reminder(
    authorization: str = Header(...),
    guild_id: int = Query(...),
    content: str = Body(...),
    start_at: str = Body(...),
):
    perms, member, guild = await api.get_user_info(authorization, guild_id)
    await q.Reminder(guild_id).create(user=member["user"]["id"], content=content, start_at=start_at)
    c = await q.Reminder(guild_id).get_config()
    embed = Embed(title=content, color=config.theme_color, inline=False)
    embed.add_field(name='日時', value=start_at)
    embed.add_field(name='作成者', value=f'<@{member["user"]["id"]}>')
    await api.send_message(channel_id=c["channel"], content="新規リマインダーが登録されました", embed=embed.to_dict())


@router.patch("", status_code=204)
async def update_reminder(
    authorization: str = Header(...),
    guild_id: int = Query(...),
    reminder_id: int = Query(...),
    content: str = Body(...),
    start_at: str = Body(...),
):
    perms, member, guild = await api.get_user_info(authorization, guild_id)
    await q.Reminder(guild_id).set(reminder_id, content=content, start_at=start_at)
    c = await q.Reminder(guild_id).get_config()
    embed = Embed(title=content, color=config.theme_color, inline=False)
    embed.add_field(name='日時', value=start_at)
    embed.add_field(name='編集者', value=f'<@{member["user"]["id"]}>')
    await api.send_message(channel_id=c["channel"], content="リマインダーが変更されました", embed=embed.to_dict())


@router.delete("", status_code=204)
async def delete_reminder(
    authorization: str = Header(...),
    guild_id: int = Query(...),
    reminder_id: int = Query(...),
):
    perms, member, guild = await api.get_user_info(authorization, guild_id)
    reminder = await q.Reminder(guild_id).get(reminder_id)
    await q.Reminder(guild_id).delete(reminder_id)
    c = await q.Reminder(guild_id).get_config()
    embed = Embed(title=reminder["content"],
                  color=config.theme_color, inline=False)
    embed.add_field(name='日時', value=reminder["start_at"])
    embed.add_field(name='編集者', value=f'<@{member["user"]["id"]}>')
    await api.send_message(channel_id=c["channel"], content="リマインダーが削除されました", embed=embed.to_dict())


@router.get("/monthly")
async def get_reminders_monthly(
    authorization: str = Header(...),
    guild_id: int = Query(...),
    year: int = Query(2020),
    month: int = Query(1)
):
    perms, member, guild = await api.get_user_info(authorization, guild_id)
    reminders = await q.Reminder(guild_id).monthly(year=year, month=month)
    return reminders
