import urllib2
import sys
import time
import argparse
from os import path
from urlparse import parse_qs
from urllib2 import URLError

class VideoInfo(object):
    def __init__(self, video_url):
        request_url = 'http://www.youtube.com/get_video_info?video_id='
        if 'http://www.youtube.com/watch?v' in parse_qs(video_url).keys():
            request_url += parse_qs(video_url)['http://www.youtube.com/watch?v'][0]
        elif 'https://www.youtube.com/watch?v' in parse_qs(video_url).keys():
            request_url = 'https://www.youtube.com/get_video_info?video_id='+parse_qs(video_url)['https://www.youtube.com/watch?v'][0]
        elif 'v' in parse_qs(video_url).keys():
            request_url += parse_qs(video_url)['v'][0]
        else :
            sys.exit('Invalid URL' % video_url)
        request = urllib2.Request(request_url)
        try:
            self.video_info = parse_qs(urllib2.urlopen(request).read())
        except URLError :
            sys.exit('Invalid URL' % video_url)

def getTitle(videoinfo):
    if not isinstance(videoinfo, VideoInfo):
        sys.exit('Invalid VideoInfo')
    title = videoinfo.video_info['title'][0].decode('utf-8')
    return title

def getVideoURLS(videoinfo):
    if not isinstance(videoinfo, VideoInfo):
        sys.exit('Invalid VideoInfo')
    url_encoded_fmt_stream_map = videoinfo.video_info['url_encoded_fmt_stream_map'][0].split(',')
    entrys = [parse_qs(entry) for entry in url_encoded_fmt_stream_map]
    url_maps = [dict(url=entry['url'][0], type=entry['type']) for entry in entrys]
    return url_maps

def downloader(url, filename, prefix_message=''):
    request=urllib2.Request(url)
    file=open(filename, 'wb')
    link=urllib2.urlopen(request)
    meta=link.info()
    filesize=int(meta.getheader('Content-Length'))
    buff_size=16384
    downloaded_size=0
    print "Downloading "+filename+"\n"
    while True:
        buffer = link.read(buff_size)
        if not buffer:
            break
        downloaded_size += len(buffer)
        file.write(buffer)
        display = '%s .... %d of %d' %(filename, downloaded_size, filesize)
        sys.stdout.write("\r"+display)
        sys.stdout.flush()
    time.sleep(1)
    sys.stdout.write('\n')
    sys.stdout.flush()
    print "Done!\n\n"
    file.close()

def getVideoID(playlist):
    reference = "thumb-menu dark-overflow-action-menu video-actions"
    response = urllib2.urlopen(playlist)
    pagecode = str(response.read())
    lastocur = pagecode.rfind(reference)
    pagecode = pagecode[0:lastocur-1]
    lastocur = pagecode.rfind(reference)
    filteredcode = pagecode[lastocur:lastocur+1000]
    filteredcode = filteredcode[filteredcode.find("data-video-ids"):len(filteredcode)]
    return filteredcode[filteredcode.find("=")+2:filteredcode.find(">")-1]

def getPlaylistAmount(playlist):
    reference = "thumb-menu dark-overflow-action-menu video-actions"
    response = urllib2.urlopen(playlist)
    pagecode = str(response.read())
    return pagecode.count("thumb-menu dark-overflow-action-menu video-actions")-1

def main():
    playlisturl = "https://www.youtube.com/playlist?list=xxxxxxx"
    print "YouTube playlist bot\n"
    amount = getPlaylistAmount(playlisturl)
    #amount = 0
    parser = argparse.ArgumentParser()
    parser.add_argument('url', metavar='url', type=str)
    parser.add_argument('type', metavar='type', type=str)
    while True:
        actualamount = getPlaylistAmount(playlisturl)
        if actualamount != amount:
            print "New video added!\n"
            url_str = "https://www.youtube.com/watch?v="+getVideoID(playlisturl)
            type = 'video/mp4'
            video_info = VideoInfo(url_str)
            video_url_map = getVideoURLS(video_info)
            video_title = getTitle(video_info)
            url = ''
            for entry in video_url_map:
                entry_type = entry['type'][0]
                entry_type = entry_type.split(';')[0]
                if entry_type.lower() == type.lower():
                    url = entry['url']
                    break
            downloader(url, video_title+'.mp4')
            amount = actualamount
        time.sleep(60)


if __name__ == "__main__":
    main()
