"""Module Logger: extends logger class"""
import logging


class Logger(logging.Logger):
    """Extends python logger class to allow for extra information.

    Args:
        logging (Logger): Default python logger
    """
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        return instance

    def __init__(self, name, debug=True, level=logging.NOTSET):
        super().__init__(name, level)
        self.debug_enable = debug
        self.extra_info = None

    def _get_extra(self, xtra):
        return xtra if xtra is not None else self.extra_info

    def set_extra_info(self, extra_info: dict):
        self.extra_info = extra_info

    def add_extra_info(self, new_info: dict):
        if self.extra_info is None:
            self.extra_info = new_info
        else:
            self.extra_info.update(new_info)

    def info(self, msg, *args, xtra=None, **kwargs):
        super().info(msg, *args, extra=self._get_extra(xtra), **kwargs)

    def warn(self, msg, *args, xtra=None, **kwargs):
        super().warning(msg, *args, extra=self._get_extra(xtra), **kwargs)

    def error(self, msg, *args, xtra=None, **kwargs):
        super().critical(msg, *args, extra=self._get_extra(xtra), **kwargs)

    def fatal(self, msg, *args, xtra=None, **kwargs):
        super().fatal(msg, *args, extra=self._get_extra(xtra), **kwargs)

    def debug(self, msg, *args, xtra=None, **kwargs):
        if self.debug_enable is True:
            super().debug(msg, *args, extra=self._get_extra(xtra), **kwargs)


def get_logger(name: str, level=logging.INFO, debug=False, extra_info=None):
    """Logger factory function. Returns a logger instance intended to be used
       instead of the classic print()-Function.

    Args:
        name (str): Logger name
        level (Literal[20], optional): Log level. Defaults to logging.INFO.
        debug (bool, optional): Set to True to allow debug messages. Defaults to False.
        extra_info (any, optional): _description_. Defaults to None.

    Returns:
        Logger: A logger to print messages to screen.
    """    
    logger = Logger(name, debug=debug, level=level)
    logging.basicConfig()
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s][%(name)s][%(levelname)s]: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if extra_info:
        logger.set_extra_info(extra_info)
    return logger
