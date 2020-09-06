import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import secrets
import json
import aiomysql

import konoha.models.crud2 as q
from konoha.core.abc import Singleton


class Timer(Singleton):
    def __init__(self):
        pass

    def start(self, bot):
        self.bot = bot
        self._have_event = asyncio.Event(loop=self.bot.loop)
        self._next_event = None
        self._task = self.bot.loop.create_task(self.dispatch_events())

    async def wait_for_next_event(self, cap_day=40):
        event = await q.Timer.get_next(self.bot, cap_day)
        if event is not None:
            self._have_event.set()
            return event
        else:
            self._have_event.clear()
            self._next_event = None
            await self._have_event.wait()
            return await q.Timer.get_next(self.bot, cap_day)

    async def dispatch_events(self):
        try:
            while not self.bot.is_closed():
                event = self._next_event = await self.wait_for_next_event()
                now = datetime.utcnow()
                sec = (event.expire_at - now).total_seconds()
                if sec > 0:
                    await asyncio.sleep(sec)
                await q.Timer(self.bot, event.id).delete()
                event_name = f'{event.event}_completed'
                self.bot.dispatch(event_name, json.loads(event.payload))
        except asyncio.CancelledError:
            raise
        except (OSError, discord.ConnectionClosed):
            self._task.cancel()
            self._task = self.bot.loop.create_task(self.dispatch_events())

    async def wait_short_time(self, dur, event, payload):
        await asyncio.sleep(dur)
        event_name = f'{event}_completed'
        self.bot.dispatch(event_name, json.dumps(payload))

    async def create_event(self, event, expire_at: datetime, payload: dict):
        dur = (expire_at - datetime.utcnow()).total_seconds()
        if dur <= 60:
            self.bot.loop.create_task(
                self.wait_short_time(dur, event, payload)
            )
            return
        id = secrets.token_hex(16)[:16]
        await q.Timer.create(self.bot, id, event, expire_at, json.dumps(payload))
        if dur <= (86400 * 40):
            self._have_event.set()
        if self._next_event and expire_at < self._next_event.expire_at:
            self._task.cancel()
            self._task = self.bot.loop.create_task(self.dispatch_events())
