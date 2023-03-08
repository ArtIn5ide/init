
import sys
from datetime import datetime, timedelta, time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from constants import DT_FORMAT

def preproc(dt):
    """
    Function makes dt (datetime object) preprocessing.
    if dt.weekday==Monday and dt.time < 8:00    ---> dt.weekday==Monday and dt.time==8:00;
    if dt.weekday==Saturday and dt.time >= 8:00 ---> dt.weekday==Monday and dt.time==8:00;
    if dt.weekday==Sunday                       ---> dt.weekday==Monday and dt.time==8:00.

    Args:
        dt (datetime object): date and time before preprocessing;

    Return:
        dt (datetime object): date and time after preprocessing;
    """

    t = time(hour=8, minute=0)

    if dt.weekday() == 6:
        dt = datetime.combine(dt + timedelta(days=1), t) # weekday==6 <=> Sunday

    elif dt.weekday() == 5 and dt.hour >= 8:
        dt = datetime.combine(dt + timedelta(days=2), t) # weekday==5 <=> Saturday

    elif dt.weekday() == 0 and dt.hour < 8:
        dt = datetime.combine(dt, t) # weekday==0 <=> Monday

    return dt

def subtract_datetime(start_dt, end_dt):
    """
    Function calculates days, hours, minutes, seconds
    between two datetime objects: start_dt and end_dt (including Weekends)

    Args:
        start_dt (datetime object): start datetime;
        end_dt (datetime object): end datetime;

    Return:
        days, hours, minutes, seconds (tuple): number of days, hours, minutes, seconds
                                               between start_dt and end_dt;

    """

    # Total seconds between start_dt and end_dt.
    seconds = (end_dt - start_dt).total_seconds()
    minutes = seconds/60.0
    hours = minutes/60.0
    days = hours/24.0

    return days, hours, minutes, seconds

def _subtract_datetime(start_dt, end_dt):
    """
    Function calculates days, hours, minutes, seconds
    between two datetime objects: start_dt and end_dt
    Weekends are ignored.

    Args:
        start_dt (datetime object): start datetime;
        end_dt (datetime object): end datetime;

    Return:
        days, hours, minutes, seconds (tuple): number of days, hours, minutes, seconds
                                               between start_dt and end_dt;

    """

    start_dt = preproc(start_dt)
    end_dt = preproc(end_dt)

    # List with datetime objs which correspond to each day between start_dt and end_dt.
    days = [start_dt + timedelta(x + 1) for x in range((end_dt - start_dt).days)]

    days_off = []

    # Calculate weekend days between start_dt and end_dt.
    for day in days:

        if day.date() == end_dt.date():
            if day.weekday() == 5 and day.hour >= 8: # weekday==5 <=> Saturday
                days_off.append(day)

        else:
            if day.weekday() >= 5:
                days_off.append(day)

    days_off.sort()
    seconds_off = len(days_off)*24.*60.*60.

    # Total seconds except weekends.
    seconds = (end_dt - start_dt).total_seconds() - seconds_off
    minutes = seconds/60.0
    hours = minutes/60.0
    days = hours/24.0

    return days, hours, minutes, seconds

def filter_by_datetime(history,
                       start_dt, end_dt):
    """
    Filters history by datetime. Function leaves only data
    which satisfy one of the conditions:
    1. data were 'added' in [start_dt, end_dt] bounds;
    2. data were 'added' before start_dt and 'removed' after start_dt;

    Args:
        history (dict): input data to be filtered;
        start_dt (datetime obj): start datetime, selected by user;
        end_dt (datetime obj): end datetime, selected by user;

    Return:
        filtered_history (dict): filtered data.
    """

    try:
        for iid, data in history.items():
            to_delete = []
            for i, entry in enumerate(data):

                dt_added = datetime.strptime(entry['added'], DT_FORMAT)
                dt_removed = datetime.strptime(entry['removed'], DT_FORMAT)

                if dt_added >= end_dt:
                    to_delete.append(i)

                elif dt_removed <= start_dt:
                    to_delete.append(i)

                else:
                    if dt_removed > end_dt:
                        data[i]['removed'] = end_dt.strftime(DT_FORMAT)
                    if dt_added < start_dt:
                        data[i]['added'] = start_dt.strftime(DT_FORMAT)

            for i in to_delete[::-1]:
                del history[iid][i]

    except KeyError:
        print("Error during history filtering by datetime.")
        exit()

if __name__ == '__main__':
    pass
