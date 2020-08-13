import asyncio
import youtube_dl
import functools
import inspect
import re
from typing import Union, Optional
from dataclasses import dataclass
from konoha.core import KonohaException

is_url = re.compile(r'https?://[\w/:%#\$\?\(\)~\.=\+\-&]+')
is_youtube = re.compile(
    r'https?://(www\.)?youtube\.[\w/:%#\$\?\(\)~\.=\+\-&]+')

supported_url = (
    is_youtube,
)

##############
# Exceptions #
##############


class YTDLException(KonohaException):
    pass


class UnsupportedSiteException(YTDLException):
    pass

##############
# Interfaces #
##############


@dataclass
class Video:
    id: str
    url: str
    title: str
    webpage_url: str
    thumbnail: str
    description: str
    uploader: str
    duration: int
    view_count: int
    uploader_url: Union[str, None] = None

    @classmethod
    def from_dict(cls, kwargs):
        return cls(**{
            k: v for k, v in kwargs.items()
            if k in inspect.signature(cls).parameters
        })

##


class YTDLDownloader:
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'error',
        'source_address': '0.0.0.0',
    }

    def __init__(self, ctx, **options):
        self.requester = ctx.author
        self.channel = ctx.channel
        self.ytdl = youtube_dl.YoutubeDL(self.YTDL_OPTIONS)

    async def search(self, query, *, search='ytsearch5:', loop: Optional[asyncio.AbstractEventLoop] = None):
        if loop is None:
            loop = asyncio.get_event_loop()
        if is_url.match(query):
            if all([not ptn.match(query) for ptn in supported_url]):
                raise UnsupportedSiteException(query)
        else:
            query = search + query
        try:
            results = await loop.run_in_executor(
                None,
                functools.partial(self.ytdl.extract_info, query,
                                  download=False, process=True)
            )
        except:
            try:
                query = query.replace(search, 'ytsearch1:')
                results = await loop.run_in_executor(
                    None,
                    functools.partial(self.ytdl.extract_info, query,
                                      download=False, process=True)
                )
            except:
                raise YTDLException('動画情報の取得に失敗しました')
        try:
            if "entries" in results:
                results = [
                    Video.from_dict(result)
                    for result in results["entries"]
                ]
            else:
                results = [Video.from_dict(results)]
            return results
        except KeyError:
            raise YTDLException('動画の取得に失敗')
