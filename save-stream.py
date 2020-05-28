# -*- coding: utf-8 -*-
import urllib.request
import m3u8
import streamlink
import subprocess
import os
import datetime
import math
import sys
from time import sleep
import glob

# level 0 - Detailed
# level 1 - Info
# level 2 - Success
# level 3 - Warning
# level 4 - Critical
# level 5 - Input
def log_print(msg, level=1, user_seted=1):
    user_seted = log_level
    level_names = {0:'DETAILED',1:'INFO',2:'SUCCESS',3:'WARNING',4:'CRITICAL',5:'+'}
    if level >= user_seted:
        print('[{0}] {1}'.format(level_names[level],msg))


def merge_all(tmp_folder, output_file):
    txt_list = []
    start_time = datetime.datetime.now().timestamp()
    for file_name in os.listdir(tmp_folder):
        txt_list.append('file ' + file_name + '\n')

    file_list = open(tmp_folder + '/concat.txt', 'w+')
    file_list.writelines(txt_list)
    file_list.close()

    log_print('Stream downloaded. Merging all files to {0}'
              .format(output_file),1)
    os.chdir(tmp_folder)
    ffmpeg_log = subprocess.getoutput('ffmpeg -f concat -safe 0 -i concat.txt -c copy ../{0}'
                                  .format(output_file))

    os.chdir('../')
    log_print('Merge complete. Checking file existence', 0)
    if os.path.isfile(output_file):
        log_print('Merge successful. Removing tmp files', 1)
        for file_name in os.listdir(tmp_folder):
            if 'tmp' in file_name or 'concat' in file_name:
                os.remove(tmp_folder + '/' + file_name)
        log_print('Successfully deleted', 0)
    else:
        log_print('Merge unsuccessful. Here is ffmpeg dump', 4)
        log_print(ffmpeg_log, 4)
        log_print('Stopping script. Try to check log and fix problem, then run script again and merge files again', 4)
        sys.exit()
    log_print('Merge time - {0} s'
              .format(round(datetime.datetime.now().timestamp() - start_time)), 0)


def record_stream(url, total_time, tmp_folder, output_file, block_size=20):
    start_time = datetime.datetime.now().timestamp()
    prev_data = ""
    tmp_folder = tmp_folder.rstrip('/')
    counter = 0
    segment_duration = 0
    total_iter = 1
    while counter != total_iter:
        tmp_file_path = tmp_folder + '/tmp-' + str(counter // block_size) + '.ts'

        streams = streamlink.streams(url)
        stream_url = streams["best"]
        m3u8_obj = m3u8.load(stream_url.args['url'])
        str_uri = m3u8_obj.segments[0].uri
        filedata = urllib.request.urlopen(str_uri).read()

        if filedata != prev_data:
            f = open(tmp_file_path, 'ab+')
            f.write(filedata)
            f.close()
            if segment_duration == 0:
                os.chdir(tmp_folder)
                segment_duration = round(
                    float(subprocess.getoutput('ffmpeg -i tmp-' + str(counter // block_size) + '.ts -hide_banner')
                          .split('\n')[1]
                          .split(', ')[0][-5:])
                )
                total_iter = math.ceil(total_time / segment_duration)
                log_print('Segment_duration sated to {0}. Basing on this data setting iterations to {1}'
                          .format(segment_duration, total_iter), 0)
                os.chdir('../')
            prev_data = filedata
            counter += 1
            log_print('Writing segment {0}. File path - {1} . Left {2} segments and {3} seconds'
                  .format(counter, tmp_file_path, total_iter - counter,(total_iter - counter)*segment_duration),1)
            sleep(segment_duration-1)
    merge_all(tmp_folder, output_file)
    log_print('Total time - {0} s'
              .format(round(datetime.datetime.now().timestamp() - start_time)), 1)


log_level = 0
log_print('Checking FFmpeg existence', 0)
ffmpeg_version = subprocess.getoutput('ffmpeg -version')
if 'Copyright' in ffmpeg_version.split('\n')[0]:
    log_print('FFmpeg exists', 2)
    log_print(ffmpeg_version.split('\n')[0], 0)
else:
    log_print('FFmpeg not found! Here is execute log:', 4)
    log_print(ffmpeg_version, 4)
    log_print('Check log, fix problem, then rerun script', 4)
    sys.exit()
try:
    os.mkdir('./stream-tmp/')
except OSError:
    log_print('Not creating folder ./stream-tmp - it already exists', 0)

try:
    os.mkdir('./result/')
except OSError:
    log_print('Not creating folder ./result - it already exists', 0)
if os.listdir('stream-tmp'):
    log_print('Something found in ./stream-tmp folder. Try to merge files into mp4, or Remove?[Y/n]', 5)
    input = input()
    if input.capitalize() == 'Y' or input.capitalize() == 'YES' or input == '':
        merge_all('stream-tmp', 'result/recovered-stream.mp4')
        sys.exit()
    else:
        for i in os.listdir('stream-tmp'):
            os.remove('./stream-tmp/' + i)
        log_print('Starting stream recorder', 2)

log_print('Enter url: ', 5)
uri = input()
while not uri:
    log_print('Enter url: ', 5)
    uri = input()

log_print('Enter time in seconds: ', 5)
time = int(input())

log_print('Starting stream recorder', 1)

ts = datetime.datetime.now().timestamp()
try:
    record_stream(uri, time, 'stream-tmp', 'result/stream-' + str(round(ts)) + '.mp4')
except KeyboardInterrupt:
    try:
        log_print('CTRL-C Detected. Finishing proccess', 4)
        merge_all('stream-tmp', 'result/user_finished.mp4')
    except KeyboardInterrupt:
        pass
