import logging
from colorama import Fore, Back, Style


class ColoredLogger(logging.Logger):
    @staticmethod
    def _debug(*msgs):
        return f'{Fore.CYAN}{", ".join(msgs)}{Style.RESET_ALL}'

    @staticmethod
    def _info(*msgs):
        return f'{Fore.LIGHTBLUE_EX}{", ".join(msgs)}{Style.RESET_ALL}'

    @staticmethod
    def _warn(*msgs):
        return f'{Fore.YELLOW}{", ".join(msgs)}{Style.RESET_ALL}'

    @staticmethod
    def _error(*msgs):
        return f'{Fore.RED}{", ".join(msgs)}{Style.RESET_ALL}'

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            return self._log(logging.DEBUG, self._debug(msg), args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            return self._log(logging.INFO, self._info(msg), args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.WARN):
            return self._log(logging.WARN, self._warn(msg), args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.ERROR):
            return self._log(logging.ERROR, self._error(msg), args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.CRITICAL):
            return self._log(logging.CRITICAL, self._error(msg), args, **kwargs)


logging.setLoggerClass(ColoredLogger)

handler = logging.StreamHandler()

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)
discord_logger.addHandler(handler)

aio_logger = logging.getLogger('asyncio')
aio_logger.setLevel(logging.DEBUG)
aio_logger.addHandler(handler)


def get_module_logger(modname):
    logger = logging.getLogger(modname)
    logger_format = "%(asctime)s %(name)28s[%(lineno)4d] - %(levelname)8s: %(message)s"
    date_format = "%Y/%m/%d %H:%M:%S"
    formatter = logging.Formatter(logger_format, datefmt=date_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger
