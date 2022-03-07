import serial
import pynmea2
import time
import json
import requests 
import math
import decimal


pi = 3.141592653589793234
r_pi = pi * 3000.0 / 180.0
la = 6378245.0
ob = 0.00669342162296594323


def wgs84_gcj02(lon_wgs84, lat_wgs84):
    if judge_China(lon_wgs84, lat_wgs84):
        return [lon_wgs84, lat_wgs84]
    tlat = transformlat(lon_wgs84 - 105.0, lat_wgs84 - 35.0)
    tlng = transformlng(lon_wgs84 - 105.0, lat_wgs84 - 35.0)
    rlat = lat_wgs84 / 180.0 * pi
    m = math.sin(rlat)
    m = 1 - ob * m * m
    sm = math.sqrt(m)
    tlat = (tlat * 180.0) / ((la * (1 - ob)) / (m * sm) * pi)
    tlng = (tlng * 180.0) / (la / sm * math.cos(rlat) * pi)
    lat_gcj02 = lat_wgs84 + tlat
    lon_gcj02 = lon_wgs84 + tlng
    return [lon_gcj02, lat_gcj02]

def judge_China(lon, lat):
    if lon < 70 or lon > 140:
        return True
    if lat < 0 or lat > 55:
        return True
    return False

def transformlat(lon, lat):
    r = -100.0 + 2.0 * lon + 3.0 * lat + 0.2 * lat * lat + 0.1 * lon * lat + 0.2 * math.sqrt(math.fabs(lon))
    r += (20.0 * math.sin(6.0 * lon * pi) .+ 20.0 * math.sin(2.0 * lon * pi)) * 2.0 / 3.0
    r += (20.0 * math.sin(lat * pi) + 40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    r += (160.0 * math.sin(lat / 12.0 * pi) + 320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return r

def transformlng(lon, lat):
    r = 300.0 + lon + 2.0 * lat + 0.1 * lon * lon + 0.1 * lon * lat + 0.1 * math.sqrt(math.fabs(lon))
    r += (20.0 * math.sin(6.0 * lon * pi) + 20.0 * math.sin(2.0 * lon * pi)) * 2.0 / 3.0
    r += (20.0 * math.sin(lon * pi) + 40.0 * math.sin(lon / 3.0 * pi)) * 2.0 / 3.0
    r += (150.0 * math.sin(lon / 12.0 * pi) + 300.0 * math.sin(lon / 30.0 * pi)) * 2.0 / 3.0
    return r

def lat_lng_convert(lat_lng_data):
    lat_lng_data = float(lat_lng_data) / 100.0
    lat_lng_data = int(lat_lng_data) + (lat_lng_data - int(lat_lng_data)) * 100.0 / 60.0 
    return lat_lng_data


ser = serial.Serial("/dev/ttyUSB0", 9600 )  
while(True):
        dataList = str(ser.readline())[2:][:-5].split(',')
        if '$GNRMC' in dataList:

           gcj02_lng = wgs84_gcj02(lat_lng_convert(dataList[5]),lat_lng_convert(dataList[3]))[0]
           gcj02_lat = wgs84_gcj02(lat_lng_convert(dataList[5]),lat_lng_convert(dataList[3]))[1]

           url = "http://127.0.0.1:8080/api/status-info"
           data = {"label":"gps","lat":gcj02_lat,"lng":gcj02_lng}
           headers = {'content-type': 'application/json','charset': 'utf-8'}
           res = requests.post(url,data=json.dumps(data),headers=headers)
