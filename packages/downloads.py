
import sys
from pathlib import Path
from collections import OrderedDict
sys.path.append(str(Path(__file__).parent))

from get_url import get_multipage_url
from constants import PROJ_URL

def to_dict(data,
            key, value, order=False):
    """
    Converts list of dictionaries into dictionary.
    Finds pairs (key, value) in list dicts and
    creates new dict from (key, value) pairs.
    data: [
    {...},
    {...},
    ....]

    Args:
        data (list of dicts): input data;
        key: key in dict from data;
        value: value which corresponds to key;

    Return:
        _dict (dict): new dict with (key, value) pairs.
    """

    _dict = OrderedDict() if order else {}

    try:

        for row in data:

            _dict[row[key]] = row[value]

        return _dict

    except KeyError:
        print(f'Could not convert data to dict: {key}{value}.')
        exit()

def download_issues(proj_url=PROJ_URL):
    """
    Downloads all project issues, labels and label colors from proj_url.
    Convert downloaded issues, labels and label colors to dicts.

    Args:
        proj_url (str, default=PROJ_URL): project url;

    Return:
        issues (dict): dict with project issues, (key, value) = (issue_iid, issue_title)
        labels (dict): dict with project labels, (key, value) = (label_id, label_name)
        colors (dict): dict with label colors, (key, value) = (label_id, color)
    """

    raw_issues, _ = get_multipage_url(url=f'{proj_url}/issues')
    issues = to_dict(raw_issues, key='iid', value='title')
    
    return issues

if __name__ == '__main__':
    # download_issues_and_labels()
    pass
