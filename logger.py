from enum import IntEnum


class Logger:

    TEMPLATE = "{0}{1}{2} {0}[0m"

    class Level(IntEnum):
        FATAL = 0
        ERROR = 1
        WARN = 2
        INFO = 3
        DEBUG = 4

    def __init__(self, name="", level=Level.INFO):
        self.name = name
        self.level = level

    def fatal(self, message):
        self.__print("[1;41m", "FATAL:: " + message)

    def critical(self, message):
        self.fatal(message)

    def error(self, message):
        if self.level < self.Level.ERROR:
            return
        self.__print("[0;31m", "ERROR:: " + message)

    def warn(self, message):
        if self.level < self.Level.WARN:
            return
        self.__print("[0;33m", "WARN:: " + message)

    def warning(self, message):
        self.warn(message)

    def info(self, message):
        if self.level < self.Level.INFO:
            return
        self.__print("[0;39m", message)

    def debug(self, message):
        if self.level < self.Level.DEBUG:
            return
        self.__print("[0;35m", "DEBUG:: " + message)

    def __print(self, color, message):
        print(self.TEMPLATE.format(chr(27), color, message))
