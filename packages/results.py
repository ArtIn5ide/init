from pathlib import Path
from datetime import datetime

def make_result_folder(root_folder):
    """
    Function creates result folders and defines
    result file path.

    Args:
        root_folder (str): root folder path;

    Return:
        result_folder (str): path to result folder;
        result_file (str): path to result file;
        gantt_folder (str): path to Gantt charts folder;
    """

    # Make result folder.
    now = datetime.now().strftime(r'%Y-%m-%d_%H.%M.%S')
    folder_name = f'uptime_{now}'
    result_folder = root_folder / folder_name

    result_folder.mkdir(exist_ok=True)

    # Define result file path.
    result_file = result_folder / 'uptime.xlsx'

    # Make folder for Gantt charts.
    gantt_folder = result_folder / 'GanttCharts'

    gantt_folder.mkdir(exist_ok=True)

    return result_folder, result_file, gantt_folder

if __name__ == '__main__':
    pass
