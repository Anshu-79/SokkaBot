from datetime import datetime

from globals import general

tz = general["tz"]
tf = general["tf"]

# Only returns False when the entered channel isn't in the guild's channel_list
# Or when the entered datetime was in the past
def data_check(data: dict, channel_list: list) -> bool:

    # channel_list is a list of text channels in the guild where $sch was sent
    if data["channel name"] not in channel_list:
        return False

    dt = data["date"] + data["time"]
    currentTimestamp = datetime.now(tz).timestamp()
    dtObjectTimestamp = tz.localize(datetime.strptime(dt, tf)).timestamp()

    if dtObjectTimestamp <= currentTimestamp:
        return False

    return True
