import asyncio
import json
import random
from pytz import timezone
from datetime import datetime, timedelta
from sqlalchemy.sql import and_, select, func
from sqlalchemy import desc
from aiomysql.sa import create_engine

from konoha.models import models
from konoha.core.abc import Singleton
from konoha.core import config
from konoha.core.log.logger import get_module_logger
logger = get_module_logger(__name__)


class DB:
    _engine = None

    def __init__(self, loop=None):
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

    @property
    async def engine(self):
        if self._engine is not None:
            return self._engine
        self._engine = await create_engine(
            user=config.db_user,
            db=config.db_name,
            host=config.db_host,
            password=config.db_password,
            charset='utf8',
            autocommit=True,
            loop=self.loop
        )
        return self._engine

    async def __aenter__(self):
        e = await self.engine
        self._conn = await e.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._conn.close()

    async def execute(self, query, *args, **kwargs):
        async with self._conn.begin():
            result = await self._conn.execute(query, *args, **kwargs)
        return result


class CRUDBase:
    @staticmethod
    async def execute(query, verbose=1, *args, **kwargs):
        loop = kwargs.get('loop')
        _DB = DB(loop)
        if verbose:
            logger.debug("DB接続開始")
            if verbose:
                s = str(query)
                for l in s.split("\n"):
                    logger.debug(f"\t{l}")
        async with _DB as db:
            result = await db.execute(query)
        if verbose:
            logger.debug("DB接続終了")
        return result

    async def get(self):
        raise NotImplementedError

    async def set(self, **kwargs):
        raise NotImplementedError

    async def delete(self):
        raise NotImplementedError

    @classmethod
    async def create(cls, **kwargs):
        raise NotImplementedError


class Guild(CRUDBase):
    def __init__(self, guild_id, **kwargs):
        self.guild_id = guild_id
        super().__init__(**kwargs)

    async def get(self, verbose=1):
        q = models.guild.select().where(self.guild_id == models.guild.c.id)
        result = await Guild.execute(q, verbose)
        return await result.fetchone()

    async def set(self, verbose=1, **kwargs):
        q = models.guild.update(None).where(
            self.guild_id == models.guild.c.id).values(**kwargs)
        await Guild.execute(q, verbose)
        return self

    async def delete(self, verbose=1):
        q = models.guild.delete(None).where(self.guild_id == models.guild.c.id)
        await Guild.execute(q, verbose)
        return self

    @classmethod
    async def create(cls, guild_id, verbose=1):
        q = models.guild.insert(None).values(id=guild_id)
        guild = cls(guild_id)
        await Guild.execute(q, verbose)
        return guild

    @staticmethod
    async def get_all(verbose=1):
        q = models.guild.select()
        results = await Guild.execute(q, verbose)
        return await results.fetchall()


class Hook(CRUDBase):
    def __init__(self, guild_id, channel_id, **kwargs):
        self.guild_id = guild_id
        self.channel_id = channel_id
        super().__init__(**kwargs)

    async def get(self, verbose=1):
        q = models.hook.select().where(and_(self.guild_id == models.hook.c.guild,
                                            self.channel_id == models.hook.c.channel))
        result = await Hook.execute(q, verbose)
        return await result.fetchone()

    async def set(self, verbose=1, **kwargs):
        q = models.hook.update(None).where(and_(
            self.guild_id == models.hook.c.guild, self.channel_id == models.hook.c.channel)).values(**kwargs)
        await Hook.execute(q, verbose)
        return self

    async def delete(self, verbose=1):
        q = models.hook.delete(None).where(and_(
            self.guild_id == models.hook.c.guild, self.channel_id == models.hook.c.channel))
        await Hook.execute(q, verbose)
        return self

    @classmethod
    async def create(cls, guild_id, channel_id, hookurl, tags, verbose=1):
        q = models.hook.insert(None).values(
            guild=guild_id, channel=channel_id, hookurl=hookurl, tags=tags)
        guild = cls(guild_id, channel_id)
        await Hook.execute(q, verbose)
        return guild

    @staticmethod
    async def search(verbose=1, **kwargs):
        q = models.hook.select().where(
            and_(*[v == getattr(models.hook.c, k) for k, v in kwargs.items()]))
        result = await Hook.execute(q, verbose)
        return await result.fetchall()

    @staticmethod
    async def get_all(verbose=1):
        q = models.hook.select()
        results = await Hook.execute(q, verbose)
        return await results.fetchall()


