class Logger:

    TEMPLATE = "{0}{1}{2} {0}[0m"

    def __init__(self, name=""):
        self.name = name

    def fatal(self, message):
        self.__print("[1;41m", "FATAL:: " + message)

    def critical(self, message):
        self.fatal(message)

    def error(self, message):
        self.__print("[0;31m", "ERROR:: " + message)

    def warn(self, message):
        self.__print("[0;33m", "WARN:: " + message)

    def warning(self, message):
        self.warn(message)

    def info(self, message):
        self.__print("[0;39m", message)

    def debug(self, message):
        self.__print("[0;35m", "DEBUG:: " + message)

    def __print(self, color, message):
        print(self.TEMPLATE.format(chr(27), color, message))
