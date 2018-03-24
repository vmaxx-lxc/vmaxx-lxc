# vim: expandtab:ts=4:sw=4
import numpy as np
import fcntl
import os, sys
import cv2
from xml.dom.minidom import Document
import commands as cm
import hashlib
import urllib, urllib2
import json


class WebService:
    def __init__(self, uplink_ip, cam_id):
        self.uplink_ip = uplink_ip
        self.cam_id = cam_id
        self.local_folder = '/home/ubuntu/pyEvent/results/backup/'
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

    def get_token(self):
        self.values.update({'task': 'get'})
        values_url = urllib.urlencode(self.values)
        url = 'http://' + self.uplink_ip + '/configurator/token.php' + '?' + values_url
        print url
        try:
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
        except:
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
        print url
        try:
            request = urllib2.Request(url)
            print 'request=' + str(request)
            response = urllib2.urlopen(request)
            response = response.read()
            response = json.loads(response)
            status = response['status']
            print status
            if 'success' == status:
                for file_name in file_names:
                    os.remove(self.local_folder + file_name)
                return True
            else:
                return False
        except:
            return False

    def upload_three_times(self, file_names):
        url = "http://" + self.uplink_ip + "/webservice/report.php"
        self.values.update({'task': 'receive_file'})
        self.values.update({'token': self.token})
        self.values.update({'cameraId': self.cam_id})
        value_url = urllib.urlencode(self.values)
        url = url + "?" + value_url
        for file_name in file_names:
            url += '&files[]=%s/%s' % (self.header, file_name)
        print url
        try_times = 0
        try:
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
            if 'success' == status:
                return True
            else:
                return False
        except:
            return False

