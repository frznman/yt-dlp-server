#
# youtube-dl Server Dockerfile
#
# https://github.com/frznman/yt-dlp-server
#

# Pull base image.
FROM python:3-alpine

COPY . /usr/src/app/

WORKDIR /usr/src/app/

# Install GCC, ffmpeg, and required pip packages
RUN \
  apk add --no-cache ffmpeg && \
  apk add --no-cache --virtual .build-deps gcc musl-dev && \
  pip install -r ./requirements.txt && \
  apk del .build-deps && \
  rm -rf /var/lib/apt/lists/* && \
  chmod 777 ./updateAndRun.sh
  
EXPOSE 8080

VOLUME ["/downloads"]

CMD [ "./updateAndRun.sh" ]
