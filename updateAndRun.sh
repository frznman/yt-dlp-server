#!/bin/sh
apk add --no-cache ffmpeg && \
pip install --upgrade -r ./requirements.txt && \
rm -rf /var/lib/apt/lists/*
python -u ./youtube-dl-server.py
