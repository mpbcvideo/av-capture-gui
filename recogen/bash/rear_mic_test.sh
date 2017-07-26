#!/usr/bin/env bash

ffmpeg \
    -i <( 
        gst-launch-1.0 -q v4l2src device=/dev/video0 do-timestamp=true \
            ! image/jpeg, width=1280, height=720, framerate=24/1 \
            ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 \
            ! mux. \
        alsasrc device=hw:CARD=Webcam,DEV=0 do-timestamp=true \
            ! audio/x-raw, rate=32000, channels=2 \
            ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 \
            ! mux. \
        alsasrc device=hw:CARD=PCH,DEV=0 do-timestamp=true \
            ! audio/x-raw, rate=44100, channels=2 \
            ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 \
            ! mux. \
        alsasrc device=hw:CARD=PCH,DEV=2 do-timestamp=true \
            ! audio/x-raw, rate=44100, channels=2 \
            ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 \
            ! mux. \
        matroskamux name=mux \
            ! fdsink fd=1 
    ) -pix_fmt yuv420p\
    -c:v libx264 -preset slow -crf 23 -profile:v high\
    -c:a:1 libmp3lame \
    -c:a:2 libmp3lame \
    -c:a:3 libmp3lame \
    -map 0:0 -map 0:1 -map 0:2 -map 0:3 -f mp4 \
    "/home/john/Documents/MPBC/Video_Project/$1"
