from configparser import ConfigParser
from sys import argv
from konoha.core.log.logger import get_module_logger

logger = get_module_logger(__name__)


class Config:
    bot_token: str = ""
    db_user: str = ""
    db_host: str = ""
    db_password: str = ""
    db_name: str = ""
    danbooru_name: str = ""
    danbooru_key: str = ""
    oauth2_url: str = ""
    theme_color: int = 0xff0000
    log_channel: str = ""
    deepl_apikey: str = ""

    def __init__(self, ini_file_path: str) -> None:
        parser = ConfigParser()
        try:
            parser.read(ini_file_path)
        except FileNotFoundError as e:
            logger.critical(f"{ini_file_path}が見つかりません")
            raise e
        config = parser["konoha"]
        for key in config:
            if hasattr(self, key):
                if isinstance(getattr(self, key), int):
                    setattr(self, key, int(config[key], 16))
                else:
                    setattr(self, key, config[key])


config = Config('config.ini')
