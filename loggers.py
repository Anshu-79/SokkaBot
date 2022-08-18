import logging
from logging.handlers import TimedRotatingFileHandler
from sty import fg

tf = "%d-%m-%Y %H:%M:%S"
logFormat = "\n{levelname}:{asctime}:\n{message}"

formatter = logging.Formatter(fmt=logFormat, datefmt=tf, style="{")


def setFormat(colorCode):
    return logging.Formatter(
        fmt= colorCode + logFormat + fg.rs,
        datefmt=tf,
        style="{")


# For logging initialization info on stream
initLogger = logging.getLogger('initLogger')
initLogger.propagate = False
initLogger.setLevel(logging.INFO)

initStreamHandler = logging.StreamHandler()
initStreamHandler.setFormatter(logging.Formatter(
    fmt=fg(241, 211, 2)+"{message}"+fg.rs,
    datefmt=tf,
    style='{'))
initLogger.addHandler(initStreamHandler)


# Logger which logs command outputs
cmdLogger = logging.getLogger('cmdLogger')
cmdLogger.setLevel(logging.INFO)
cmdLogger.propagate = False

cmdFileHandler = TimedRotatingFileHandler(
    filename="logs/cmd_log.log",
    when="d",
    interval=1,
    backupCount=30,
    encoding="utf-8",
    delay=False,
)
cmdFileHandler.setFormatter(formatter)
cmdLogger.addHandler(cmdFileHandler)

# cmdStreamHandler & cmdFileHandler don't have the same formatters
# because cmdStreamHandler's log is colored but the other's isn't.
cmdStreamHandler = logging.StreamHandler()
cmdStreamHandler.setFormatter(setFormat(fg(91, 195, 235)))
cmdLogger.addHandler(cmdStreamHandler)


# Logger that logs errors
errorLogger = logging.getLogger('errorLogger')
errorLogger.propagate = False
errorLogger.setLevel(logging.WARNING)

errorStreamHandler = logging.StreamHandler()
errorStreamHandler.setFormatter(setFormat(fg(247,92,3)))
errorLogger.addHandler(errorStreamHandler)

errorFileHandler = TimedRotatingFileHandler(
    filename="logs/error_log.log",
    when="d",
    interval=1,
    backupCount=30,
    encoding="utf-8",
    delay=False,
)
errorFileHandler.setFormatter(formatter)
errorLogger.addHandler(errorFileHandler)
