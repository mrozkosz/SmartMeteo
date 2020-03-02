#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import os
import glob
import pyrebase
import Adafruit_DHT
from RPi import GPIO
import lcddriver
import json
import serial, time, struct, array
from datetime import datetime
config = {
    "apiKey": "AAAATg9MbWg:APA91bGA3MdMCyBORDeeu3YKu2Tf1cxGI7YBwH8eT8FlJXJLJ25RIPq5HXs9-TLAhQZdVQW5SQtCgYeZk5la_Tf6iKEW80aCq$",
    "authDomain": "mcloud - 2a08f.firebaseio.com",
    "databaseURL": "https://mcloud-2a08f.firebaseio.com",
    "storageBucket": "mcloud-2a08f.appspot.com"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()
# End of firebase configuration

# Humidity and temperature module implementation
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
# End of module implementation
display = lcddriver.lcd()
timestamp = 0
data = dict()
isDeclared = 'false'
#PM sensor
ser = serial.Serial()
ser.port = "/dev/ttyUSB0" 
ser.baudrate = 9600
ser.open()
ser.flushInput()
  # ser.write('\x01')
def get_data():
  humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
  if  humidity is not None and temperature is not None:
    print("Temperatura={0:1f}*C Wilgotnosc={1:0.1f}%".format(temperature, humidity))
    isDeclared = 'true'
    timestamp = int(time.time())
    data["tempC"] = round(float(temperature),2)
    
    data["humi"] = round(float(humidity),2)
		#  = {"tempC": temperature, "humi": humidity}
    db.child("SM-001").child(timestamp).set(data)
  else:
    print("Blad pobrania danych")
def displayLCD():
  try:
    display.lcd_clear()
    display.lcd_display_string("Temperatura:"+str(round(data["tempC"], 1)), 1) 
    display.lcd_display_string("Wilgotnosc: "+str(round(data["humi"],0)), 2)
    time.sleep(5)
    display.lcd_clear()
    display.lcd_display_string("PM2.5:"+str(data["pm25"])+"ug/m^3",1)
    display.lcd_display_string("PM10: "+str(data["pm10"])+"ug/m^3",2)
    time.sleep(5)
    display.lcd_clear()
    display.lcd_display_string("Normy: PM2.5: 20",1)
    display.lcd_display_string("PM10: 40",2)
    time.sleep(5)
    display.lcd_clear()
    display.lcd_display_string("PM 2.5: " + str(data["pm25"]/20 * 100) + "%",1)
    display.lcd_display_string("PM  10: " + str(data["pm10"]/40 *100)+"%",2)                                       
  except KeyboardInterrupt:
    print("Cleaning up!")
    display.lcd_clear()

def getPM():
  
  # ser = serial.Serial()
 
  
  byte, lastbyte = "\x00", "\x00"
  cnt = 0
  while cnt<1:
    lastbyte = byte
    byte = ser.read(size=1)
    if lastbyte == "\xAA" and byte == "\xC0":
      sentence = ser.read(size=8) 
      readings = struct.unpack('<hhxxcc',sentence) 
      pm_25 = readings[0]/10.0
      pm_10 = readings[1]/10.0
      data["pm25"] = pm_25
      data["pm10"] = pm_10
      cnt += 1
      line = "PM 2.5: {} μg/m^3  PM 10: {} μg/m^3".format(pm_25, pm_10)
      print(datetime.now().strftime("%d %b %Y %H:%M:%S.%f: ")+line)

def sensor_sleep(self):
  bytes = ['\xaa', #head
            '\xb4', #command 1
            '\x06', #data byte 1
            '\x01', #data byte 2 (set mode)
            '\x00', #data byte 3 (sleep)
            '\x00', #data byte 4
            '\x00', #data byte 5
            '\x00', #data byte 6
            '\x00', #data byte 7
            '\x00', #data byte 8
            '\x00', #data byte 9
            '\x00', #data byte 10
            '\x00', #data byte 11
            '\x00', #data byte 12
            '\x00', #data byte 13
            '\xff', #data byte 14 (device id byte 1)
            '\xff', #data byte 15 (device id byte 2)
            '\x05', #checksum
            '\xab'] #tail

  for b in bytes:
    ser.write(b)
while True:
  getPM()
  sensor_sleep
  get_data()
  if isDeclared:
    displayLCD()
  time.sleep(30)
