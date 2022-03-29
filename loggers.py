import logging
from sty import fg

# Logger which logs info
infoLogger = logging.getLogger(__name__)
infoLogger.setLevel(logging.INFO)
infoLogger.propagate = False

infoFileHandler = logging.FileHandler(filename="log.log")

streamHandler = logging.StreamHandler()
infoLogger.addHandler(streamHandler)
infoLogger.addHandler(infoFileHandler)

formatter = logging.Formatter(
    fg(91, 195, 235) + "\n%(levelname)s:%(asctime)s:\n%(message)s" + fg.rs
)
streamHandler.setFormatter(formatter)
infoFileHandler.setFormatter(formatter)
