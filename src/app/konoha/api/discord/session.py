import aiohttp
import functools
from functools import wraps
from konoha.core import config


class Session:
    def __init__(self):
        self._api_endpoint = 'https://discord.com/api'
        self._cdn_endpoint = 'https://cdn.discordapp.com'

    def prepare(self, type, auth):
        if auth:
            headers = {'Authorization': f"Bot {config.bot_token}"}
        else:
            headers = None
        if type == 'api':
            endpoint = self._api_endpoint
        else:
            endpoint = self._cdn_endpoint
        return endpoint, headers

    def run(self, url, *, method="get", type='api', auth=False, **kwargs):
        def _run(coro):
            @wraps(coro)
            async def wrapper(*_args, **_kwargs):
                endpoint, headers = self.prepare(type, auth)
                async with aiohttp.ClientSession() as session:
                    fn = functools.partial(
                        getattr(session, method), headers=headers, **kwargs)
                    _args = list(_args)
                    _args.insert(1, fn)
                    _args.insert(2, endpoint + url)
                    data = await coro(*_args, **_kwargs)
                return data
            return wrapper
        return _run
