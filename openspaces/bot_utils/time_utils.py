from datetime import datetime, timedelta, timezone, time
from dateutil.parser import parse
import pytz


def convert_to_utc(talk_time, date_mention=False):
    """Convert the datetime string we get from SUTime to utcnow"""
    local_tz = pytz.timezone('US/Pacific')

    # get correct local year, month, day
    local_date = datetime.now(local_tz)
    local_date_str = datetime.strftime(local_date, "%Y %m %d")
    year, month, day = local_date_str.split(" ")

    # get SUTime parsed talk time and extract hours, mins
    dt_obj = parse(talk_time)
    local_time_str = datetime.strftime(dt_obj, "%H %M")
    hours, mins = local_time_str.split(" ")
    
    # build up correct datetime obj, normalize & localize, switch to utc 
    correct_dt = datetime(int(year), int(month), int(day), int(hours), int(mins))
    tz_aware_local = local_tz.normalize(local_tz.localize(correct_dt))
    local_as_utc = tz_aware_local.astimezone(pytz.utc)

    return local_as_utc

def get_local_clock_time():
    local_dt = datetime.now(pytz.timezone('US/Pacific'))
    local_clock_time = datetime.strftime(local_dt, "%H:%M")
    return local_clock_time

def check_start_time(talk_time):
    """If time of openspaces talk within next 30 mins return True"""
    time_diff = talk_time - datetime.now(timezone.utc)
    threshold = timedelta(minutes=30)

    if time_diff < threshold:
        return True
    else:
        return False
