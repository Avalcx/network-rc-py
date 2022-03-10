import serial
import time
import json
import requests 
import math

pi = 3.141592653589793234

def lng_lat_algorithm(gps_lng, gps_lat):

    def lng_lat_convert(lng_lat_data):
        lng_lat_data = float(lng_lat_data) / 100.0
        lng_lat_data = int(lng_lat_data) + (lng_lat_data - int(lng_lat_data)) * 100.0 / 60.0 
        return lng_lat_data  

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

    def wgs84_gcj02(lng, lat):
        lng = lng_lat_convert(lng)
        lat = lng_lat_convert(lat)
        rlat = lat / 180.0 * pi
        m = 1 - 0.00669342162296594323 * math.sin(rlat) * math.sin(rlat)
        sm = math.sqrt(m)
        tlat = (transformlat(lng - 105.0, lat - 35.0) * 180.0) / ((6378245.0 * (1 - 0.00669342162296594323)) / (m * sm) * pi)
        tlng = (transformlng(lng - 105.0, lat - 35.0) * 180.0) / (6378245.0 / sm * math.cos(rlat) * pi)
        lng = lng + tlng
        lat = lat + tlat
        return [lng,lat]


    return wgs84_gcj02(gps_lng, gps_lat)

ser = serial.Serial("/dev/ttyS0", 9600)
while(True):
        gpsList = str(ser.readline())[2:][:-3].split(',')
        if '$GNRMC' in gpsList and gpsList[2] == "A":
            try:
               print(gpsList)
               gcj02_lng = lng_lat_algorithm(gpsList[5],gpsList[3])[0]
               gcj02_lat = lng_lat_algorithm(gpsList[5],gpsList[3])[1]
               speed = str(round((float(gpsList[7]) * 1.852),2)) + "km/h"
               url = "http://127.0.0.1:8080/api/status-info"
               data = {"label":"gps","lng":gcj02_lng,"lat":gcj02_lat}
               headers = {'content-type': 'application/json','charset': 'utf-8'}
               res = requests.post(url,data=json.dumps(data),headers=headers)
               data = {"label":"速度","value":speed,"color":"green"}
               res = requests.post(url,data=json.dumps(data),headers=headers)

            except:
               pass
