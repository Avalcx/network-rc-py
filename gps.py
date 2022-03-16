import time
import os
import math
import requests
import json
import serial
import re

class GPS(object):
    pi = 3.141592653589793234
    r_pi = pi * 3000.0 / 180.0

    def __init__(self,gps_lng,gps_lat):
        self.gps_lng = gps_lng
        self.gps_lat = gps_lat
    
    def lng_lat_convert(self,lng_lat_data):
        lng_lat_data = float(lng_lat_data) / 100.0
        lng_lat_data = int(lng_lat_data) + (lng_lat_data - int(lng_lat_data)) * 100.0 / 60.0 
        return lng_lat_data  

    def transformlat(self,lng,lat):
        r = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        r += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 * math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        r += (20.0 * math.sin(lat * self.pi) + 40.0 * math.sin(lat / 3.0 * self.pi)) * 2.0 / 3.0
        r += (160.0 * math.sin(lat / 12.0 * self.pi) + 320 * math.sin(lat * self.pi / 30.0)) * 2.0 / 3.0
        return r

    def transformlng(self,lng,lat):
        r = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        r += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 * math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        r += (20.0 * math.sin(lng * self.pi) + 40.0 * math.sin(lng / 3.0 * self.pi)) * 2.0 / 3.0
        r += (150.0 * math.sin(lng / 12.0 * self.pi) + 300.0 * math.sin(lng / 30.0 * self.pi)) * 2.0 / 3.0
        return r

    def wgs84_gcj02(self):
        lng = self.lng_lat_convert(self.gps_lng)
        lat = self.lng_lat_convert(self.gps_lat)
        rlat = lat / 180.0 * self.pi
        m = 1 - 0.00669342162296594323 * math.sin(rlat) * math.sin(rlat)
        sm = math.sqrt(m)
        tlat = (self.transformlat(lng - 105.0, lat - 35.0) * 180.0) / ((6378245.0 * (1 - 0.00669342162296594323)) / (m * sm) * self.pi)
        tlng = (self.transformlng(lng - 105.0, lat - 35.0) * 180.0) / (6378245.0 / sm * math.cos(rlat) * self.pi)
        lng = lng + tlng
        lat = lat + tlat
        return [lng,lat]
    
    def wgs84_bd09(self):
        self.gps_lng = self.wgs84_gcj02()[0]
        self.gps_lat = self.wgs84_gcj02()[1]
        b = math.sqrt(self.gps_lng * self.gps_lng + self.gps_lat * self.gps_lat) + 0.00002 * math.sin(self.gps_lat * self.r_pi)
        o = math.atan2(self.gps_lat, self.gps_lng) + 0.000003 * math.cos(self.gps_lng * self.r_pi)
        lng = b * math.cos(o) + 0.0065
        lat = b * math.sin(o) + 0.006
        return [lng,lat]


class PostInfo(object):

    def __init__(self):
        self.lng = None
        self.lat = None
        self.speed = None

    def Status(self,Speed):
        self.speed = Speed
        url = "http://127.0.0.1:8080/api/status-info"
        data = {"color":"green","label":"速度","value":self.speed}
        headers = {'content-type': 'application/json','charset': 'utf-8'}
        res = requests.post(url,data=json.dumps(data),headers=headers)

    def GPS(self,Lng,Lat):
        self.lng = Lng
        self.lat = Lat
        url = "http://127.0.0.1:8080/api/status-info"
        data = {"label":"gps","lng":self.lng,"lat":self.lat}
        headers = {'content-type': 'application/json','charset': 'utf-8'}
        res = requests.post(url,data=json.dumps(data),headers=headers)


def setL76x():
    def L76X_Send_Command(ser,data):
        Temp = '0123456789ABCDEF*'
        Check = ord(data[1]) 
        for i in range(2, len(data)):
            Check = Check ^ ord(data[i]) 
        data = data + Temp[16]
        data = data + Temp[int(Check/16)]
        data = data + Temp[int(Check%16)]
        
        ser.write(data.encode())
        ser.write('\r'.encode())
        ser.write('\n'.encode())
    ser = serial.Serial("/dev/ttyS0",115200)
    L76X_Send_Command(ser,'$PMTK251,115200')
    time.sleep(2)
    ser = serial.Serial("/dev/ttyS0",115200)
    L76X_Send_Command(ser,'$PMTK220,800')
    return ser

#ser=setL76x()

#开启pi的硬件串口，关闭软串口，方法：
    # raspi-config →→→→
    # 3-Interface Options →→→→
    # P6 Serial Port →→→→
    # 1.No  2.Yes →→→→
    # reboot
    
ser = serial.Serial("/dev/ttyS0",9600)

while True:
        dataList = re.sub('\r|\n','',ser.readline().decode(encoding="utf8",errors="ignore")).split(',')
        if '$GNRMC' in dataList and dataList[2] == "A":
            gps = GPS(dataList[5],dataList[3])
            lng = gps.wgs84_gcj02()[0]
            lat = gps.wgs84_gcj02()[1]
            speed = str(round((float(dataList[7]) * 1.852),2)) + "km/h"
            print(lng,lat)
            post = PostInfo()
            post.Status(speed)
            post.GPS(lng,lat)