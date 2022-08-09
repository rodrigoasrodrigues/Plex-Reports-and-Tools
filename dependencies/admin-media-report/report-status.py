from genericpath import isdir
from pprint import pprint
from pymediainfo import MediaInfo
from os import listdir
from os.path import isfile, join, isdir
from email_utils import *
from datetime import date, timedelta
import time

import yaml
import pandas as pd

library_template = 'templates/library-report.mjml'
admin_template = 'templates/admin-report.mjml'


def get_resolution(width):
    if width < 1280:
        return "SD"
    elif width < 1920:
        return "HD"
    elif width == 1920:
        return "FHD"
    else:
        return "UHD"

def get_media_info(path, libname):
    try:
        media_info = MediaInfo.parse(path)
        result = {}
        result['path'] = path
        result['libname'] = libname
        for track in media_info.tracks:
            if track.track_type == 'General':
                result['extension'] = track.file_extension
                result['name'] = track.file_name
                result['duration'] = track.duration
                result['readable_duration'] = track.other_duration[0]
                result['file_size'] = track.file_size
                result['readable_file_size'] = track.other_file_size[0]
            elif track.track_type == 'Video':
                # print(track.to_data())
                codec = track.internet_media_type
                if codec is None:
                    codec = track.commercial_name
                elif '/' in codec:
                    codec = codec.split('/')[-1]
                result['codec'] = codec
                result['resolution'] = get_resolution(track.width)
        result['size_duration_ratio'] = result['file_size'] / result['duration']
        return result
    except:
        print(f'Failed to get info: {path}')
        return None

def calculate_group_metrics(df, group):
    total = len(df)
    group_metrics = df.groupby([group]).size()
    group_items = group_metrics.keys()
    metrics = {}
    metrics[group] = group_items
    for group_item in group_items:
        metrics[group_item] = group_metrics[group_item]
        metrics[f'{group_item}_percent'] = str(round(group_metrics[group_item] * 100 / total, 2)) + '%'
    return metrics

def calculate_library_metrics(df, libname):
    metrics = {}
    metrics['libname'] = libname
    total = len(df)
    metrics['total'] = total
    metrics['metric_groups'] = ['codec', 'extension', 'resolution']
    for metric_group in metrics['metric_groups']:
        new_metrics = calculate_group_metrics(df, metric_group)
        metrics.update(new_metrics)
    return metrics

def apply_library_template(dic_library):
    return apply_template(dic_library, library_template)

def apply_admin_template(dic_library):
    return apply_template(dic_library, admin_template)

def build_library_email(list_info, lib_name):
    df_lib = pd.DataFrame(list_info)
    lib_metrics = calculate_library_metrics(df_lib, lib_name)
    mail = apply_library_template(lib_metrics)
    return mail

def get_file_list(path, recursive=False):
    result = []
    for f in listdir(path):
        full_path_f = join(path, f)
        if isfile(full_path_f) and f.endswith(media_endings):
            result.append(full_path_f)
        elif isdir(full_path_f) and recursive:
            result.extend(get_file_list(full_path_f, recursive))
    return result


start = time.time()

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    media_endings = tuple(config['video_extensions'])

all_media = []
libraries_mail = ""
for media_library in config['libs']:
    library_name = media_library["name"]
    print(f'processing {library_name}')
    media_path = media_library['path']
    recursive = False
    if 'recursive' in media_library:
        recursive = media_library['recursive']
    media_files = get_file_list(media_path, recursive)
    all_library_media = [x for x in
        (get_media_info(video, library_name) for video in media_files) if x]
    mail = build_library_email(all_library_media, library_name)
    libraries_mail += mail
    all_media.extend(all_library_media)

# saves csv for later analysis
df_all_media = pd.DataFrame(all_media)
df_all_media.to_csv(f'report_{str(date.today())}.csv',sep=';', header=True)

# do the same template for the entire media collection and add before all others
libraries_mail = build_library_email(all_media, 'All') + libraries_mail

report_elements = {}
report_elements['library-report'] = libraries_mail
report_elements['date'] = date.today()
end = time.time()
execution_time = end - start
report_elements['execute-time'] = str(timedelta(seconds=execution_time))
report_mail = apply_admin_template(report_elements)

# print(report_mail)
send_admin_report(report_mail, config)
