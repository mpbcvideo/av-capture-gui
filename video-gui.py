#!/usr/bin/python3

from tkinter import *
from ffmpy import FFmpeg
from threading import Thread
from subprocess import PIPE
import sys
import io
import os
import time
import datetime
import boto3

fields = 'Site', 'Subject', 'Visit'
studies = 'MPVA1', 'MJP1', 'MDA1', 'TEST'
visits = ['V%02d' % i for i in range(1, 40)]

sys.stdout = io.BytesIO()

def makeform(root, fields):

   entries = []
   for field in fields:
      row = Frame(root, bg='#001320')
      lab = Label(
          row, 
          width=15, 
          text=field+':', 
          fg='white', 
          bg='#001320', 
          anchor='w'
      )
      ent = Entry(row)
      row.pack(side=TOP, fill=BOTH, padx=5, pady=5)
      lab.pack(side=LEFT, expand=YES, padx=20)
      ent.pack(anchor=CENTER, expand=NO, fill=NONE, padx=20)
      entries.append((field, ent))
   return entries

def fetch(entries):

    global name
    name = ''
    record = True
    for i, entry in enumerate(entries):
        field = entry[0]
        text = entry[1].get()
        if i == 0 and str(text) not in studies:
            print('Error: Invalid Study ID')
            record = False
            break;
        elif i == 2 and str(text) not in visits:
            print('Error: Invalid Visit ID')
            record = False
            break;
        else:
          name += text+'_'
    name += time.strftime("%d%b%y")+'.mp4'
    if record:
        l1['text'] = name
        b1.config(state=DISABLED)
        b2.config(state=ACTIVE)
        thread = Thread(target=recordThread)
        thread.start()
    
def recordThread():

    ffmpeg = FFmpeg(
        inputs = {
            '/dev/video0' : ['-y', '-f', 'v4l2', '-thread_queue_size', '8192'],
            'hw:0' : ['-f', 'alsa', '-thread_queue_size', '8192']
        },
        outputs = {
            name : '-threads 0 -map 0:v? -map 1:a?'
        }
    )
    
    #os.system(ffmpeg.cmd)
    #ffmpeg.run(stdout=PIPE, stderr=PIPE)
    ffmpeg.run()
    
def stop():
    
    b1.config(state=ACTIVE)
    b2.config(state=DISABLED)
    os.system('pkill -n ffmpeg')

if __name__ == '__main__':
   root = Tk()
   ents = makeform(root, fields)
   root.bind('<Return>', (lambda event, e=ents: fetch(e)))   
   b1 = Button(root, text='Record',
          command=(lambda e=ents: fetch(e)),
          fg='red')
   b1.pack(side=LEFT, anchor=CENTER, padx=5, pady=5)
   b2 = Button(root, text='Stop', command=stop)
   b2.pack(side=LEFT, anchor=CENTER, padx=5, pady=5)
   b3 = Button(root, text='Quit', command=root.quit)
   b3.pack(side=LEFT, anchor=CENTER, padx=5, pady=5)
   l1 = Label(root, text='')
   root.title('MPBC Video Capture Demo')
   root.configure(bg='#001320')
   root.mainloop()
    
