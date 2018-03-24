# vim: expandtab:ts=4:sw=4

import os, sys
import commands as cm
import hashlib
import urllib, urllib2
import json
import logging
import pytz
import datetime

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
import ssl
import time


class cloudWebService:
    def __init__(self, clouduplink_ip):
        ssl._create_default_https_context = ssl._create_unverified_context
        self.clouduplink_ip = clouduplink_ip
        m = hashlib.md5()
        m.update('Xjtu123456')
        pwd = m.hexdigest()
        self.username = "admin"
        self.values = {'username': 'admin', 'password': pwd, 'task': ''}
        self.token = ''
        self.errorfilePath = "."

    def getErrorLineNo(self):
        return str(sys.exc_info()[-1].tb_lineno)

    def writeErrorInfo(self,typeid, e):
        timestamp = datetime.datetime.now(pytz.timezone('America/Los_Angeles')).strftime("%Y-%m-%d_%H-%M-%S")
        error = 'Error on line {}:{}'.format(sys.exc_info()[-1].tb_lineno, e)
        with open(self.errorfilePath + "/webservice_" + timestamp + ".log", "a+") as f:
            error = str(typeid)+"@" + error + "\n"
            f.writelines(error)

    def get_token(self):
        # get request
        errorCount = 0
        self.values.update({'task': 'get'})
        values_url = urllib.urlencode(self.values)
        url = 'https://' + self.clouduplink_ip + '/configurator/token.php' + '?' + values_url
        # print url
        while errorCount < 3:
            try:
                request = urllib2.Request(url)
                response = urllib2.urlopen(request, timeout=30)
                response = response.read()
                response = json.loads(response)
                status = response["status"]

                if 'success' == status:
                    self.token = response["token"]
                    break
                    #return True
                else:
                    errorInfo = ""
                    if response.has_hey("error"):
                        errorInfo = str(response["error"])
                    # logging.error("get token failed!"+str(errorInfo))
                    raise Exception(str(errorInfo))
            except BaseException, e:
                # logging.error("sql request failed at time " + str(errorCount) + " : line : " + self.getErrorLineNo() + ":" + str(e))
                self.writeErrorInfo(14,e)
                errorCount += 1
                status = "fail"
                time.sleep(10)
        if status == "success":
             return True
        else:
            return False


    # fileCloud_path = "uplinktest/"
    # container_name = "office"
    # file_name = "test.jpg"
    def file_request(self, container_name,fileCloud_path,file_name):
        errorCount = 0
        # post request
        url = "https://" + self.clouduplink_ip + "/webservice/update.php"
        register_openers()
        errorInfo = ""
        while errorCount < 3:
            try:
                token = self.token
                datagen, headers = multipart_encode(
                    {"task": 'file_request', 'username': self.username, 'token': token,
                     "filetoupload": open(file_name, "rb"),
                     "fileCloud_path": fileCloud_path, "container_name": container_name})
                request = urllib2.Request(url, datagen, headers)

                response = urllib2.urlopen(request, timeout=300).read()

                responseObj = json.loads(response)
                status = responseObj["status"]

                if status == "success":
                    break
                else:
                    if responseObj.has_key("error"):
                        errorInfo = str(responseObj["error"])
                    # logging.error("file_request failed!" + str(errorInfo))
                    raise Exception(str(errorInfo))
            except BaseException, e:
                # logging.error("file_request failed at time " + str(errorCount) + " : line : " + self.getErrorLineNo() + ":" + str(e))
                errorInfo = str(e)
                self.writeErrorInfo(14,e)
                time.sleep(10)
                errorCount += 1
                status = "fail"
                tokenST = self.get_token()
                if tokenST == True:
                    continue
                else:
                    break

        if status == "success":
            return response
        else:
            response = {'status': 'fail', 'content': errorInfo}
            response = json.dumps(response)
            return response

    def sql_request(self,sql,dbname):
        errorCount = 0
        # post request
        url = "https://" + self.clouduplink_ip + "/webservice/update.php"
        register_openers()
        errorInfo = ""
        while errorCount < 3:
            try:
                token = self.token
                datagen, headers = multipart_encode({"task": 'sql_request', 'username': self.username, 'token': token,
                                                     'sql': sql, 'dbname': dbname})
                request = urllib2.Request(url, datagen, headers)

                response = urllib2.urlopen(request, timeout=50).read()
                responseObj = json.loads(response)
                status = responseObj["status"]

                if status == "success":
                    break
                else:

                    if responseObj.has_key("error"):
                        errorInfo = str(responseObj["error"])
                    # logging.error("sql_request failed!" + str(errorInfo))
                    raise Exception(str(errorInfo))

            except BaseException, e:
                # logging.error("sql request failed at time " + str(errorCount) + " : line : " + self.getErrorLineNo() + ":" + str(e))
                errorInfo = str(e)
                self.writeErrorInfo(14,e)
                time.sleep(10)
                errorCount += 1
                status = "fail"
                tokenST = self.get_token()
                if tokenST == True:
                    continue
                else:
                    break
        if status == "success":
            return response
        else:
            response = {'status': 'fail', 'content': errorInfo}
            response = json.dumps(response)
            return response


    def sql_inserts(self,sql,dbname):
        errorCount = 0
        # post request
        url = "https://" + self.clouduplink_ip + "/webservice/update.php"
        register_openers()
        errorInfo = ""
        while errorCount < 3 :
            try:
                token = self.token
                datagen, headers = multipart_encode({"task": 'sql_inserts', 'username': self.username, 'token': token,
                                                     'sql': sql, 'dbname': dbname})
                request = urllib2.Request(url, datagen, headers)

                response = urllib2.urlopen(request, timeout=50).read()
                responseObj = json.loads(response)
                status = responseObj["status"]
                if status == "success":
                    if not responseObj.has_key("Exception"):
                        break
                    else:
                        errorObjDict = responseObj["Exception"]
                        sqlList = errorObjDict.keys()
                        # errorList = errorObjDict.values()
                        sql = ""
                        for sqlItem in sqlList:
                            sql = sql + sqlItem+"@@@"
                        sql = sql[:-3]
                        # status = "fail"
                        raise Exception(str(errorObjDict))


                else:
                    if responseObj.has_hey("error"):
                        errorInfo = str(responseObj["error"])
                    # logging.error("sql_inserts failed!" + str(errorInfo))
                    raise Exception(str(errorInfo))

            except BaseException, e:
                # logging.error("sql inserts failed at time " + str(errorCount) + " : line : " + self.getErrorLineNo()+":"+str(e))
                errorInfo = str(e)
                self.writeErrorInfo(14,e)
                time.sleep(10)
                errorCount += 1
                status = "fail"
                tokenST = self.get_token()
                if tokenST == True:
                    continue
                else:
                    break
        if status == "success":
            return response
        else:
            response = {'status': 'fail', 'content': errorInfo}
            response = json.dumps(response)
            return response
                # response = {'status': 'fail', 'fileCloud': ''}
                # response = json.dumps(response)
                # return response

    def get_token_http(self):
        # get request
        self.values.update({'task': 'get'})
        values_url = urllib.urlencode(self.values)
        url = 'http://' + self.clouduplink_ip + '/configurator/token.php' + '?' + values_url
        print url
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            response = response.read()
            response = json.loads(response)
            status = response["status"]

            if 'success' == status:
                self.token = response["token"]
                return True
            else:
                return False

        except:
            return False

    # fileCloud_path = "uplinktest/"
    # container_name = "office"
    # file_name = "test.jpg"
    def file_request_http(self, container_name,fileCloud_path,file_name):
        # post request
        url = "http://" + self.clouduplink_ip + "/webservice/update.php"
        register_openers()

        try:
            token = self.token
            datagen, headers = multipart_encode(
                {"task": 'file_request', 'username': self.username, 'token': token,
                 "filetoupload": open(file_name, "rb"),
                 "fileCloud_path": fileCloud_path, "container_name": container_name})
            request = urllib2.Request(url, datagen, headers)

            response = urllib2.urlopen(request).read()
            print response
            # response = json.loads(response)

            return response
            print "upload file ok"
        except:
            response = {'status': 'fail', 'fileCloud': ''}
            response = json.dumps(response)
            return response


    def sql_request_http(self,sql,dbname):
        # post request
        url = "http://" + self.clouduplink_ip + "/webservice/update.php"
        register_openers()
        try:
            token = self.token
            datagen, headers = multipart_encode({"task": 'sql_request', 'username': self.username, 'token': token,
                                                 'sql': sql, 'dbname': dbname})
            request = urllib2.Request(url, datagen, headers)

            response = urllib2.urlopen(request).read()
            print response
            # response = json.loads(response)

            return response

        except:
            response = {'status': 'fail', 'fileCloud': ''}
            response = json.dumps(response)
            return response



