
import sys
from datetime import datetime, time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from windows import calendar_window
from constants import DESCRIPTION, START, END

def get_start_end_datetime():
    """
    Gets 'start' and 'end' datetime from ttkcalendar GUI.
    Checks that input 'start' and 'end' are correct.

    Return:
        start, end (datetime_obj): 'start' and 'end' datetime objects.
    """

    start_time = time(0, 0, 0)
    end_time = time(23, 59, 59, 999999)
    
    comment = DESCRIPTION + '\nStart date: '
    start_date = calendar_window(title='Select start date',
                                 comment=comment)

    if start_date:
        start = datetime.combine(start_date, start_time)
        start_date = start_date.date()
    else:
        start_date = START.date() 
        start = START

    comment = comment + f'{start}\nEnd date: '
    end_date = calendar_window(title='Select end date',
                               comment=comment)

    if end_date:
        end = datetime.combine(end_date, end_time)
        end_date = end_date.date()
    else:
        end_date = END.date()
        end = END

    if end_date <= start_date:
        start_date, end_date = end_date, start_date
        start = datetime.combine(start_date, start_time)
        end = datetime.combine(end_date, end_time)

    start = START if start < START else start 
    end = END if end > END else end

    return start, end

if __name__ == '__main__':
    pass
