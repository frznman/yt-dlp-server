import json
import os
import subprocess
import urllib.request
import urllib.error
from queue import Queue
from bottle import route, run, Bottle, request, static_file
from threading import Thread
import mutagen
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3
import yt_dlp

app = Bottle()

@app.route('/yt')
def dl_queue_list():
    return static_file('index.html', root='./')

@app.route('/yt/static/:filename#.*#')
def server_static(filename):
    return static_file(filename, root='./static')

@app.route('/yt/q', method='GET')
def q_size():
    return { "success" : True, "size" : json.dumps(list(dl_q.queue)) }

@app.route('/yt/q', method='POST')
def q_put():
    url = request.forms.get( "url" )
    if "" != url:
        dl_q.put( DownloadItem(url) )
        print("Added url " + url + " to the download queue")
        return { "success" : True, "url" : url }
    else:
        return { "success" : False, "error" : "yt called without a url" }

@app.route('/yt/search', method='GET')
def search():
    artist = request.params.get( "artist" )
    title = request.params.get( "title" )
    album = request.params.get( "album" )
    artwork = request.params.get( "artwork-url" )
    ext = request.params.get( "ext" )

    terms = [ artist, title, album ]
    search = ' '.join(filter(None, terms))

    if search is not None and "" != search:
        print( "Searching for: ", search )
        dl_q.put( DownloadItem(None, artist, title, album, artwork) )
        return { "success" : True }
    else:
        return { "success" : False, "error" : "yt called without a search query" }

def dl_worker():
    while not done:
        item = dl_q.get()
        download(item)
        dl_q.task_done()

def download(item):
    if item.url is not None:
        print("Starting download of " + item.url)
        command = ['/usr/local/bin/yt-dlp', '-f "ba"', '-o', '/downloads/%(title)s-%(id)s-%(artist)s-%(album)s-%(track)s.%(ext)s', '-x', item.url]
        if item.ext is "mp3": command.append('--audio-format=mp3')
        subprocess.call(command, shell=False)
        
        ydl_opts = {
            'format': 'bestaudio/best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(['https://www.youtube.com/watch?v=BaW_jenozKc'])
            print(json.dumps(ydl.sanitize_info(info)))
        
        print("Finished downloading " + item.url)
    else:
        print("Starting download of " + item.artist + " - " + item.title)
        filepath = "/downloads/{0}-{1}-{2}".format(item.artist, item.title, item.album)
        command = ['/usr/local/bin/yt-dlp', '-f "ba"', '-o', filepath+"-%(id)s-%(artist)s-%(album)s-%(track)s.%(ext)s", '-x', "ytsearch:{0} {1} {2} lyrics".format(item.artist, item.title, item.album)]
        if item.ext is "mp3": command.append('--audio-format=mp3')
        subprocess.call(command, shell=False)
        print("Finished downloading")
        filepath = filepath + ".mp3"
        print("Setting ID3 Tags")
        try:
            song = EasyID3(filepath)
        except mutagen.id3.ID3NoHeaderError:
            song = mutagen.File(filepath, easy=True)
            song.add_tags()
        song["artist"] = item.artist
        song["album"] = item.album
        song["title"] = item.title
        song.save()
        print("Saved ID3 Tag data")
        if item.artwork is not None:
            try:
                audio = ID3(filepath)
                with urllib.request.urlopen(item.artwork) as albumart:
                    audio['APIC'] = APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3, desc=u'Cover',
                        data=albumart.read()
                    )
                audio.save()
            except urllib.error.HTTPError as err:
                print(err.reason)
            finally:
                try:
                    sf.close()
                except NameError:
                    pass
        print("Saved Artwork Image")

class DownloadItem(object):
    def __init__(self, url=None, artist=None, title=None, album=None, artwork=None, ext=None):
        self.url = url
        self.artist = artist
        self.title = title
        self.album = album
        self.artwork = artwork
        self.ext = ext

# Start queue and app

dl_q = Queue();
done = False;
dl_thread = Thread(target=dl_worker)
dl_thread.start()

print("Started download thread")

app.run(host='0.0.0.0', port=8080, debug=True)
done = True
dl_thread.join()
diff --git a/youtube-dl-server.py b/youtube-dl-server.py