class Reminder(CRUDBase):
    def __init__(self, guild_id, **kwargs):
        self.guild_id = guild_id
        super().__init__(**kwargs)

    async def get_config(self, verbose=1):
        q = models.reminder_config.select().where(
            self.guild_id == models.reminder_config.c.guild,
        )
        result = await Reminder.execute(q, verbose)
        return await result.fetchone()

    @staticmethod
    async def get_config_from_id(id, verbose=1):
        q = models.reminder_config.select().where(
            id == models.reminder_config.c.id,
        )
        result = await Reminder.execute(q, verbose)
        return await result.fetchone()

    async def update_config(self, channel_id=None, verbose=1):
        if (await self.get_config(verbose)) and channel_id:
            q = models.reminder_config.update(None).where(
                self.guild_id == models.reminder_config.c.guild,
            ).values(channel=channel_id)
            await Reminder.execute(q, verbose)
            return "update"
        else:
            q = models.reminder_config.insert(None).values(
                guild=self.guild_id, channel=channel_id
            )
            await Reminder.execute(q, verbose)
            return "create"

    async def get(self, id, verbose=1):
        c = await self.get_config(verbose)
        q = models.reminder.select().where(
            and_(
                models.reminder.c.config == c.id,
                models.reminder.c.id == id
            )
        )
        result = await Reminder.execute(q, verbose)
        return await result.fetchone()

    async def list(self, verbose=1, type='future', limit=10, offset=0, sort_by='start', descending=True):
        c = await self.get_config(verbose)
        f = [models.reminder.c.config == c.id]
        if type == 'future':
            f.append(datetime.now().astimezone(timezone('Asia/Tokyo'))
                     <= models.reminder.c.start_at)
        elif type == 'past':
            f.append(datetime.now().astimezone(timezone('Asia/Tokyo'))
                     >= models.reminder.c.start_at)
        if sort_by == 'start' and not descending:
            s = models.reminder.c.start_at
        elif sort_by == 'start' and descending:
            s = desc(models.reminder.c.start_at)
        elif sort_by == 'created' and not descending:
            s = models.reminder.c.created_at
        elif sort_by == 'created' and descending:
            s = desc(models.reminder.c.created_at)
        join = models.reminder.join(models.reminder_config)
        conf = models.reminder_config.c
        q = select([models.reminder, conf.guild, conf.channel]) \
            .select_from(join) \
            .order_by(s) \
            .where(and_(*f)).limit(limit).offset(offset)
        result = await Reminder.execute(q, verbose)
        data = await result.fetchall()
        q = models.reminder.count(None).where(
            and_(*f))
        result = await Reminder.execute(q, verbose)
        count = await result.scalar()
        return data, count

    async def monthly(self, verbose=1, year=2020, month=1):
        c = await self.get_config(verbose)
        f = [models.reminder.c.config == c.id]
        f.append(datetime(year=year, month=month, day=1)
                 <= models.reminder.c.start_at)
        if month != 12:
            f.append(datetime(year=year, month=month+1, day=1)
                     > models.reminder.c.start_at)
        else:
            f.append(datetime(year=year+1, month=1, day=1)
                     > models.reminder.c.start_at)
        s = models.reminder.c.start_at
        join = models.reminder.join(models.reminder_config)
        conf = models.reminder_config.c
        q = select([models.reminder, conf.guild, conf.channel]) \
            .select_from(join) \
            .order_by(s) \
            .where(and_(*f))
        result = await Reminder.execute(q, verbose)
        data = await result.fetchall()
        return data

    async def set(self, id, verbose=1, **kwargs):
        c = await self.get_config(verbose)
        q = models.reminder.update(None).where(
            and_(
                models.reminder.c.config == c.id,
                models.reminder.c.id == id
            )
        ).values(**kwargs)
        await Reminder.execute(q, verbose)
        return self

    async def delete(self, id, verbose=1, **kwargs):
        c = await self.get_config(verbose)
        q = models.reminder.delete(None).where(
            and_(
                models.reminder.c.config == c.id,
                models.reminder.c.id == id
            )
        )
        await Reminder.execute(q, verbose)
        return self

    @staticmethod
    async def search_between_minutes(minutes, verbose=1):
        q = models.reminder.select().where(
            and_(
                datetime.now().astimezone(timezone('Asia/Tokyo')) +
                timedelta(minutes=minutes-1) <= models.reminder.c.start_at,
                datetime.now().astimezone(timezone('Asia/Tokyo')) +
                timedelta(minutes=minutes) >= models.reminder.c.start_at,
            )
        )
        result = await Reminder.execute(q, verbose)
        return await result.fetchall()

    async def create(self, user, content, start_at, verbose=1):
        c = await self.get_config(verbose)
        q = models.reminder.insert(None).values(
            config=c.id,
            user=user,
            content=content,
            start_at=start_at,
            created_at=datetime.now().astimezone(timezone('Asia/Tokyo'))
        )
        await Reminder.execute(q, verbose)
        return self


class Error(CRUDBase):
    def __init__(self, id, **kwargs):
        self.id = id
        super().__init__(**kwargs)

    async def get(self, verbose=1):
        q = models.error_log.select().where(self.id == models.error_log.c.id)
        result = await self.execute(q, verbose)
        return await result.fetchone()

    @classmethod
    async def create(cls, id, guild_id, channel_id, user_id, message_id, command, name, detail, traceback, verbose=1):
        q = models.error_log.insert(None).values(
            id=id, guild=guild_id, channel=channel_id, user=user_id, message=message_id, command=command,
            name=name, detail=detail, traceback=traceback
        )
        guild = cls(id)
        await cls.execute(q, verbose)
        return guild

    @staticmethod
    async def search(verbose=1, **kwargs):
        q = models.error_log.select().where(
            and_(*[v == getattr(models.error_log.c, k) for k, v in kwargs.items()]))
        result = await CRUDBase.execute(q, verbose)
        return await result.fetchall()


