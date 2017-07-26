#!/usr/bin/env python3

conversions = {'mp4':'video/','mp3':'audio/'}

def get_s3path(file_):
    path = file_.split('_')[:3]
    path.append(conversions[file_.split('.').pop()])
    return '/'.join(path)
