from datetime import datetime
import pytz

tz = pytz.timezone("Asia/Kolkata")
tf = "%d-%m-%Y%H:%M:%S"


def data_check(data: dict, channel_list: list) -> bool:
    if data["channel name"] not in channel_list:
        return False

    dt = data["date"] + data["time"]
    currentTimestamp = datetime.now(tz).timestamp()
    dtObjectTimestamp = tz.localize(datetime.strptime(dt, tf)).timestamp()

    if dtObjectTimestamp <= currentTimestamp:
        return False

    return True
