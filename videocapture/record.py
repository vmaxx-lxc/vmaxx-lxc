#! /usr/bin/python
#
# recording
#
# code by Ruoyu Yang
# 2017 08 31
#

import sys
import os
import time
import commands as cm
import json
import re
import hashlib
import json
import commands as cm
import sys
import urllib, urllib2




class WebService:
    def __init__(self, uplink_ip, cam_id):
        self.uplink_ip = uplink_ip
        self.cam_id = cam_id
        self.local_folder = '../pyEvent/results/'
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
        self.header = 'http://' + local_ip + '/event'
        self.token = ''

    def get_toke(self):
        self.values.update({'task': 'get'})
        values_url = urllib.urlencode(self.values)
        url = 'http://' + self.uplink_ip + '/configurator/token.php' + '?' + values_url
        # print url
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
        # print url
        try_times = 0
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


[chunk, camera_name, camera_id, url,startHour,endHour] = sys.argv[1:]



#daily_start & daily_end

FFMPEG_BINARY = '/usr/bin/ffmpeg'
status_log_script = './status_log.py' 
#container = 'office'

errorCount = 0
date = ""
hour = ""

ts = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time()))
date = ts[0:10]
hour = ts[11:13]

#time_now = ts[11:13]+':'+ts[14:16]
#fileBaseName = company_name+"_"+property_name+"_"+camera_name+"_"+ts
fileBaseName = camera_name+"_"+camera_id+"_"+ts[0:16]

filePathName = "cache_/"+fileBaseName+".mp4"

#split_filename=re.split(r'[\/]',filePathName)
#video_name = split_filename[1]

# capture the video

hour = int(hour)
startHour = int(startHour)
endHour = int(endHour)

if startHour < endHour:
    work_hours = range(startHour, endHour)
else:
    work_hours = range(startHour, 24) + range(0, endHour)

if hour in work_hours:
    print "Work time"
    command = FFMPEG_BINARY+ " -hide_banner -i '"+url+"' -c:v copy -an -t "+chunk+ " -r 15 -s 1280x720 -b:v 2500k '"+filePathName +"'"
    print "start recording ",fileBaseName
    err_counter = 0

    while True:
        (status_record, output) = cm.getstatusoutput(command)
        if status_record == 0:
            command = "mv " + "cache_/"+fileBaseName+ ".mp4 " + camera_name + "/"
            os.system(command)
            break
        else:
            err_counter = err_counter +1
            time.sleep(3)
            if err_counter == 5:
                #print "error on video capturing"
                #curtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                #content = "At " + curtime + " Error happened while capturing the video from camera " + camera_name + ". Please have a look! <br /> <br /> Error message is as below : <br /> <br/> " + output + " <br /><br />"
                f = open('video_'+camera_name+'_'+camera_id+'_'+ts+'.log', 'a+')
                log_filename = 'video_'+camera_name+'_'+camera_id+'_'+ts+'.log'
                content = "3"+"@"+output[0:512]
                f.write(content)
                f.close()
                src = log_filename
                dst = '../pyEvent/results/transfile/' + log_filename
                #dst = '/data/video/backup/' + camera_id + '/' + date + '/' + log_filename
                os.rename(src, dst)
                #web = WebService('192.168.2.32', camera_id)
                #web.get_toke()
                #web.upload([log_filename])
                #command = status_log_script + " " + "'" +  content + "'"
                #os.system(command)
                break
else:
    print "sleep time"


