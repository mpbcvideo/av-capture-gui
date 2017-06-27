import time
import boto3
from queue import *
from threading import Thread
import connection

queue = Queue()
s3 = boto3.resource('s3')
bucket = 'mpbcnodecamtest'
inProgress = []

def upload(file_):
    #try appending the current upload attempts to a list and make it a condition that they are not in that list to be added to the queue
    print("Attempting to upload "+file_)
    try:
        s3.meta.client.upload_file(file_, bucket, file_, ExtraArgs={"ContentType": "video/mp4"})
        print("Successfully uploaded "+file_)
        fileQueue.remove(file_)
        f = open("fileQueue.txt", "w")
        for files in fileQueue:
            f.write(files)
        f.close() 
    except:
        print("Upload of "+file_+" failed")
    inProgress.remove(file_)
    
def pull_from_queue():
    while True:
        item = queue.get()
        upload(item)
 
while True:
    f = open("fileQueue.txt", "r")
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
