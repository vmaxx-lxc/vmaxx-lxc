#! /usr/bin/python
#
# start cameras
#
# code by Ruoyu Yang
# 2017 08 31
# revised for Irvine 
# 2017 11 02
#

import sys
import os
import time
import commands as cm
import json
import threading
import hashlib
import urllib, urllib2


class WebService:
    def __init__(self, uplink_ip, cam_id):
        self.uplink_ip = uplink_ip
        self.cam_id = cam_id
        self.local_folder = '../pyEvent/results/backup/'
        m = hashlib.md5()
        m.update('Xjtu123456')
        pwd = m.hexdigest()
        self.values = {'username': 'admin', 'password': pwd, 'task': ''}
        command = "ip route get 8.8.8.8 | awk '{print $7}'"
        (status, output) = cm.getstatusoutput(command)
        if status == 0:
            local_ip = output.strip()
        else:
            sys.exit(0) # TODO ADD LOG
        self.header = 'http://' + local_ip + '/event/backup'
        self.token = ''

    def get_toke(self):
        self.values.update({'task': 'get'})
        values_url = urllib.urlencode(self.values)
        url = 'http://' + self.uplink_ip + '/configurator/token.php' + '?' + values_url
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        response = response.read()
        response = json.loads(response)
        status = response["status"]
        self.token = response["token"]
        if 'success' == status:
            return True
        else:
            return False

    def upload(self, file_names):
        url = "http://" + self.uplink_ip + "/webservice/report.php"
        self.values.update({'task': 'receive_file'})
        self.values.update({'token': self.token})
        self.values.update({'cameraId': self.cam_id})
        value_url = urllib.urlencode(self.values)
        url = url + "?" + value_url
        for file_name in file_names:
            url += '&files[]=%s/%s' % (self.header, file_name)
        try_times = 0
        # print url
        while try_times < 3:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            response = response.read()
            response = json.loads(response)
            status = response['status']
            try_times += 1
            if 'success' == status:
                try_times = 3
        for file_name in file_names:
            os.remove(self.local_folder + file_name)


RECORD_SCRIPT = './record.py'
chunk = '00:05:00'

try:
    os.mkdir("cache_")
except BaseException,e:
    print e

def upload_storage():
    uplink_ip = "10.55.1.21"
    cameraId = "1"    

    try:
        folder_path = '../pyEvent/results/backup/'
        folder_path = '/home/ubuntu/pyEvent/results/backup/'
        file_names = os.listdir(folder_path)
        local_webService = WebService(uplink_ip, cameraId)
        status = local_webService.get_toke()
        if status:
            length = len(file_names)
            file_inter = 10
            len_sta = 0
            len_end = file_inter
            forstatus = True
            if length < len_end :
                len_end = length

            while forstatus:
                file_dos = []
                for i in range(len_sta, len_end):
                    file_tmp = file_names[i].strip()
                    file_dos.append(file_tmp)
                    len_sta = len_end
                    len_end = len_end + file_inter
                    if length < len_end:
                        forstatus = False
                print "file_dos", file_dos
                status1 = local_webService.upload(file_dos)

                print "file status = ", status1
                if status1:
                    print "upload file success"
                else:
                    status2 = local_webService.get_toke()
                    if status2:
                        print "token success"
                # time.sleep(10)
        
    except BaseException, e:
        print e



def starter():
    command = "ls /var/www/TX2_console/param/setup_*"
    status, info = cm.getstatusoutput(command)
    json_list = info.split()

    for fn in json_list:
        try:
            with open(fn,'r') as f:
                set_up = json.load(f)
            try:
                os.makedirs(set_up['description'])
            except BaseException, e:
                print e
            command = RECORD_SCRIPT +" '"+chunk+"' '"+set_up['description'] +"' '"+set_up["cameraId"]+"' '"+ set_up['source'] +"' '"+ set_up['dailyStart'] +"' '"+ set_up['dailyStop']+"'&"
            os.system(command)
            # print i
        except:
            print "file not"
    f = threading.Timer(300, starter)
    f.start()


f = threading.Timer(2, starter)
f.start()
