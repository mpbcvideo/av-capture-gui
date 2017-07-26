#!/usr/bin/env bash

DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)";
APP="${DIR%bash}/app.py"
#resets all attached USB ports until a camera is detected
j=0;
c=1;
while [ $j -lt 5 ] && [ $c -eq 1 ]; do
    #checks if a camera is detected
    v4l2-ctl --list-devices;
    let c=$?;
    if [ $c -eq 0 ]; then
        #runs application
        python3 $APP;
        #resets alsa
        sudo alsa reload;
        
        exit 0;
    fi;
    echo "$j, $c";
    let j=j+1;
    for i in /sys/bus/pci/drivers/[uoex]hci_hcd/*:*; do
        echo "${i##*/}" | sudo tee "${i%/*}/unbind";
        echo "${i##*/}" | sudo tee "${i%/*}/bind";
        sleep 3;
    done;
done;

notify-send --expire-time=10 --icon=/home/john/Documents/MPBC/Video_Project/mpbccapture.png 'No camera detected' 'Please check the connection';

python3 $APP;

sudo alsa reload;

exit 1;
