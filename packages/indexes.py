
import sys
from pathlib import Path
from collections import OrderedDict
import numpy as np

sys.path.append(str(Path(__file__).parent))

from .constants import UPTIME_LABELS, DOWNTIME_LABELS

def total_labels_time(data, label_ids):
    """
    Calculates total time of labels (which is in label_ids list) from data.
    data:
        data = {label_id1: label_time1,
                label_id2: label_time2,
                ...,
                label_idN: label_timeN}

    Args:
        data (dict): contains each label times: (label_id, label_time);
        label_ids (list): list of label ids;

    Return:
        total (float): total time of labels (which is in label_ids) from data.
    """

    total = 0.

    for label_id in label_ids:
        total += data[label_id]

    return total

def label_change_count(data,
                       src_label_ids, dst_label_ids):
    """
    Count number of label changes
    from src_label_ids (list) to dst_label_ids (list).

    data in the form:
        [{'added': u'2018-03-19T11:24:32.866Z',
          'id': 316,
          'removed': u'2018-03-19T11:26:45.761Z'},
         {'added': u'2018-03-19T11:33:04.358Z',
          'id': 317,
          'removed': u'2018-03-20T10:37:13.723Z'},
         {'added': u'2018-03-20T10:37:13.723Z',
          'id': 320,
          'removed': u'2018-03-21T07:44:47.498Z'},
         {'added': u'2018-03-21T07:44:47.498Z',
          'id': 316,
          'removed': u'2018-04-03T08:22:17.666Z'}]

    Args:
        data (list of dict): data for analysis;
        src_label_ids (list): list of source label ids;
        dst_label_ids (list): list of destination label ids;

    Return:
        N (int): number of label changes from src_labels to dst_labels.
    """

    N = 0

    for i in range(len(data[:-1])):

        if data[i]['id'] in src_label_ids and data[i+1]['id'] in dst_label_ids:
            N = N + 1

    return N

def value_by_multikey(_dict, keys):
    """
    Function extracts that values from dictionary by list of keys.

    Args:
        dict (dict): dictionary;
        keys (list): list of keys;

    Return:
        list of values: values corresponding to keys list.
    """

    return [_dict[key] for key in keys]

def average(indexes, index_name):
    """
    Finds average value of 'index_name' index for all issues (tools).

    Args:
        indexes (dict): dict with indexes values for all issues;
        index_name (str): index name;

    Return:
        average value (float): average value of 'index_name' index.
    """

    values = [indexes[iid][index_name] for iid in indexes.keys()
              if indexes[iid][index_name] is not None]

    return np.average(values) if len(values) > 0 else None 

