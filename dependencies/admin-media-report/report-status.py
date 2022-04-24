from pprint import pprint
from pymediainfo import MediaInfo
from os import listdir
from os.path import isfile, join

media_path = "C:\Transcode"


def get_media_info(path):
    media_info = MediaInfo.parse(path)
    result = {}
    result['path'] = path
    for track in media_info.tracks:
        if track.track_type == 'General':
            result['extension'] = track.file_extension
            result['name'] = track.file_name
            result['duration'] = track.duration
            result['readable_duration'] = track.other_duration[0]
            result['file_size'] = track.file_size
            result['readable_file_size'] = track.other_file_size[0]
        elif track.track_type == 'Video':
            codec = track.internet_media_type.split('/')[-1]
            result['codec'] = codec
    return result



media_files = [join(media_path, f) for f in listdir(media_path) if f.endswith(('.mp4','.mkv','.avi','.m4v','mpeg','mpg')) and isfile(join(media_path, f))]

for video in media_files:
    mi = get_media_info(video)
    print(mi)