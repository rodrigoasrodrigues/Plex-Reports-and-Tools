from pprint import pprint
from pymediainfo import MediaInfo
from os import listdir
from os.path import isfile, join
from email_utils import *
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
            codec = track.internet_media_type.split('/')[-1]
            result['codec'] = codec
            result['resolution'] = get_resolution(track.width)
    result['size_duration_ratio'] = result['file_size'] / result['duration']
    return result

def calculate_library_metrics(df, libname):
    metrics = {}
    metrics['libname'] = libname
    total = len(df)
    metrics['total'] = total
    codec_metrics = df.groupby(['codec']).size()
    metrics['H264'] = codec_metrics['H264']
    metrics['H264_PERCENT'] = codec_metrics['H264'] / total
    metrics['H265'] = codec_metrics['H265']
    metrics['H265_PERCENT'] = codec_metrics['H265'] / total
    extension_metrics = df.groupby(['extension']).size()
    metrics['MP4'] = extension_metrics['mp4']
    metrics['MP4_PERCENT'] = extension_metrics['mp4'] / total
    metrics['MKV'] = extension_metrics['mkv']
    metrics['MKV_PERCENT'] = extension_metrics['mkv'] / total
    # resolution_metrics = df.groupby(['resolution']).size()
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

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

all_media = []
libraries_mail = ""
for media_library in config['libs']:
    library_name = media_library["name"]
    media_path = media_library['path']
    media_endings = tuple(config['video_extensions'])
    media_files = [join(media_path, f) for f in listdir(media_path) \
        if f.endswith(media_endings) and isfile(join(media_path, f))]

    all_library_media = [get_media_info(video, library_name) for video in media_files]
    mail = build_library_email(all_library_media, library_name)
    libraries_mail += mail
    all_media.extend(all_library_media)

#now do the same for the entire media collection
libraries_mail += build_library_email(all_media, 'All')

report_elements = {}
report_elements['library-report'] = libraries_mail

report_mail = apply_admin_template(report_elements)

print(report_mail)
send_admin_report(report_mail, config)
