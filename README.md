youtube-dl-server
=================

Interface and code forked from [`manbearwiz/youtube-dl-server`](https://github.com/manbearwiz/youtube-dl-server) to provide a single location to save YouTube videos as MP3s using [`bottle`](https://github.com/bottlepy/bottle) + [`youtube-dl`](https://github.com/rg3/youtube-dl).

Also includes an option to use a YouTube API key to search for videos and automagically download the top result as an MP3

![screenshot][1]

How to use this image
---------------------

### Run on host networking

This example uses host networking for simplicitly. Also note the `-v` argument. This directory will be used to output the resulting videos

```
sudo docker run -d --net="host" --name youtube-dl -v /home/scott/youtube-dl:/youtube-dl shuaiscott/youtube-dl-server
```

### Start a download remotely

Downloads can be triggered by supplying the `{{url}}` of the requested video through the Web UI or through the REST interface via curl, etc.

#### HTML

Just navigate to `http://{{address}}:8080/yt` and enter the requested `{{url}}`.

#### Curl

```
curl -X POST --data-urlencode "url={{url}}" http://{{address}}:8080/youtube-dl/q
```

### Search for a video

Searches can be triggered by supplying the `{{artist}}`, `{{title}}`, and `{{album}}` through the Web UI or through the REST interface via curl, etc.

#### Curl

```
curl -X POST --data-urlencode "artist={{artist}}" --data-urlencode "title={{title}}" --data-urlencode "album={{album}}" http://{{address}}:8080/yt/search
```

Implementation
--------------

The server uses [`bottle`](https://github.com/bottlepy/bottle) for the web framework and [`youtube-dl`](https://github.com/rg3/youtube-dl) to handle the downloading. For better or worse, the calls to youtube-dl are made through the shell rather then through the python API.

This docker image is based on [`python:3-onbuild`](https://registry.hub.docker.com/_/python/) and consequently [`debian:jessie`](https://registry.hub.docker.com/u/library/debian/).

There is now a start-up script that updates all pip libraries so you'll always have the latest version of youtube-dl. To update, just restart the docker container.

Thanks to
----------
CodePen: [Material "toast" notification](http://codepen.io/Dannzzor/pen/YXxaLE/) by Danny Davenport ([@Dannzzor](http://codepen.io/Dannzzor)) on [CodePen](http://codepen.io).



[1]: https://raw.githubusercontent.com/shuaiscott/youtube-dl-server/master/youtube-dl-server.png
