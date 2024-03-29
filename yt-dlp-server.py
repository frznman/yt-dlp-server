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
from yt_dlp.postprocessor.common import PostProcessor

app = Bottle()

@app.route('/yt')
def index_static():
    return static_file('index.html', root='./')

@app.route('/yt/static/:filename#.*#')
def server_static(filename):
    return static_file(filename, root='./static')

@app.route('/yt/q', method='GET')
def q_size():
    return { "success" : True, "size" : dl_q.qsize() }

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

    search = f'{artist} {title} Lyric Video'

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
    mp3_postprocessor = {
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '0',
    }

    opus_postprocessor = {
    'key': 'FFmpegExtractAudio',
    'preferredcodec': item.ext,
    }

    metadata_postprocessor = {
    'key': 'FFmpegMetadata',
    'add_metadata': True
    }

    ydl_opts = {
    'format': 'bestaudio/best',
    'paths': {
        'home': '/downloads/'
    },
    'outtmpl': '%(artist)s-%(album)s-%(track)s-[%(id)s]-(%(title)s).%(ext)s'
    }
    if item.ext == 'mp3': ydl_opts['postprocessors'] = [mp3_postprocessor, metadata_postprocessor]
    if item.ext in ['opus', 'ogg', 'webm']: ydl_opts['postprocessors'] = [opus_postprocessor, metadata_postprocessor]

    if item.url is not None:
        print("Starting download of " + item.url)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.add_post_processor(AddID3ArtworkPP())
            ydl.download([item.url])

        print("Finished downloading " + item.url)
    else:
        print(f'Starting download {item.artist}-{item.title}')

        if item.artist is not None and item.album is not None:
            ydl_opts['paths']['home'] = f'/downloads/{item.artist}/{item.album}/'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.add_post_processor(AddID3ArtworkPP())
            ydl.extract_info(f'ytsearch:{item.artist} {item.title} Lyric Video', extra_info={'artwork': item.artwork})
            
        print(f'Finished downloading {item.artist}-{item.title}')

class DownloadItem(object):
    def __init__(self, url=None, artist=None, title=None, album=None, artwork=None, ext='opus'):
        self.url = url
        self.artist = artist
        self.title = title
        self.album = album
        self.artwork = artwork
        self.ext = ext

class AddID3ArtworkPP(PostProcessor):
  def run(self, info):
    if info['ext'] != 'mp3':
      self.to_screen('Not MP3, skipping ID3 tag update')
      return [], info
    self.to_screen('Setting ID3 Tags')
    filepath = info['filepath']
    try:
        song = EasyID3(filepath)
    except mutagen.id3.ID3NoHeaderError:
        song = mutagen.File(filepath, easy=True)
        song.add_tags()
    if info['artwork'] is not None:
        try:
            audio = ID3(filepath)
            with urllib.request.urlopen(info['artwork']) as albumart:
                audio['APIC'] = APIC(
                    encoding=3,
                    mime=albumart.info().get_content_type(),
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
    return [], info

# Start queue and app

dl_q = Queue();
done = False;
dl_thread = Thread(target=dl_worker)
dl_thread.start()

print("Started download thread")

app.run(host='0.0.0.0', port=8080, debug=False)
done = True
dl_thread.join()
