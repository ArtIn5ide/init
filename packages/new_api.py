
import sys
import concurrent.futures
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from get_url import get_multipage_url
from constants import PROJ_URL, END, DT_FORMAT, LABELS, COLORS
from json_handler import load_json, save_to_json
from datetime import datetime 

def filter_data(response, id_offset):
    """Trim any excess data from raw Gitlab API response.

    Args:
        response (dictionary): Raw Gitlab API response
    Returns:
        (dictionary): filtered tool history 
        Unit example:
        "<issue_id>":{
            "<message_id>":{
                "date"  : "date",
                "action": "add / removed",
                "label" : "",
                "user"  : "full name"
            }
		}
    """  

    formatted_history = {}
    for message in response:
        try:
            label_id = message['label']['id']
            message_id = message['id']
            if str(label_id) in LABELS:
                formatted_history[str(id_offset + message_id)] =\
                    {
                        'date': message['created_at'],
                        'label': message['label']['name'],
                        'user': message['user']['name'],
                        'action': message['action']
                    }
            else:
                continue
        except:
            # Ignore deleted labels
            continue
    return formatted_history

def download_history(old_history, issue, url=PROJ_URL):
    """
    Downloads history of issue labels change by new Gitlab API, since GitLab 11.3 version.

    Args:
        issues (dict): dict with project issues: (issue_iid, issue_title);
        labels (dict): dict with project issues: (label_id, label_name);
        url (string, default=PROJ_URL): project url;

    Return:
        history (dict): dict with (key, value) = (issue_iid, list with history of labels change)
        Unit example:
        "<issue_id>":{
            "<message_id>":{
                "date"  : "date",
                "action": "add / removed",
                "label" : "",
                "user"  : "full name"
            }
		}
    """
    issue_id = issue[0]
    issue_name = issue[1]
    
    issue_file = Path(fr'./history/{issue_name}.json').resolve()
    id_offset = int(old_history['ID offset'])
    page_offset = old_history['Last new API page'] if 'Last new API page' in old_history else 1
    
    full_url = f'{url}/issues/{issue_id}/resource_label_events'
    issue_history, page_offset = get_multipage_url(url=full_url, starting_page=page_offset)
    old_history['Last new API page'] = page_offset
    
    issue_history = filter_data(issue_history, id_offset)
    old_history[issue_id].update(issue_history)

    old_history[issue_id] =\
        {
            key: value for key, value in sorted(old_history[issue_id].items(), key=\
                lambda x: (
                datetime.strptime(x[1]['date'], DT_FORMAT),
                x[1]['action']))
        }
    save_to_json(issue_file, old_history)
    
    # Change format from long-term storage to more pliable
    del old_history['Last new API page']
    del old_history['ID offset']
    old_history[issue_id] = [value for value in old_history[issue_id].values()]
    
    return old_history

def to_new_form(input_history):
    """
    Transforms input history to new format.
    Walks through input history, setting the date to corresponding label.
    If both dates are set, appends to the result

    input_history form:
        [{'action': 'add',
            'date': '2018-03-27T07:09:46.768Z',
            'label': '',
            'user': ''
        },
        {'action': 'remove',
            'date': '2018-03-27T07:09:46.768Z',
            'label': '', 'user': ''
        }, 
        ...]
     output_history form:
        {issue_id1: [
            {'added': u'2018-03-19T11:24:32.866Z',
             'id': 316,
             'removed': u'2018-03-19T11:26:45.761Z'}
            {'added': u'2018-04-03T08:22:17.666Z',
             'id': 320,
             'removed': u'2018-04-03T11:31:06.041Z'},
            ...],
         issue_id2:[
            ...],
         ...}

    Args:
        input_history (dict): input data to be transformed;

    Return:
        output_history (dict): output data in new form.
    """

    output_history = {}

    for iid, hist in input_history.items():
        data = []
        tmp = {label:
               {
                   'id': key,
                   'added': None,
                   'removed': None
               } for key, label in LABELS.items()}

        for entry in hist:
            label_name = entry['label']
            
            if entry['action'] == 'add':
                tmp[label_name]['added'] = entry['date']
                tmp[label_name]['removed'] = None
            
            elif entry['action'] == 'remove':
                tmp[label_name]['removed'] = entry['date']

            if tmp[label_name]['removed'] and tmp[label_name]['added']:
                data.append(tmp[label_name].copy())
                tmp[label_name]['added'] = None
                tmp[label_name]['removed'] = None

        for entry in tmp.values():
            if entry['added'] != None and entry['removed'] == None:
                entry['removed'] = END.strftime(DT_FORMAT)
                data.append(entry)

        output_history[iid] = data
    return output_history

if __name__ == '__main__':
    pass
