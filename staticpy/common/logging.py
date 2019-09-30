from enum import IntEnum, auto


class LoggingLevel(IntEnum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    FATAL = auto()


_logging_level = LoggingLevel.INFO


def set_logging_level(level: LoggingLevel):
    global _logging_level
    _logging_level = level


def debug(*args, **kwargs):
    if _logging_level >= LoggingLevel.DEBUG:
        print(*args, **kwargs)


def info(*args, **kwargs):
    if _logging_level >= LoggingLevel.INFO:
        print(*args, **kwargs)


def warning(*args, **kwargs):
    if _logging_level >= LoggingLevel.WARNING:
        print(*args, **kwargs)


def error(*args, **kwargs):
    if _logging_level >= LoggingLevel.ERROR:
        print(*args, **kwargs)


def fatal(*args, **kwargs):
    if _logging_level >= LoggingLevel.FATAL:
        print(*args, **kwargs)