def calculate_indexes(summary,
                      history,
                      labels):
    """
    Function for calculation of main production indexes.
    For detailed indexes description, see: http://llccmt.mapperllc/ShowItem?docid=7355
    Indexes:
    * total         * uptime        * downtime
    * service_kpi   * service_kpi_% * MTBF
    * EDU           * OU            * MTTR
    * MTOL          * MTBD          * PII

    Args:
        summary (dict): dict with the summary time
                        for each issue (tool) for each label (state);
        history (dict): label changes history for each issue;
        labels (dict): dict with project labels, (key, value) = (label_id, label_name);

    Return:
        indexes (dict): dict with main production indexes (for each issue <=> tool);
        average_indexes (dict): dict with average values of main production indexes.
    """

    labels = OrderedDict((value, key) for key, value in labels.items())
    indexes = {}

    for iid, data in history.items():

        tmp = {}

        # Calculate total time for all status [days].
        label_ids = labels.values()
        tmp['total'] = total_labels_time(summary[iid], label_ids)

        # Calculate total time for uptime status:
        # 'Up', 'Contamination', 'SPC', 'Out of control' [days].
        label_ids = value_by_multikey(labels, UPTIME_LABELS)
        tmp['uptime'] = total_labels_time(summary[iid], label_ids)

        # Calculate Operational Uptime index [%]
        tmp['OU'] = 100.*tmp['uptime']/tmp['total'] if tmp['total'] > 0.0 else None

        # Calculate total time for downtime status:
        # 'Down', 'Maintenance', 'No facility', 'Conditioning' [days].
        label_ids = value_by_multikey(labels, DOWNTIME_LABELS)
        tmp['downtime'] = total_labels_time(summary[iid], label_ids)

        # Calculate Service KPI index [days]: 'Total' - 'Down'.
        down_id = labels['Down']
        tmp['service_kpi'] = tmp['total'] - summary[iid][down_id]

        # Calculate Service KPI index [%].
        tmp['service_kpi_%'] = 100.*tmp['service_kpi']/tmp['total'] if tmp['total'] > 0.0 else None

        # Calculate Mean Productive Time Between Failures index [days].
        src_label_ids = value_by_multikey(labels, UPTIME_LABELS)
        dst_label_ids = [labels['Down']]
        number = label_change_count(data, src_label_ids, dst_label_ids)
        tmp['MTBF'] = tmp['uptime']/number if number > 0 else None

        # Calculate Equipment Dependent Uptime [%].
        label_ids = list(labels.values())
        label_ids.remove(labels['No facility'])
        time = total_labels_time(summary[iid], label_ids)
        tmp['EDU'] = 100.*tmp['uptime']/time if time > 0. else None

        # Calculate Mean Time To Repair index [days].
        src_label_ids = value_by_multikey(labels, UPTIME_LABELS)
        dst_label_ids = [labels['Down']]
        number = label_change_count(data, src_label_ids, dst_label_ids)
        time = total_labels_time(summary[iid], dst_label_ids)
        tmp['MTTR'] = time/number if number > 0 else None

        # Calculate Mean Time Off-line index [days].
        src_label_ids = value_by_multikey(labels, UPTIME_LABELS)
        dst_label_ids = value_by_multikey(labels, DOWNTIME_LABELS)
        number = label_change_count(data, src_label_ids, dst_label_ids)
        tmp['MTOL'] = tmp['downtime']/number if number > 0 else None

        # Calculate Mean Time Between Deviation index [days].
        label_ids = [labels['Up']]
        src_label_ids = value_by_multikey(labels, ['Up', 'SPC', 'Contamination'])
        dst_label_ids = [labels['Out of control']]
        time = total_labels_time(summary[iid], label_ids)
        number = label_change_count(data, src_label_ids, dst_label_ids)
        tmp['MTBD'] = time/number if number > 0 else None

        # Calculate Process Instability Index [%].
        label_ids = [labels['Out of control']]
        time = total_labels_time(summary[iid], label_ids)
        tmp['PII'] = 100.*time/tmp['uptime'] if tmp['uptime'] > 0.0 else None

        indexes[iid] = tmp

    # Calculate average values of all production indexes.
    index_names = list(indexes.values())[0].keys()
    average_indexes = {}

    for index_name in index_names:
        average_indexes[index_name] = average(indexes, index_name)

    return indexes, average_indexes

def verify_indexes(indexes, specs, stack=False):
    """
    Verifies each index in 'indexes' whether it is in 'specs' or not.
    'stack' flag separate verification for 2 different 'indexes' structures
    (see function code).
    For stack=True: indexes = {
                        issue_iid1:{
                        index_name1: index_value1,
                        ....
                        index_nameN: index_valueN},
                        issue_iid2:{...},
                        ...}
    For stack=False: indexes = {
                        index_name1: index_value1,
                        ....
                        index_nameN: index_valueN}
    specs = {
        index_name1: {
            low: spec_val1,
            up: spec_val2
        },
        ...,
        index_nameN: {...}}

    Args:
        indexes (nested dict): input dict with indexes values;
        specs (dict with strs): input dict with specs for production indexes;
        stack (bool, default=False): flag which indicates the structure of
                                     input 'indexes';
    """

    result = {}

    if stack:
        for iid in indexes.keys():

            tmp = {}
            for ind_name in indexes[iid].keys():

                try:
                    # Try to load specs ('low' and 'up') for index: 'ind_name'.
                    low_spec = specs[ind_name]['low']
                    up_spec = specs[ind_name]['up']

                    # Verify 'indexes[iid][ind_name]' value.
                    tmp[ind_name] = in_spec(indexes[iid][ind_name], low_spec, up_spec)\
                                    if indexes[iid][ind_name] else True

                except KeyError:
                    tmp[ind_name] = True

            result[iid] = tmp

    else:
        for ind_name in indexes.keys():

            try:
                # Try to load specs ('low' and 'up') for index: 'ind_name'.
                low_spec = specs[ind_name]['low']
                up_spec = specs[ind_name]['up']

                # Verify 'indexes[ind_name]' value.
                result[ind_name] = in_spec(indexes[ind_name], low_spec, up_spec)\
                                   if indexes[ind_name] else True

            except KeyError:
                result[ind_name] = True

    return result

def in_spec(value, low_spec, up_spec):
    """
    Verifies whether  'low_spec' <= 'value' <= up_spec or not.

    Args:
        value (float): value;
        low_spec (str): low spec;
        up_spec (str): up_spec;
    """

    result = True
    if low_spec and up_spec:
        result = (float(low_spec) <= value) & (value <= float(up_spec))

    elif low_spec:
        result = (float(low_spec) <= value)

    elif up_spec:
        result = (value <= float(up_spec))

    return result

if __name__ == '__main__':
    pass
