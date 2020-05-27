import urllib.request
import m3u8
import streamlink
import subprocess
import os
import datetime;

def record_stream(url,iterations,tmp_folder,output_file):
    start_time = ts = datetime.datetime.now().timestamp()
    prev_data = ""
    tmp_folder=tmp_folder.rstrip('/')
    counter = 0
    while counter != iterations:
        streams = streamlink.streams(url)
        stream_url = streams["best"]
        m3u8_obj = m3u8.load(stream_url.args['url'])
        str_uri = m3u8_obj.segments[0].uri
        filedata = urllib.request.urlopen(str_uri).read()

        if filedata != prev_data:
            f = open(tmp_folder+'/tmp-'+str(counter)+'.ts', 'ab+')
            f.write(filedata)
            f.close()
            prev_data = filedata
            counter+=1
            print('[INFO] Writing segment '+str(counter)+'. File path - '+tmp_folder+'/tmp-'+str(counter)+'.ts. Left '+str(iterations-counter)+' segments or '+str((iterations-counter)*5)+' secs')

    txt_list = []
    for i in os.listdir(tmp_folder):
        txt_list.append('file '+i+'\n')

    list = open(tmp_folder+'/concat.txt','w+')
    list.writelines(txt_list)
    list.close()

    print('[INFO] Stream downloaded. Merging all files to '+output_file)
    os.chdir(tmp_folder)
    subprocess.call('ffmpeg -f concat -safe 0 -i concat.txt -c copy ../'+output_file+' -hide_banner -loglevel panic')
    print('[INFO] Merge successful. Removing tmp files')
    os.chdir('../')
    for i in os.listdir(tmp_folder):
        os.remove(tmp_folder+'/'+i)
    print('[INFO] Successfully deleted')
    print('[INFO] Recording time - '+str(datetime.datetime.now().timestamp() - start_time)+'s ')

print("[+] Enter url: ")
uri = input()
while not uri:
    print("[+] Enter url(example - https://www.youtube.com/watch?v=nsN6AiOAdII): ")
    uri = input()

print("[+] Enter record time in seconds: ")
iter = int(input()) // 5

try:
    os.mkdir('./stream-tmp/')
except OSError:
    print('[INFO] Not creating folder ./stream-tmp - it already exists')

try:
    os.mkdir('./result/')
except:
    print('[INFO] Not creating folder ./result - it already exists')
if os.listdir('stream-tmp'):
    print('[INFO] Something found in ./stream-tmp folder. Deleting...')
    for i in os.listdir('stream-tmp'):
        os.remove('./stream-tmp/'+i)
    print('[INFO] Successfully deleted')

print('[INFO] Starting stream recorder')

ts = datetime.datetime.now().timestamp()
record_stream(uri,iter,'stream-tmp','result/stream-'+str(round(ts))+'.mp4')