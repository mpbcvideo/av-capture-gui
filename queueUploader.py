import time
import boto3
from queue import *
from threading import Thread
import connection

queue = Queue()
s3 = boto3.resource('s3')
bucket = #INSERT BUCKET HERE
inProgress = []

def upload(file_):
    '''
    Attempts to upload a given file, and if upload is successful, it removes the file from fileQueue.txt
    and writes all the remaining files back. If the upload files it removes the file from the files in 
    the process of uploading. 
    '''
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
