import time
import board
import busio
import smbus
import struct
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import requests
import json
import os


def readADS1115(PIN):
    
    pin = PIN
    chan = "chan" + str(pin)
    chanPin = "ADS.P" + str(pin)
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1015(i2c)
    chan = AnalogIn(ads, chanPin)
    voltage = float('%0.2f'%(chan.voltage * 5))
    return voltage

def readUPS(bus):
    address = 0x36
    read = bus.read_word_data(address, 0X04)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    capacity = swapped/256
    return capacity

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
        voltage = readADS1115(PIN=0)
        if voltage == 0:
           continue
        Color = colorStatus(voltage,10.2,9)
        voltage = str(voltage) + "v"
        postStatus(Color,"电压",voltage)
     except:
        postStatus("red","电压","异常")
        pass
     
     try:
        bus = smbus.SMBus(1)
        upsCapacity = readUPS(bus)
        Color = colorStatus(upsCapacity,50,20)
        upsCapacity = str(int(upsCapacity)) + "%"
        postStatus(Color,"UPS",upsCapacity)
     except:
        postStatus("red","UPS","异常")
        pass
    
     try:
        temp = float(os.popen("vcgencmd measure_temp|sed 's/[^0-9,.]//g'").read())            
        Color = colorStatus(100-temp,60,40)
        temp = str(temp) + "'C"
        postStatus(Color,"温度",temp)
     except:
         postStatus("red","温度","异常")
         pass

     time.sleep(0.5)
