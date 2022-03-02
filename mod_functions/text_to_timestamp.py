from datetime import datetime

from globals import general

tz = general["tz"]
tf = general["tf"]


def t2t(text):
    return tz.localize(datetime.strptime(text, tf)).timestamp()
