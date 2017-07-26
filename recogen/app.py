from flask import Flask, jsonify, render_template, request, url_for, redirect
from cefpython3 import cefpython as cef
from ffmpy import FFmpeg
from time import strftime, gmtime, sleep
import subprocess as sp
import random
import threading
import platform
import shlex
import sys
import os
import shutil
import boto3
import socket

app = Flask(__name__)

path = os.path.dirname(os.path.abspath(__file__))

s3 = boto3.client('s3')

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

ipaddress = get_ip()

test_complete = False

studies = [{'name' : 'MP16'}, {'name' : 'MAPP1'}, {'name' : 'MAPP2'}]
sites = [
    { 'name' : {'Charleston' : '01'}}, 
    { 'name' : {'Boulder' : '02'}}, 
    { 'name' : {'Fort Collins' : '03'}}, 
    { 'name' : {'Los Angeles' : '04'}}, 
    { 'name' : {'New Orleans' : '05'}},
    { 'name' : {'UCSF' : '06'}},
    { 'name' : {'San Francisco Private Practice' : '07'}},
    { 'name' : {'UConn' : '08'}},
    { 'name' : {'Madison' : '09'}},
    { 'name' : {'NYU' : '10'}},
    { 'name' : {'NY Center for Optimal Living' : '11'}},
    { 'name' : {'Vanvouver Site' : 'TBD'}},
    { 'name' : {'Boston Site' : 'TBD'}},
    { 'name' : {'Israel Site' : 'TBD'}},
    { 'name' : {'Dr. Simon Amar, LLC' : 'TBD'}}
]
visits = ['V{:02}'.format(i) for i in range(1, 40)]

test_paths = [True] * 5

wait_messages = {
    1 : ['Don\'t trip.', 'This will only take a moment.'],
    2 : ['Hold tight.', 'Your video sample will be ready momentarily.'],
    3 : ['I\'m so happy to be a part of your research.', 'You know, your typical AI doesn\'t often get to participate in psychedelic science.'],
    4 : ['If it weren\'t for your work,', 'I wouldn\'t be here right now. Thank you!'],        
    5 : ['Sit tight.', 'Your test recording will be ready in a moment.'],
    6 : ['“We have been to the moon, we have charted the depths of the ocean and the heart of the atom...', 'but we have a fear of looking inward to ourselves because we sense that is where all the contradictions flow together.”', 'Terence McKenna'],
    7 : ['“Not since Moses has anyone seen a mountain so greatly.”', 'Rainer Maria Rilke'],
    8 : ['“Surely all art is the result of one\'s having been in danger,', 'of having gone through an experience all the way to the end, where no one can go any further.”', 'Rainer Maria Rilke']
}
    
message = wait_messages[random.sample(set(wait_messages), 1)[0]]    
    
@app.route('/')
def index():

    return render_template(
        'index.html',
        studies = studies,
        sites = sites,
        visits = visits,
        study = '',
        site = '',
        participant = '',
        visit = '',
        ipaddress = ipaddress,
        test_complete = False,
        first_attempt = True
    )
    
@app.route('/test_results')
def test_results():
    return render_template(
        'results.html',
        combined = test_paths[0],
        webcam = test_paths[1],
        omni = test_paths[2],
        shotgun = test_paths[3],
        lapel = test_paths[4]
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
        
    if btn == 'exit':
        shutdown_server()

    global filename
    filename = '_'.join([study, participant, visit, time])   
    
    if participant != '' and visit in visits:
        if btn == 'start':
            capture_thread = threading.Thread(target = capture)
            capture_thread.start()
            return render_template(
                'recording.html',
                participant = participant,
                visit = visit,
            )
        elif btn == 'test':
            sound_thread = threading.Thread(target = play_sound)
            sound_thread.start()
            test_thread = threading.Thread(target = test_capture)
            test_thread.start()
            return render_template(
                'test.html'
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
            ipaddress = ipaddress,
            test_complete = False,
            first_attempt = False
        )                 


@app.route('/start', methods=['POST', 'GET'])
def start():
    
    folder = path + '/static/tmp'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        if os.path.isfile(file_path):
            os.unlink(file_path)

    
    btn = request.args.get('btn') 

    if btn == 'start':
        capture_thread = threading.Thread(target = capture)
        capture_thread.start()
        return render_template('recording.html')
        
    elif btn == 'back':
        return render_template(
            'index.html',
            studies = studies,
            sites = sites,
            visits = visits,
            study = '',
            site = '',
            participant = '',
            visit = '',
            ipaddress = ipaddress,
            test_complete = False,
            first_attempt = True
        )
    elif btn == 'test':
        test_thread = threading.Thread(target = test_capture)
        test_thread.start()
        return render_template(
            'test.html'
        )         

@app.route('/cancel_recording', methods=['POST', 'GET'])
def cancel_recording(): 
    kill_thread = threading.Thread(target = kill)
    kill_thread.start()    
    return render_template(
        'index.html',
        studies = studies,
        sites = sites,
        visits = visits,
        study = '',
        site = '',
        participant = '',
        visit = '',
        ipaddress = ipaddress,
        test_complete = False,
        first_attempt = True
    )

@app.route('/stop_recording', methods=['POST', 'GET'])
def stop_recording():
    kill_thread = threading.Thread(target = kill)
    kill_thread.start() 
    queue_thread = threading.Thread(target = queue_upload)
    queue_thread.start()
    #mux()
    return render_template(
        'index.html',
        studies = studies,
        sites = sites,
        visits = visits,
        study = '',
        site = '',
        participant = '',
        visit = '',
        ipaddress = ipaddress,
        test_complete = False,
        first_attempt = True
    )

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()


@app.errorhandler(500)
def internal_error(error):

    return render_template(
        'index.html',
        studies = studies,
        sites = sites,
        visits = visits,
        study = '',
        site = '',
        participant = '',
        visit = '',
        ipaddress = ipaddress,
        test_complete = False,
        first_attempt = True
    )

def shutdown_server():
    cef.Shutdown()
    sleep(5)
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def kill():
    sleep(1)
    os.system('killall ffmpeg')
    
def queue_upload():
    sleep(5)
    f = open(path + '/queue/fileQueue.txt', 'a+')
    #f.write(filename+'.mp3\n')
    f.write(filename+'.mp4\n')
    f.close()
    
def capture():
    sp.call([path + '/bash/capture.sh', filename])

def test_capture():
    child = sp.Popen(path + '/bash/test_capture.sh', stdout=sp.PIPE)
    tc = child.communicate()[0]
    rc = child.returncode
    for i in range(1, rc):
        if i < 3: test_paths[i] = False
        else: test_paths[i-2] = True
    
def play_sound():
    pass
       
def flask_thread():
    app.run(host=ipaddress)

def main():
    app_thread = threading.Thread(target = flask_thread)
    app_thread.daemon = True
    app_thread.start() 
    
    
    sleep(3)
    #check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    cef.Initialize()
    cef.CreateBrowserSync(url="http://"+ipaddress+":5000/",
                          window_title="Recogen")
    cef.MessageLoop()
    sleep(5)
    cef.Shutdown()
    
def check_versions():
    print("[app.py] CEF Python {ver}".format(ver=cef.__version__))
    print("[app.py] Python {ver} {arch}".format(
          ver=platform.python_version(), arch=platform.architecture()[0]))
    assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"


if __name__ == '__main__': 
    main()
 
