import json
from pathlib import Path

def save_to_json(path_to_json, history):
    """
    Saves data (history) to json file (path_to_json).

    Args:
        path_to_json (Path object): path to .json file;
        history : data to be written to .json file.
    """

    with path_to_json.open(mode='w') as json_file:
        json.dump(history, json_file,
                  indent=5, separators=(',', ': ')) # Last 2 args for pretty print

def load_json(path_to_json):
    """
    Loads data form .json file (path_to_json).

    Args:
        path_to_json (Path object): path to .json file.

    Return:
        data (OrderedDict class instance): json file data;
    """

    with path_to_json.open(mode='r') as json_file:
        data = json.load(json_file)

    return data

def load_config(filename):
    """
    Loads config (settings) from file with 'filename', which is in current folder.

    Args:
        filename(str): config file name;

    Return:
        config (OrderedDict class instance): config, which contains required info;
    """

    config_folder = Path(__file__).parent
    config_path = config_folder / filename

    if not config_path.is_file():
        msg = f'Config file does not exists: {str(config_path)}!'
        raise IOError(msg)

    config = load_json(config_path)

    return config

def parse_config(config, key):
    """
    Parses input 'config', i.e. finds 'key' word and
    returns data, which corresponds to 'key'.

    Args:
        config (OrderedDict class instance or dict): input config;
        key (str): key word to extract config data;

    Return:
        config_data (OrderedDict class instance or dict): extracted config data;
    """

    content = None
    config_data = None

    try:
        content = config[key]

    except KeyError:
        print(f'Could not extract data by key: {key}')

    if content:

        try:
            version = content.get('version')
            config_data = content[version]

        except KeyError:
            print('Could not extract config data')

    return config_data

if __name__ == '__main__':
    pass
