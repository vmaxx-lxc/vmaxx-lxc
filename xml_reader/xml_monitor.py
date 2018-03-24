#! /usr/bin/python

import time
import os
import sys
import shutil

def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
'''
def rm_acc():
    if os.path.exists('cam_json'):
        shutil.rmtree('cam_json')
        os.mkdir('cam_json')
    else:
        os.mkdir('cam_json')

    if os.path.exists('line_json'):
        shutil.rmtree('line_json')
        os.mkdir('line_json')
    else:
        os.mkdir('line_json')

    if os.path.exists('poly_json'):
        shutil.rmtree("poly_json")
        os.mkdir('poly_json')
    else:
        os.mkdir('poly_json')
'''

while True:
    #rm_acc()
    command = "sudo /usr/bin/python2.7" + " " + cur_file_dir() + "/xml_read.py"
    #print command
    os.system(command)
    time.sleep(30)
