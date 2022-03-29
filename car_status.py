'''
sudo pip3 install adafruit-circuitpython-ads1x15
sudo pip3 install board
'''

import time
import board
import busio
#import smbus
#import struct
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import requests
import json
import os

def readADS1115(PIN):
    
    pin = PIN
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1015(i2c)
    if pin == 0:
        chan = AnalogIn(ads,ADS.P0)
    elif pin == 1:
        chan = AnalogIn(ads,ADS.P1)
    elif pin == 2:
        chan = AnalogIn(ads,ADS.P2)
    elif pin == 3: 
        chan = AnalogIn(ads,ADS.P3)  
    voltage = chan.voltage
    return voltage
'''
def readUPS(bus):
    address = 0x36
    read = bus.read_word_data(address, 0X04)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    capacity = swapped/256
    return capacity
'''
def postStatus(Color,Label,Value):

    url = "http://127.0.0.1:8080/api/status-info"
    data = {"color":Color,"label":Label,"value":Value}
    headers = {'content-type': 'application/json','charset': 'utf-8'}
    res = requests.post(url,data=json.dumps(data),headers=headers)

def colorStatus(value,Green,Red):

    if value > Green:
       return "green"
    elif Red < value < Green:
       return "orange"
    elif value < Red:
       return "red"


while True:
     try:
        voltage = float('%.2f'%(readADS1115(PIN=0) * 5))
        if voltage == 0:
           continue
        Color = colorStatus(voltage,10.2,9)
        voltage = str(voltage) + "v"
        postStatus(Color,"电压",voltage)
     except:
        postStatus("red","电压","异常")
        pass
     '''
     try:
        bus = smbus.SMBus(1)
        upsCapacity = readUPS(bus)
        Color = colorStatus(upsCapacity,50,20)
        upsCapacity = str(int(upsCapacity)) + "%"
        postStatus(Color,"UPS",upsCapacity)
     except:
        postStatus("red","UPS","异常")
        pass
    '''
     try:
        temp = float(os.popen("vcgencmd measure_temp|sed 's/[^0-9,.]//g'").read())            
        Color = colorStatus(100-temp,60,40)
        temp = str(temp) + "℃"
        postStatus(Color,"温度",temp)
     except:
         postStatus("red","温度","异常")
         pass

     time.sleep(0.5)
