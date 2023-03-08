
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from datetimes import subtract_datetime
from constants import DT_FORMAT

def timetable_calculation(history):
    """
    Calculates time of each tool in status from history (history of tool status change)
    within date and time borders: [start_dt, end_dt].

    history:
    {issue_id1: [
        {'label': '',
         'added': '2018-11-09T11:39:53.351Z',
         'removed': '2018-11-10T12:24:53.001Z',
        },
        {...},
        ...],
     issue_id2: [
        {...},
        {...},
        ...],
     ...}

    Args:
        history (dict): dictionary with status (label) change for each tool (issue);
        start_dt (datetime object): start date and time;
        end_dt (datetime object): end date and time;

    Return:
        timetable (dict): dictionary with time (days/hours/minutes/seconds)
                          of each label (status) for each issue (tool).
    """

    try:

        timetable = {}

        for iid, data in history.items():

            tmp = []

            for row in data:

                added_dt = datetime.strptime(row['added'], DT_FORMAT)
                removed_dt = datetime.strptime(row['removed'], DT_FORMAT)

                days, hours, minutes, seconds = subtract_datetime(added_dt, removed_dt)

                label_time =\
                {
                    'id'     : row['id'],
                    'added'  : row['added'],
                    'removed': row['removed'],
                    'days'   : days,
                    'hours'  : hours,
                    'minutes': minutes,
                    'seconds': seconds
                }

                tmp.append(label_time)

            timetable[iid] = tmp

        return timetable

    except KeyError:
        print("Error during labels time calculation.")
        exit()

def timetable_summary(timetable,
                      issues,
                      labels):
    """
    Function calculates the summary time
    for each issue (tool) for each label (state).

    Args:
        timetable (dict): contains times of each issue and each label;
        issues (dict): dict with project issues: (issue_iid, issue_title);
        labels (dict): dict with project issues: (label_id, label_name);

    Return:
        summary (dict): dict with the summary time
                        for each issue (tool) for each label (state).
    """

    summary = {}

    for issue_iid in issues.keys():

        tmp = \
        {
            label_iid : 0.0 for label_iid in labels.keys()
        }
        summary[issue_iid] = tmp

    for iid, data in timetable.items():
        for row in data:

            summary[iid][row['id']] += row['days']

    return summary

if __name__ == '__main__':
    pass
