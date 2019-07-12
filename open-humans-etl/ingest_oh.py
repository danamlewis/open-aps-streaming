
from models import Treatment, Entry, Profile, DeviceStatus, DeviceStatusMetric
from utils.stream_ingester import StreamIngester
from helpers import get_connection
from utils.database import Database
import traceback
import json
import sys
import os


def get_user_filepaths(user_folder):

    nightscout_files = []

    for subdirs, dirs, files in os.walk(BASE_DIRECTORY + user_folder):

        for file in files:

            if '.json' in file and file not in nightscout_files:

                nightscout_files.append(f'{subdirs}/{file}')

    return nightscout_files


def get_user_records(file_paths):

    entries, treatments, profiles, device_status = [], [], [], []
    for file in file_paths:

        with open(file, encoding='utf-8') as f:
            records = json.load(f)

        if 'entries' in file.lower():
            [entries.append({**x, **{'app_id': user_folder, 'oh_source_entity': 'OpenAPS'}}) for x in records]

        elif 'treatments' in file.lower():
            [treatments.append({**x, **{'app_id': user_folder, 'oh_source_entity': 'OpenAPS'}}) for x in records]

        elif 'profile' in file.lower():
            [profiles.append({**x, **{'app_id': user_folder, 'oh_source_entity': 'OpenAPS'}}) for x in records]

        elif 'device' in file.lower():
            [device_status.append({**x, **{'app_id': user_folder, 'oh_source_entity': 'OpenAPS'}}) for x in records]

    status_metrics = [{**x['openaps'], **{'device_status_id': x['_id']}} for x in device_status if 'openaps' in x]

    mapper = {
        'treatment': {'entity': treatments, 'object': Treatment, 'table': 'treatments'},
        'entries': {'entity': entries, 'object': Entry, 'table': 'entries'},
        'profiles': {'entity': profiles, 'object': Profile, 'table': 'profile'},
        'status_metrics': {'entity': status_metrics, 'object': DeviceStatusMetric, 'table': 'device_status_metrics'},
        'devicestatus': {'entity': device_status, 'object': DeviceStatus, 'table': 'device_status'}
    }

    return mapper


def ingest(mapper):

        for k, v in mapper.items():

            temp_list = []
            try:

                for item in v['entity']:
                    with v['object'](item) as t:
                        temp_list.append(vars(t))

            except Exception:
                print(traceback.format_exc())
                sys.exit(666)

            if temp_list:

                unduplicated = [dict(t) for t in {tuple(d.items()) for d in temp_list}]

                # try:
                #     ingester.add_target(target_data=unduplicated,
                #                         output_schema='openaps',
                #                         table_name=v['table'],
                #                         date_format='YYYY-MM-DD HH24:MI:SS'
                #                         )
                # except Exception:
                #     print(traceback.format_exc())
                #     break


db = Database(get_connection())
ingester = StreamIngester(get_connection())
BASE_DIRECTORY = 'D:/Work/OpSci/openaps/src/ingest/openaps_data_2/'

user_folders = [x for x in next(os.walk(BASE_DIRECTORY))[1]]

count = 1
for user_folder in user_folders:

    print(f'{user_folder}: {count}/{len(user_folders)}')
    count = count + 1

    paths = get_user_filepaths(user_folder)
    mapper = get_user_records(paths)

    try:
        ingest(mapper)

    except Exception as e:
        print(f'{user_folder} ~ {str(e)}')
        continue
