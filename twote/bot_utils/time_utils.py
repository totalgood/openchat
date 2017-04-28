from datetime import datetime
from dateutil.parser import parse
import pytz


def convert_to_utc(talk_time):
    """Convert the datetime string we get from SUTime to utcnow"""

    local_tz = pytz.timezone('US/Pacific')

    # get correct local year, month, dat
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