class User(CRUDBase):
    def __init__(self, id, **kwargs):
        self.id = id
        super().__init__(**kwargs)

    async def get(self, verbose=1):
        q = models.user_status.select().where(self.id == models.user_status.c.id)
        result = await self.execute(q, verbose)
        return await result.fetchone()

    @classmethod
    async def create(cls, id, verbose=1, **kwargs):
        q = models.user_status.insert(None).values(id=id, **kwargs)
        guild = cls(id)
        await cls.execute(q, verbose)
        return guild

    async def set(self, verbose=1, **kwargs):
        q = models.user_status.update(None).where(
            models.user_status.c.id == self.id
        ).values(**kwargs)
        await Reminder.execute(q, verbose)
        return self

    @staticmethod
    async def search(verbose=1, **kwargs):
        q = models.user_status.select().where(
            and_(*[v == getattr(models.user_status.c, k) for k, v in kwargs.items()]))
        result = await CRUDBase.execute(q, verbose)
        return await result.fetchall()


class Vote(CRUDBase):
    def __init__(self, id, **kwargs):
        self.id = id
        super().__init__(**kwargs)

    async def get(self, verbose=1):
        q = models.vote.select().where(self.id == models.vote.c.id)
        result = await self.execute(q, verbose)
        return await result.fetchone()

    @classmethod
    async def create(cls, id, verbose=1, **kwargs):
        q = models.vote.insert(None).values(id=id, **kwargs)
        guild = cls(id)
        await cls.execute(q, verbose)
        return guild

    async def set(self, verbose=1, **kwargs):
        q = models.vote.update(None).where(
            models.vote.c.id == self.id
        ).values(**kwargs)
        await Reminder.execute(q, verbose)
        return self

    @staticmethod
    async def search(verbose=1, **kwargs):
        q = models.vote.select().where(
            and_(*[v == getattr(models.vote.c, k) for k, v in kwargs.items()]))
        result = await CRUDBase.execute(q, verbose)
        return await result.fetchall()


class Timer(CRUDBase):
    def __init__(self, id, **kwargs):
        self.id = id
        super().__init__(**kwargs)

    async def get(self, verbose=1):
        q = models.timer.select().where(self.id == models.timer.c.id)
        result = await self.execute(q, verbose)
        return await result.fetchone()

    @classmethod
    async def create(cls, id, event, expire_at, payload, verbose=1):
        q = models.timer.insert(None).values(
            id=id,
            event=event,
            payload=json.dumps(payload),
            expire_at=expire_at,
            created_at=datetime.now().astimezone(timezone('Asia/Tokyo'))
        )
        await cls.execute(q, verbose)
        return cls(id)

    @classmethod
    async def get_next(cls, cap_day, verbose=1):
        q = models.timer.select().where(and_(
            datetime.now().astimezone(timezone('Asia/Tokyo')) + timedelta(days=cap_day)
            >= models.timer.c.expire_at
        )).order_by(models.timer.c.expire_at).limit(1)
        result = await cls.execute(q, verbose)
        return await result.fetchone()

    async def delete(self, verbose=1):
        q = models.timer.delete(None).where(
            models.timer.c.id == self.id
        )
        await self.execute(q, verbose)
        return self


class Vocab(CRUDBase):
    def __init__(self, name, **kwargs):
        self.name = name
        super().__init__(**kwargs)

    async def get(self, verbose=1):
        q = models.noun.select().where(self.name == models.noun.c.name)
        result = await self.execute(q, verbose)
        return await result.fetchone()

    @classmethod
    async def get_random(cls, first, verbose=1):
        q = models.noun.select().where(first == models.noun.c.first)
        result = await cls.execute(q, verbose)
        data = await result.fetchall()
        return random.choice(data)


class Money(CRUDBase):
    def __init__(self, guild_id, user_id, **kwargs):
        self.user_id = str(user_id)
        self.guild_id = str(guild_id)
        super().__init__(**kwargs)

    async def get(self, verbose=1):
        q = models.money.select().where(and_(
            self.user_id == models.money.c.user,
            self.guild_id == models.money.c.guild
        ))
        result = await self.execute(q, verbose)
        return await result.fetchone()

    @classmethod
    async def create(cls, user_id, guild_id, verbose=1, **kwargs):
        q = models.money.insert(None).values(
            user=user_id, guild=guild_id, **kwargs)
        await cls.execute(q, verbose)
        return cls(guild_id, user_id)

    async def set(self, verbose=1, **kwargs):
        q = models.money.update(None).where(and_(
            self.user_id == models.money.c.user,
            self.guild_id == models.money.c.guild
        )).values(**kwargs)
        await Reminder.execute(q, verbose)
        return self

    @staticmethod
    async def reset(verbose=1):
        q = models.money.update(None).values(bonus=0)
        await CRUDBase.execute(q, verbose)
