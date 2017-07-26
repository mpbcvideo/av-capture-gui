#!/usr/bin/env python3

import time
import boto3
import os
from queue import *
from threading import Thread
import connection
import filenameParser as fp

vidpath = os.path.expanduser('~')+"/Videos/"
path = os.path.dirname(os.path.abspath(__file__))
queue = Queue()
s3 = boto3.resource('s3')
bucket = 'maps-study-videos'
inProgress = []

def upload(file_):
    #try appending the current upload attempts to a list and make it a condition that they are not in that list to be added to the queue
    print("Attempting to upload "+vidpath+file_)
    try:
        s3path = fp.get_s3path(file_)
        s3.meta.client.upload_file(vidpath+file_, bucket, s3path+file_, ExtraArgs={"ContentType": "video/mp4"})
        print('Successfully uploaded '+file_)
        fileQueue.remove(file_)
        f = open(path+'/queue/fileQueue.txt', 'w')
        for files in fileQueue:
            f.write(files+"\n")
        f.close() 
        os.remove(vidpath+file_)
    except:
        print("Upload of "+file_+" to "+s3path+" failed")
    inProgress.remove(file_)
    
def pull_from_queue():
    while True:
        item = queue.get()
        upload(item)
 
while True:
    f = open(path + '/queue/fileQueue.txt', 'r')
    fileQueue = [line.strip() for line in f.readlines()]
    newQueue = fileQueue
    f.close()
    for i in range(4):
        thread = Thread(target=pull_from_queue)
        thread.daemon = True
        thread.start()
    
    for file_ in set(fileQueue).difference(inProgress):
        queue.put(file_)
        inProgress.append(file_)
    time.sleep(10)
