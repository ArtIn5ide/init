import sys
import copy
from pathlib import Path
from re import search
sys.path.append(str(Path(__file__).parent))

from get_url import get_multipage_url
from json_handler import load_json, save_to_json
from constants import PROJ_URL, LABELS, LABEL_ADD, LABEL_REMOVE

def filter_data(response):
    """Trim any excess data from raw Gitlab API response. 

    Args:
        response (dictionary): Raw Gitlab API response

    Returns:
        (dictionary): filtered tool history
        Unit example:
        "<issue_id>":{
            "<message_id>":{
                "date"  : "created_at",
                "action": "added / removed",
                "label" : "",
                "user"  : "author['name']"
            }
        }
    """
    formatted_history = {}
    for message in response:
        try:
            adds = LABEL_ADD.search(message['body'])
            removes = LABEL_REMOVE.search(message['body'])

            removes = [] if removes is None else removes[0].strip().split(' ')
            adds = [] if adds is None else adds[0].strip().split(' ')

            id_increment = 1 / ( len(adds) + len(removes) )
            message_id = int(message['id'])

            for add in adds:
                add = add.replace('~','')
                formatted_history[message_id] =\
                    {
                        'date': message['created_at'],
                        'label': LABELS[add],
                        'user': message['author']['name'],
                        'action': 'add'
                    }
                message_id += id_increment

            for remove in removes:
                remove = remove.replace('~','')
                formatted_history[message_id] =\
                    {
                        'date': message['created_at'],
                        'label': LABELS[remove],
                        'user': message['author']['name'],
                        'action': 'remove'
                    }
                message_id += id_increment
        except:
            # Ignore lables, which are not related to tool statuses
            continue
    return formatted_history


def download_old_history(issue, url=PROJ_URL):
    """
    Downloads history of issue labels change by old Gitlab API (before 11.3 version).
    Then the history is transformed into new Gitlab API label history format.

    Args:
        issue_id (int): id of issue in question;
        labels (dict): dict with project issues: (label_id, label_name);
        colors (dict): dict with label colors, (key, value) = (label_id, color);
        url (string, default=PROJ_URL): project url;

    Return:
        history (dict): dict with (key, value) = (issue_iid, list with history of labels change);
        history:
        {
            "<issue_id>":{
			    "<message_id>":{
                "date"  : "created_at",
                "action": "added / removed",
                "label" : "",
                "user"  : "author['name']"
			    }
		    },
            "Old ID offset": <max integer ID>
        }
    """

    issue_id = issue[0]
    issue_name = issue[1]
    json_file = Path(fr'./history/{issue_name}.json').resolve()

    if not json_file.exists():

        full_url = f'{url}/issues/{issue_id}/notes'  # old full_url to issues history

        raw_issue_history, _ = get_multipage_url(full_url)

        # Remove extra lines from raw_issue_history,
        # which do not contain label changes (such as comments)
        issue_history = filter_data(raw_issue_history)

        issue_history = {issue_id: issue_history}
        issue_history['ID offset'] = int(max(issue_history[issue_id].keys())) if issue_history[issue_id] else 0
    else:
        issue_history = load_json(json_file)
    return issue_history, issue


if __name__ == '__main__':
    pass
