#! /usr/bin/python
import os
import commands as cm
import datetime
import time
import json
import fcntl
import calendar
import os
from dateutil.relativedelta import relativedelta

xmlFileFolder = "/home/sijun/sijun"
readyFile = "./ready.log"
list = []

def file_sort(f_dir):
    print f_dir
    status, info = cm.getstatusoutput(f_dir)
    info = info.split()
    # print "info",info

    if info == []:
        result = []
        return result

    dic = {}
    for i in range(0, len(info)):
        ts = info[i].split("_")
        dic[info[i]] = ts[2] + "_" + ts[3]

    rd = sorted(dic.items(), lambda x, y: cmp(x[1], y[1]))
    result = []
    for i in range(0, len(rd)):
        result.append(rd[i][0])
    return result

def change2DailyBegin(dt):
    hour = dt.hour
    if int(hour) >= 0 and int(hour) <= 6:
        dt = dt - datetime.timedelta(days=1)
    year = dt.year
    month = dt.month
    day = dt.day
    hour = 7
    dt = datetime.datetime(year, month, day, hour)
    return dt

def change2MonthlyBegin(dt):
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    if day == 1 and hour >= 0 and hour <= 6:
        year = (dt - relativedelta(months = 1)).year
        month = (dt - relativedelta(months = 1)).month
    day = 1
    hour = 7
    dt = datetime.datetime(year,month,day,hour)
    return dt

if os.path.exists(readyFile):
    with open(readyFile,"r") as f:
        try:
            dic = json.load(f)
        except BaseException, e:
            print e
else:
    with open(readyFile,"a+") as f:
        dic = {"hourly": [], "daily": [], "monthly": []}
        json.dump(dic, f)



beginFlag = True
histFile = ""
while True:
    with open(readyFile,"a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        dic = json.load(f)
        file_dir = "ls " + xmlFileFolder
        filesList = file_sort(file_dir)
        if len(filesList) != 0:
            curFile = filesList[0]
            if beginFlag:
                histFile = curFile
            else:
                histYear = histFile.split("_")[2][0:4]
                histMonth = histFile.split("_")[2][5:7]
                histDay = histFile.split("_")[2][8:10]
                histHour = histFile.split("_")[3][0:2]
                histDateTime = datetime.datetime(int(histYear),int(histMonth),int(histDay),int(histHour))

                curYear = curFile.split("_")[2][0:4]
                curMonth = curFile.split("_")[2][5:7]
                curDay = curFile.split("_")[2][8:10]
                curHour = curFile.split("_")[3][0:2]
                curMin = curFile.split("_")[3][3:5]
                curDateTime = datetime.datetime(int(curYear), int(curMonth), int(curDay), int(curHour),int(curMin))

                seconds = (curDateTime - histDateTime).seconds
                days = (curDateTime - histDateTime).days
                if curDateTime > histDateTime:
                    seconds = (curDateTime - histDateTime).seconds
                    if seconds >= 3600:
                        dic["hourly"].append(histDateTime.strftime("%Y-%m-%d %H:%M:%S"))
                        dayBeginDT = change2DailyBegin(histDateTime)##NOTE
                        deltaDays = (curDateTime - dayBeginDT).days
                        if deltaDays >= 1:
                            dic["daily"].append(dayBeginDT.strftime("%Y-%m-%d %H:%M:%S"))
                            monthBeginDT = change2MonthlyBegin(histDateTime)##NOTE
                            lastMonthOfToday = curDateTime - relativedelta(months = 1)
                            # yearTmp = monthBeginDT.year
                            # monthTmp = monthBeginDT.month
                            # if
                            # days = calendar.monthrange(int(yearTmp), int(monthTmp))[1]
                            if monthBeginDT <= lastMonthOfToday:
                                dic["monthly"].append(monthBeginDT.strftime("%Y-%m-%d %H:%M:%S"))
                        fileWriter = open(readyFile, "w")
                        json.dump(dic, fileWriter)
                        fileWriter.flush()
                        fileWriter.close()


                    else:
                        print "world"
                else:
                    print "need time exchange"
            histFile = curFile


        fcntl.flock(f, fcntl.LOCK_UN)
        os.remove(xmlFileFolder+"/"+curFile)
    beginFlag = False
    time.sleep(2)
print "hello"