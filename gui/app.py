#!/usr/bin/python3

from flask import Flask, jsonify, render_template, request, url_for, redirect
from cefpython3 import cefpython as cef
from subprocess import Popen, DEVNULL, STDOUT
from ffmpy import FFmpeg
from time import strftime, gmtime, sleep
import threading
import platform
import shlex
import sys
import os
import boto3
import ipaddress as ip

app = Flask(__name__)

s3 = boto3.client('s3')

ipaddress = ip.get_ip()


studies = [{'name' : 'MP16'}, {'name' : 'MAPP1'}, {'name' : 'MAPP2'}]
sites = [
    { 'name' : {'Zen Therapeutic Solutions, LLC' : '01'}}, 
    { 'name' : {'Aguazul-Bluewater, Inc.' : '02'}}, 
    { 'name' : {'Wholeness Center' : '03'}}, 
    { 'name' : {'New School Research, LLC' : '04'}}, 
    { 'name' : {'Ray Worthy Psychiatry, LLC' : '05'}},
    { 'name' : {'University of California, San Francisco' : '06'}},
    { 'name' : {'Private Practice' : '07'}},
    { 'name' : {'University of Connecticut' : '08'}},
    { 'name' : {'Uniersity of Wisconsin, Madison' : '09'}},
    { 'name' : {'New York University' : '10'}},
    { 'name' : {'Center for Optimal Living' : '11'}},
    { 'name' : {'Vanvouver Site' : 'TBD'}},
    { 'name' : {'Boston Site' : 'TBD'}},
    { 'name' : {'Israel Site' : 'TBD'}},
    { 'name' : {'Dr. Simon Amar, LLC' : 'TBD'}}
]
visits = ['V{:02}'.format(i) for i in range(1, 40)]

@app.route('/')
def index():
    '''
    return render_template('recording.html')
    '''
    return render_template(
        'index.html',
        studies = studies,
        sites = sites,
        visits = visits,
        study = '',
        site = '',
        participant = '',
        visit = '',
        test_complete = False,
        first_attempt = True
    )

@app.route('/start_recording', methods=['POST', 'GET'])
def start_recording():
    '''
    Checks the parameters for correctness, names the recording given the 
    parameters, and starts the recording process.
    '''
    btn = request.args.get('btn') 
    study = request.args.get('study')
    site = request.args.get('site')
    participant = request.args.get('participant')
    visit = request.args.get('visit')
    time =  strftime("%Y%m%d_%H%M%S", gmtime())
    
    global filename
    filename = '_'.join([study, participant, visit, time]) + '.mp4'
    
    print(filename)
    

    if participant != '' and visit in visits:
        if btn == 'start':
            capture_thread = threading.Thread(target = capture)
            #video_thread = threading.Thread(target = videoCapture)
            #audio_thread = threading.Thread(target = audioCapture) 
            capture_thread.start()
            #video_thread.start()
            #audio_thread.start()
            return render_template(
                'recording.html',
                participant = participant,
                visit = visit,
            )
        elif btn == 'test':
            return render_template(
                'index.html', 
                studies = studies,
                sites = sites,
                visits = visits,
                study = study,
                site = site,
                visit = visit,
                participant = participant,
                test_complete = True,
                first_attempt = False
            )                 
    else:
        return render_template(
            'index.html', 
            studies = studies,
            sites = sites,
            visits = visits,
            study = study,
            site = site,
            visit = visit,
            participant = participant,
            test_complete = False,
            first_attempt = False
        )                 


@app.route('/stop_recording', methods=['POST', 'GET'])
def stop_recording():
    os.system('killall ffmpeg')
    sleep(5)
    f = open("../fileQueue.txt", "w")
    f.write(filename)
    f.close()
    #mux()
    return "Success"

def capture():

    ffmpeg = FFmpeg(
        inputs = {
            'hw:2' : [
                '-f', 'alsa', 
                '-ac', '2',
                '-thread_queue_size', '8192'
            ],
            '/dev/video0' : [
                '-f', 'v4l2', 
                '-s', '1280x720', 
                '-r', '24', 
                '-input_format', 'mjpeg',
                '-thread_queue_size', '8192'
            ]
        },
        outputs = {
            "../"+filename : None
        }
    )
    
    #os.system(ffmpeg.cmd)
    #ffmpeg.run(stdout=PIPE, stderr=PIPE)
    
    print(ffmpeg.cmd)
    
    p = Popen(shlex.split(ffmpeg.cmd), stdin=DEVNULL, stdout=DEVNULL, stderr=STDOUT)

def videoCapture():
    
    ffmpeg = FFmpeg(
        inputs = {
            '/dev/video0' : [
                '-f', 'v4l2', 
                '-s', '1280x720', 
                '-r', '24', 
                '-input_format', 'mjpeg',
                '-thread_queue_size', '8192'
            ]
        },
        outputs = {
            'video.mp4' : None
        }
    )
    
    p = Popen(shlex.split(ffmpeg.cmd), stdin=DEVNULL, stdout=DEVNULL, stderr=STDOUT)
    
    
def audioCapture():

    ffmpeg = FFmpeg(
        inputs = {
            'hw:2' : [
                '-f', 'alsa', 
                '-ac', '2',
                '-thread_queue_size', '8192'
            ]
        },
        outputs = {
            'audio.mp3' : None
        }
    )
    
    #os.system(ffmpeg.cmd)
    #ffmpeg.run(stdout=PIPE, stderr=PIPE)
    
    print(ffmpeg.cmd)
    
    p = Popen(shlex.split(ffmpeg.cmd), stdin=DEVNULL, stdout=DEVNULL, stderr=STDOUT)    

def mux():
    
    ffmpeg = FFmpeg(
        inputs = {
            './audio.mp3' : ['-acodec', 'copy'],
            './video.mp4' : ['-vcodec', 'copy']
           
        },
        outputs = {
            filename : None
        }
    )

    p = Popen(shlex.split(ffmpeg.cmd), stdin=DEVNULL, stdout=DEVNULL, stderr=STDOUT)   

def flask_thread():
    app.run(host=ipaddress)

def main():
    app_thread = threading.Thread(target = flask_thread)
    app_thread.daemon = True
    app_thread.start() 
    
    
    sleep(3)
    check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    cef.Initialize()
    cef.CreateBrowserSync(url="http://"+ipaddress+":5000/",
                          window_title="App")
    cef.MessageLoop()
    cef.Shutdown()
    
def check_versions():
    print("[app.py] CEF Python {ver}".format(ver=cef.__version__))
    print("[app.py] Python {ver} {arch}".format(
          ver=platform.python_version(), arch=platform.architecture()[0]))
    assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"


if __name__ == '__main__': 
    main()
 
