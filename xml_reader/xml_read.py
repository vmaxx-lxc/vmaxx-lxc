#! /usr/bin/python
#
# read data analysis result from XML
# insert the result to db
#
# code by Ruoyu Yang
# 2017 11 20
#

import xml.dom.minidom
import commands as cm
import os
import json
import time
import cloud_webservice as cloudweb
from xml.etree import ElementTree as ET
clouduplink_ip = "52.240.159.164"#####
cloud_webService = cloudweb.cloudWebService(clouduplink_ip)
#dbname = "irvine_middle"
dbname = "dashboard_v1"####
#init = True
#change_day = False

log_path = '/result/uplinkdata/log/'
#################################
path = "/result/uplinkdata/xml/"
################################
#path = "xml/"  ###
file_dir = "ls " + path

###
#beginFlag = True
#histFile = ""
###

def file_sort(f_dir):

    status, info = cm.getstatusoutput(f_dir)
    info = info.split()
    if info == []:
        result = []
        return result
    dic = {}
    for i in range(0, len(info)):
        ts = info[i].split("_")
        dic[info[i]] = ts[2] + "_" + ts[3]
    rd = sorted(dic.items(), lambda x, y: cmp(x[1], y[1]), reverse = False)
    result = []
    for i in range(0, len(rd)):
        result.append(rd[i][0])
    return result

def xml_read():
    while True:

        file_sorted_list = file_sort(file_dir)

        while True:
            token_status = cloud_webService.get_token()
            if token_status == True:
                break
            else:
                mv_command = 'mv *.log ' + log_path
                (status_mv, info) = cm.getstatusoutput(mv_command)
                if status_mv != 0:
                    print 'fail to move token log', info
                #os.rename('xml_' + log_time + '.log', log_path + 'xml_' + log_time + '.log')
                pass

        if file_sorted_list == []:
            print "no more to insert "
            time.sleep(30)
            continue

        for xml_file in file_sorted_list:
            xml_name = xml_file.split(".")
            xml_name_split = xml_name[0].split('_')
            name = xml_name_split[0]
            cam_id = xml_name_split[1]
            date = xml_name_split[2]
            clock = xml_name_split[3]
            string = date.split("-")
            year = string[0]

            month = string[1]
            day = string[2]

            hour = clock.split("-")[0]
            minute = clock.split("-")[1]

            # check xml validation
            if os.stat(path + xml_file).st_size == 0:
                os.remove(path + xml_file)
                continue
            try:
                ET.parse(path + xml_file)
            except Exception, e:
                print 'bad formatted xml'
                print 'possible reason', e
                os.remove(path + xml_file)
                continue


            DOMTree = xml.dom.minidom.parse(path + xml_file)
            root = DOMTree.documentElement

            sql_command = []

            cam_occupancy = root.getAttribute("occupancy")
            cam_dwell = root.getAttribute("dwell")

            #stay_time = float(cam_dwell) * float(cam_occupancy)#

            lines = root.getElementsByTagName("polyline")
            polygons = root.getElementsByTagName("polygon")
            time_str = year + "-" + month + "-" + day + " " + hour + ":" + minute

            command = "insert into occupancy(camera_id,occupancy,dwell_time,created_time) values (%s,%s,%s,'%s')" \
                      % (cam_id, cam_occupancy, cam_dwell, time_str)#timestamp to created_time

            sql_command.append(command)

            if lines != []:
                for line in lines:
                    line_id = line.getAttribute("id")

                    enters = line.getElementsByTagName("Frame")[-1].getAttribute("enter")
                    exits = line.getElementsByTagName("Frame")[-1].getAttribute("exit")

                    command = "insert into linecounting(line_id,enter, exitnum,timestamp) values (%s,%s,%s,'%s')" \
                              % (line_id, enters, exits, time_str)

                    sql_command.append(command)

            if polygons != []:
                for polygon in polygons:
                    poly_id = polygon.getAttribute("id")
                    occupancy = polygon.getAttribute("occupancy")
                    dwell = polygon.getAttribute("dwell")

                    enters = polygon.getElementsByTagName("Frame")[-1].getAttribute("enter")
                    exits = polygon.getElementsByTagName("Frame")[-1].getAttribute("exit")
                    #stay_time = float(occupancy) * float(dwell)#

                    command = "insert into polygoncounting(polygon_id, enter, exitnum,occupancy,dwell,timestamp) values (%s,%s,%s,%s,%s,'%s')" \
                              % (poly_id, enters, exits, occupancy, dwell, time_str)

                    sql_command.append(command)

            s = "@@@"
            sql_insertion = s.join(sql_command)
            sql_response = cloud_webService.sql_inserts(sql_insertion, dbname)
            sql_response_json = json.loads(sql_response)
            sql_status = sql_response_json["status"]
            if sql_status == "success":
                os.remove(path + xml_file)
                print "sql insertion success"
            if sql_status != "success":
                mv_command = 'mv *.log ' + log_path
                (status_mv, info) = cm.getstatusoutput(mv_command)
                if status_mv != 0:
                    print 'fail to move sql insertion log', info
                err_count = 0
                while True:
                    token_status = cloud_webService.get_token()
                    if token_status:
                        sql_response = cloud_webService.sql_inserts(sql_insertion, dbname)
                        sql_response_json = json.loads(sql_response)
                        sql_status = sql_response_json["status"]
                        print "token_status", token_status
                        print "sql_status", sql_status
                        if sql_status == "success":
                            os.remove(path + xml_file)
                            break
                        if sql_status != "success" and err_count <= 100:
                            mv_command = 'mv *.log ' + log_path
                            (status_mv, info) = cm.getstatusoutput(mv_command)
                            if status_mv != 0:
                                print 'fail to move sql insertion log', info
                            err_count += 1
                            time.sleep(5)
                        #TRY 5  times
                        if sql_status != "success" and err_count == 100:
                            mv_command = 'mv *.log ' + log_path
                            (status_mv, info) = cm.getstatusoutput(mv_command)
                            if status_mv != 0:
                                print 'fail to move sql insertion log', info
                            log_time = time.strftime('%Y-%m-%d_%H-%M', time.localtime(time.time()))
                            print "fail 5 times"
                            f = open('xml_' + log_time + '.log', 'a+')
                            f.write("4@no connection to Database at" + time_str)
                            f.close()
                            os.rename('xml_' + log_time + '.log', log_path + 'xml_' + log_time + '.log')
                            time.sleep(60)
                            err_count = 0
                            break
                    else:
                        mv_command = 'mv *.log ' + log_path
                        (status_mv, info) = cm.getstatusoutput(mv_command)
                        if status_mv != 0:
                            print 'fail to move token log', info
                        err_count += 1



        print "retrieved one round"
        time.sleep(20)

if __name__ == "__main__":
    while True:
        try:
            xml_read()
        except:
            print "main error"