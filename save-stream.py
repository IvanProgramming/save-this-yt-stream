import urllib.request
import m3u8
import streamlink
import subprocess
import os
import datetime
import sys


def merge_all(tmp_folder, output_file):
    txt_list = []
    start_time = datetime.datetime.now().timestamp()
    for file_name in os.listdir(tmp_folder):
        txt_list.append('file ' + file_name + '\n')

    file_list = open(tmp_folder + '/concat.txt', 'w+')
    file_list.writelines(txt_list)
    file_list.close()

    print('[INFO] Stream downloaded. Merging all files to ' + output_file)
    os.chdir(tmp_folder)
    subprocess.call('ffmpeg -f concat -safe 0 -i concat.txt -c copy ../' + output_file +
                    ' -hide_banner -loglevel panic')
    print('[INFO] Merge successful. Removing tmp files')
    os.chdir('../')
    for file_name in os.listdir(tmp_folder):
        os.remove(tmp_folder + '/' + file_name)
    print('[INFO] Successfully deleted')
    print('[INFO] Merge time - ' + str(round(datetime.datetime.now().timestamp() - start_time)) + 's')


def record_stream(url,iterations,tmp_folder,output_file,block_size=20):
    start_time = datetime.datetime.now().timestamp()
    prev_data = ""
    tmp_folder = tmp_folder.rstrip('/')
    counter = 0
    segment_duration = 0
    while counter != iterations:
        tmp_file_path = tmp_folder + '/tmp-'+str(counter // block_size)+'.ts'

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
                    float(subprocess.getoutput('ffmpeg -i tmp-'+str(counter // block_size)+'.ts -hide_banner')
                      .split('\n')[1]
                      .split(', ')[0][-5:])
                )
                os.chdir('../')
            prev_data = filedata
            counter += 1
            print('[INFO] Writing segment '+str(counter)+'. File path - '+tmp_file_path+'. Left '+str(iterations-counter)+' segments')
    merge_all(tmp_folder, output_file)
    print('[INFO] Total time - '+str(round(datetime.datetime.now().timestamp() - start_time))+'s')


try:
    os.mkdir('./stream-tmp/')
except OSError:
    print('[INFO] Not creating folder ./stream-tmp - it already exists')

try:
    os.mkdir('./result/')
except OSError:
    print('[INFO] Not creating folder ./result - it already exists')
if os.listdir('stream-tmp'):
    print('[INFO] Something found in ./stream-tmp folder. Try to merge files into mp4, or Remove?[Y/n]')
    input = input()
    if input.capitalize() == 'Y' or input.capitalize() == 'YES' or input == '':
        merge_all('stream-tmp', 'result/recovered-stream.mp4')
        sys.exit()
    else:
        for i in os.listdir('stream-tmp'):
            os.remove('./stream-tmp/'+i)
        print('[INFO] Successfully deleted')


print("[+] Enter url: ")
uri = input()
while not uri:
    print("[+] Enter url: ")
    uri = input()

print("[+] Enter quanity of segmets(1 segment - from 1 to 10 seconds): ")
iter = int(input())


print('[INFO] Starting stream recorder')

ts = datetime.datetime.now().timestamp()
try:
    record_stream(uri, iter, 'stream-tmp', 'result/stream-'+str(round(ts))+'.mp4')
except KeyboardInterrupt:
    try:
        print('[INFO] CTRL-C Detected. Finishing proccess')
        merge_all('stream-tmp', 'result/user_finished.mp4')
    except KeyboardInterrupt:
        pass
