import logging
from logging.handlers import TimedRotatingFileHandler
from sty import fg

# Logger which logs info
infoLogger = logging.getLogger(__name__)
infoLogger.setLevel(logging.INFO)
infoLogger.propagate = False

# switches log files after 1 day to find errors faster
# deletes logs older than 30 days
infoFileHandler = TimedRotatingFileHandler(
    filename="logs/log.log",
    when="d",
    interval=1,
    backupCount=30,
    encoding="utf-8",
    delay=False,
)

streamHandler = logging.StreamHandler()
infoLogger.addHandler(streamHandler)
infoLogger.addHandler(infoFileHandler)

tf = "%d-%m-%Y %H:%M:%S"
logFormat = "\n{levelname}:{asctime}:\n{message}"

# streamHandler & infoFileHandler don't have the same formatters
# because streamHandler's log is colored but the other's isn't.
formatter = logging.Formatter(fmt=logFormat, datefmt=tf, style="{")

streamHandler.setFormatter(
    logging.Formatter(
        fmt=fg(91, 195, 235) + logFormat + fg.rs,
        datefmt=tf,
        style="{")
)

infoFileHandler.setFormatter(formatter)
