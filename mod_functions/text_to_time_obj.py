from datetime import datetime
import pytz


def timeObj(text: str):
    tz = pytz.timezone("Asia/Kolkata")
    tf = "%d-%m-%Y%H:%M:%S"

    return tz.localize(datetime.strptime(text, tf))
