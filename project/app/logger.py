import logging

class Logger(logging.Logger):
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        return instance
    
    def __init__(self, name, debug=False, level=logging.NOTSET):
        super().__init__(name, level)
        self.debug_enable = debug
        self.extra_info = None
        
    def get_logger(name: str, level=logging.INFO, debug=False, extra_info=None):
        logger = Logger(name, debug=debug, level=level)
        logger.setLevel(level)
        if extra_info:
            logger.set_extra_info(extra_info)
        return logger
        
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