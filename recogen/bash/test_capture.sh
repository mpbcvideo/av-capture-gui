#! /usr/bin/env bash

combined=1
webcam=1

j=0;
c=1;
while [ $j -lt 3 ] && [ $c -eq 1 ]; do
    #checks if a camera is detected
    v4l2-ctl --list-devices;
    let c=$?;
    if [ $c -eq 0 ]; then
        continue;
    fi;
    echo "$j, $c";
    let j=j+1;
    for i in /sys/bus/pci/drivers/[uoex]hci_hcd/*:*; do
        echo "${i##*/}" | sudo tee "${i%/*}/unbind";
        echo "${i##*/}" | sudo tee "${i%/*}/bind";
        sleep 3;
    done;
done;

{
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
            alsasrc device=hw:CARD=Device,DEV=0 do-timestamp=true \
                ! audio/x-raw, rate=44100, channels=2 \
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
        ) -pix_fmt yuv420p -y -t 10\
        -c:v libvpx-vp9 -deadline realtime -cpu-used 8\
        -map 0:0 -map 0:1 -map 0:2 -map 0:3? -map 0:4? -f webm \
        "/home/john/Documents/MPBC/recogen/recogen/static/tmp/combined.webm" \
        -map 0:0 -map 0:1 -t 10  \
        "/home/john/Documents/MPBC/recogen/recogen/static/tmp/webcam.webm" \
        -map 0:2 -t 10 \
        "/home/john/Documents/MPBC/recogen/recogen/static/tmp/omni.wav" \
        -map 0:3 -t 10 \
        "/home/john/Documents/MPBC/recogen/recogen/static/tmp/shotgun.wav" \
        -map 0:4 -t 10 \
        "/home/john/Documents/MPBC/recogen/recogen/static/tmp/lapel.wav" && 
        rc=0 && exit $rc || 
        rc=1;
} && {   
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
            matroskamux name=mux \
                ! fdsink fd=1 
        ) -pix_fmt yuv420p -y -t 10\
        -c:v libvpx-vp9 \
        -map 0:0 -map 0:1 -f webm \
        "/home/john/Documents/MPBC/recogen/recogen/static/tmp/webcam.webm" &&
        webcam=1 ||
        webcam=0; 
        rc=2;
} && {
    ffmpeg \
        -i <( 
            gst-launch-1.0 -q alsasrc device=hw:CARD=Device,DEV=0 do-timestamp=true \
                ! audio/x-raw, rate=44100, channels=2 \
                ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 \
                ! mux. \
            matroskamux name=mux \
                ! fdsink fd=1 
        ) -pix_fmt yuv420p -y -t 10\
        -f wav \
        "/home/john/Documents/MPBC/recogen/recogen/static/tmp/omni.wav" || 
        if [ $webcam = 1 ]; then 
            rc=4;
        else
            rc=3;
        fi
} && {
    ffmpeg \
    -i <( 
        gst-launch-1.0 -q alsasrc device=hw:CARD=PCH,DEV=0 do-timestamp=true \
            ! audio/x-raw, rate=44100, channels=2 \
            ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 \
            ! mux. \
        matroskamux name=mux \
            ! fdsink fd=1 
    ) -pix_fmt yuv420p -y -t 10\
    -f wav \
    "/home/john/Documents/MPBC/recogen/recogen/static/tmp/shotgun.wav"        
} && {
    ffmpeg \
    -i <( 
        gst-launch-1.0 -q alsasrc device=hw:CARD=PCH,DEV=2 do-timestamp=true \
            ! audio/x-raw, rate=44100, channels=2 \
            ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 \
            ! mux. \
        matroskamux name=mux \
            ! fdsink fd=1 
    ) -pix_fmt yuv420p -y -t 10\
    -f wav \
    "/home/john/Documents/MPBC/recogen/recogen/static/tmp/lapel.wav"              
} && exit $rc 

