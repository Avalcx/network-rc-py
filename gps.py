import serial
import time
import json
import requests 
import math


pi = 3.141592653589793234
r_pi = pi * 3000.0 / 180.0
la = 6378245.0
ob = 0.00669342162296594323


def wgs84_gcj02(lng_wgs84, lat_wgs84):

    def lng_lat_convert(lng_lat_data):
        lng_lat_data = float(lng_lat_data) / 100.0
        lng_lat_data = int(lng_lat_data) + (lng_lat_data - int(lng_lat_data)) * 100.0 / 60.0 
        return lng_lat_data
    
    def judge_China(lng, lat):
        if lng < 70 or lng > 140:
            return True
        if lat < 0 or lat > 55:
            return True      
        return False

    def transformlat(lng, lat):
        r = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        r += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        r += (20.0 * math.sin(lat * pi) + 40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
        r += (160.0 * math.sin(lat / 12.0 * pi) + 320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
        return r

    def transformlng(lng, lat):
        r = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        r += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        r += (20.0 * math.sin(lng * pi) + 40.0 * math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
        r += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 * math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
        return r

    lng_wgs84 = lng_lat_convert(lng_wgs84)
    lat_wgs84 = lng_lat_convert(lat_wgs84)

    if judge_China(lng_wgs84, lat_wgs84):
        return [lng_wgs84, lat_wgs84]

    tlat = transformlat(lng_wgs84 - 105.0, lat_wgs84 - 35.0)
    tlng = transformlng(lng_wgs84 - 105.0, lat_wgs84 - 35.0)
    rlat = lat_wgs84 / 180.0 * pi
    m = math.sin(rlat)
    m = 1 - ob * m * m
    sm = math.sqrt(m)
    tlat = (tlat * 180.0) / ((la * (1 - ob)) / (m * sm) * pi)
    tlng = (tlng * 180.0) / (la / sm * math.cos(rlat) * pi)
    lat_gcj02 = lat_wgs84 + tlat
    lng_gcj02 = lng_wgs84 + tlng
    return [lng_gcj02, lat_gcj02]


ser = serial.Serial("/dev/ttyUSB0", 9600 ) 
while(True):
        dataList = str(ser.readline())[2:][:-5].split(',')
        if '$GNRMC' in dataList:

           gcj02_lng = wgs84_gcj02(dataList[5],dataList[3])[0]
           gcj02_lat = wgs84_gcj02(dataList[5],dataList[3])[1]
  
           url = "http://127.0.0.1:8080/api/status-info"
           data = {"label":"gps","lat":gcj02_lat,"lng":gcj02_lng}
           headers = {'content-type': 'application/json','charset': 'utf-8'}
           res = requests.post(url,data=json.dumps(data),headers=headers)