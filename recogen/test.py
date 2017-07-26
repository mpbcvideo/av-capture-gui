#!/usr/bin/python3

from subprocess import Popen, PIPE, check_output
import os

audio_devices = {
    'hw:CARD=PCH,DEV=0' : False,
    'hw:CARD=PCH,DEV=2' : False,
    'hw:CARD=Webcam,DEV=0' : False,
    'hw:CARD=Device,DEV=0' : False
}

path = os.path.dirname(os.path.abspath(__file__))

p = Popen(['v4l2-ctl', '--list-devices'], stdout=PIPE, stderr=PIPE)
output = p.communicate()[0]
if p.returncode != 0:
    q = Popen(path + '/bash/reset_usb.sh', stdout=PIPE)
    output = q.communicate()[0]

arecord = Popen(['arecord', '-L'], stdout=PIPE)
grep = Popen(['grep', '^hw'], stdin=arecord.stdout, stdout=PIPE, stderr=PIPE)
output = grep.communicate()[0]

for f in output.decode().split('\n'):
    if f in audio_devices: audio_devices[f] = True
    
for device in audio_devices:
    if not audio_devices[device]: print(device)


