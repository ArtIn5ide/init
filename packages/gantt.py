import concurrent.futures
import plotly.figure_factory as ff
from plotly.offline import plot
from constants import LABELS, COLORS

def make_gantt_charts(history, issue_name, dir_path):
    """
    Function creates Gantt chart for each issue in issues,
    using plotly.figure_factory.create_gantt function and
    saves '.html' on disk.
    history:
    {issue_id1: [
        {'added': u'2018-03-19T11:24:32.866Z',
         'id': 316,
         'removed': u'2018-03-19T11:26:45.761Z'}
        {'added': u'2018-04-03T08:22:17.666Z',
         'id': 320,
         'removed': u'2018-04-03T11:31:06.041Z'},
         ...],
     issue_id2: [
         ...],
     ...}

    Args:
        history (dict): history of label changes for each issue;
        issue_name (string): Tool name as in issue on Gitlab;
        dir_path (str): path to dir where Gantt charts should be saved.
    """

    # Sort history[issue_iid] by labels.keys() order.
    data = sorted(history,
                    key=lambda x: list(LABELS.keys()).index(x['id']))

    # Reorganize data in a way, which suits ff.create_gantt() funct.
    dataframe = []
    for row in data:

        tmp = {}
        tmp['Task'] = LABELS[row['id']]
        tmp['Start'] = row['added']
        tmp['Finish'] = row['removed']

        dataframe.append(tmp)

    # Create Gantt chart (plotly.figure_factory.create_gantt) and
    # save '.html' files on disk.
    if dataframe:
        fig = ff.create_gantt(dataframe, colors=COLORS,
                                index_col='Task', showgrid_x=True, group_tasks=True)

        plot(fig,
                filename=str(dir_path / f'{issue_name}_GanttChart.html'), auto_open=False)

if __name__ == '__main__':
    pass
