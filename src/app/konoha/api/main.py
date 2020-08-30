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
from konoha.api.discord.client import Discord
from konoha.api.routers import prefix, reminders, guilds

app = FastAPI(
    title='Konoha API',
    openapi_url='/openapi.json',
    docs_url='/dev',
    redoc_url='/docs'
)

discord = Discord()


app.include_router(prefix.router, prefix="/prefix")
app.include_router(reminders.router, prefix="/reminders")
app.include_router(guilds.router, prefix="/guilds")
