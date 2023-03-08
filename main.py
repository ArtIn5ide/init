import concurrent.futures
import sys
from pathlib import Path
from requests.exceptions import ConnectionError
sys.path.append(str(Path(__file__).parent))

from packages.constants import CONFIG_FILENAME, DESCRIPTION, LABELS, TOTAL_CORES
from packages.datetimes import filter_by_datetime
from packages.downloads import download_issues
from packages.gantt import make_gantt_charts
from packages.get_datetime import get_start_end_datetime
from packages.indexes import calculate_indexes, verify_indexes
from packages.json_handler import load_config, parse_config
from packages.new_api import download_history, to_new_form
from packages.occurrence import occurrence_curve
from packages.old_api import download_old_history
from packages.pie import pie
from packages.results import make_result_folder
from packages.timetable import timetable_calculation, timetable_summary
from packages.windows import checkbuttons_window, result_window
from packages.xlsx import write_xlsx

def main():
    """
    Main function of the application.
    Tool state changes (from GITLAB project) analysis.
    """

    print('Start analysis.')

    # Ask user to select start and end datetime.
    start_dt, end_dt = get_start_end_datetime()

    print(f"\nStart date: {start_dt}")
    print(f"End date: {end_dt}\n")
    print('Downloading statuses and tools from GITLAB project...')

    # Download config from packages/config.json.
    config = load_config(CONFIG_FILENAME)

    # Download project issues, LABELS and label colors.
    try:
        issues = download_issues()
    except ConnectionError:
        print('Request failed. Unable to establish connection with Gitlab.')
        exit()
    except Exception as ex:
        print(ex)
        exit()

    # Ask user to select required issues.
    title = 'Select tools: '
    comment = DESCRIPTION +\
              f'\nStart date: {start_dt}' +\
              f'\nEnd date: {end_dt}' +\
              '\nSelect tools for analysis: '
    issues = checkbuttons_window(issues, title, comment)

    if not issues:
        print('No tools were selected. Exiting.')
        exit()

    # Create required result folders and files.
    root_folder = Path(__file__).parent
    result_folder, result_file, gantt_folder = make_result_folder(root_folder)
    history_folder = root_folder / 'history'
    history_folder.mkdir(exist_ok=True)

    print('Downloading tool status change history from GITLAB project...')
    history = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(issues)//2 + 1) as executor:
        # Download old_history via old Gitlab API.
        futures = []
        tools = []
        for issue in issues.items():
            futures.append(executor.submit(download_old_history, issue))
        # Download new_history via new Gitlab API.
        try:
            for result in concurrent.futures.as_completed(futures):
                old_history, issue = result.result()
                tools.append(executor.submit(download_history, old_history, issue))

            for tool in concurrent.futures.as_completed(tools):
                history.update(tool.result())

        except ConnectionError:
            print('Request failed. Unable to establish connection with Gitlab.')
            exit()
        except Exception as ex:
            print(ex)
            exit()
    
    history = to_new_form(history)
    # Remove history parts which are outside [start_dt, end_dt] bounds.
    filter_by_datetime(history, start_dt, end_dt)
    print('Calculating each status time for each tool...')

    # Calculate timetable, i.e. duration of each issue label in history.
    timetable = timetable_calculation(history)

    # Calculate summary time for each issue and for each label.
    summary = timetable_summary(timetable, issues, LABELS)
    print('Calculating required production indexes...')

    # Calculate all required production indexes:
    # UPTIME, SERVICE_KPI, MTBF, EDU, MTTR, MTOL, MTBD, PII.
    indexes, avg_indexes = calculate_indexes(summary,
                                             history, LABELS)
    # Load indexes specs from config.
    specs = parse_config(config, 'specs')

    # Verify each index in 'indexes' and 'avg_indexes' dicts.
    verification = (verify_indexes(indexes, specs, True),
                    verify_indexes(avg_indexes, specs, False))
    print('Making charts...')
    pie_charts = []
    total_pie_charts = []
    occurrence_charts = []
    # Make required charts: pie, occurrence and Gantt charts.
    with concurrent.futures.ProcessPoolExecutor(max_workers=( TOTAL_CORES//2 )) as executor:
        charts = executor.map(pie,
                              [summary[_id] for _id in issues.keys()],
                              issues.values())
        for chart in charts:
            pie_charts.append(chart)

        charts = executor.map(pie,
                              [summary[_id] for _id in issues.keys()],
                              issues.values(),
                              [True]*len(issues))
        for chart in charts:
            total_pie_charts.append(chart)

        charts = executor.map(occurrence_curve, [timetable[_id] for _id in issues.keys()], issues.values())
        for chart in charts:
            occurrence_charts.append(chart)

        executor.map(make_gantt_charts, [history[_id] for _id in issues.keys()], issues.values(), [gantt_folder] * len(issues))
    print('Writing results...')

    # Write all required data to .xlsx file.
    wb_data = (timetable, summary, issues, LABELS,\
               indexes, avg_indexes, verification, specs,\
               pie_charts, total_pie_charts, occurrence_charts,\
               start_dt, end_dt)

    write_xlsx(result_file, wb_data)
    # Show result window to user.
    title = 'Results'
    comment = DESCRIPTION +\
              f'\nStart date: {start_dt}' +\
              f'\nEnd date: {end_dt}' +\
              '\nDone.'
    result_window(title, comment, link=result_folder)
    print('\nAnalysis was successfully finished.')

if __name__ == '__main__':
    main()
