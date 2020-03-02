#!/usr/bin/python
# -*- coding: UTF-8 -*-
#Imports
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
from decimal import Decimal

# Constants
SENSOR_SERIAL_NUMBER = "SM-005"
DATA_DELAY_TIME = 0

# Firebase config
config = {
    "apiKey": "AAAATg9MbWg:APA91bGA3MdMCyBORDeeu3YKu2Tf1cxGI7YBwH8eT8FlJXJLJ25RIPq5HXs9-TLAhQZdVQW5SQtCgYeZk5la_Tf6iKEW80aCq$",
    "authDomain": "mcloud - 2a08f.firebaseio.com",
    "databaseURL": "https://mcloud-2a08f.firebaseio.com",
    "storageBucket": "mcloud-2a08f.appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Humidity and temperature module implementation
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

#LCD implementation
display = lcddriver.lcd()
data = dict()
isPmSensor = True
ser = serial.Serial()

#PM sensor implementation
def pmSensorSetUp():
  global ser
  global isPmSensor
  try:
    print("Main try")
    ser.port = "/dev/ttyUSB0"
    ser.baudrate = 9600
    ser.open()
    ser.flushInput()
  except Exception:
    print("Serial exception")
    isPmSensor = False


def getTmpAndHumid():
  humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
  if humidity is None:
    humidity = 0
  if temperature is None:
    temperature = 0
  return humidity, temperature

def getPm10AndPm25():
  global ser
  global isPmSensor
  if isPmSensor:
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
        cnt += 1
        line = "PM 2.5: {} μg/m^3  PM 10: {} μg/m^3".format(pm_25, pm_10)
        print(datetime.now().strftime("%d %b %Y %H:%M:%S.%f: ")+line)
        return pm_10, pm_25
  else:
    return 0, 0

def displayLCD(humidity, temperature, pm10, pm25):
  global display
  try:
    display.lcd_clear()
    display.lcd_display_string("Temperatura:{:3.1f}".format(temperature),1)
    display.lcd_display_string("Wilgotnosc: {:3.1f}".format(humidity),2)
    time.sleep(5)
    display.lcd_clear()
    display.lcd_display_string("PM 2.5:{:3.1f}".format(pm25),1)
    display.lcd_display_string("PM  10:{:3.1f}".format(pm10),2)
    time.sleep(5)
    display.lcd_clear()
    display.lcd_display_string("PM 2.5:{:4.1f}%".format(pm25 * 5),1) # NORMA TO 20 * 100% = 5
    display.lcd_display_string("PM  10:{:4.1f}%".format(pm10 * 2.5),2) # NORMA TO 40 * 100% = 2.5
    time.sleep(5)
  except KeyboardInterrupt:
    print("Cleaning up!")
    display.lcd_clear()

# PM Sensor SetUp
pmSensorSetUp()

#def turnOffUsb():
#   bashCommand = "cwm --rdf test.rdf --ntriples > test.nt"
#   import subprocess
#   process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
#   output, error = process.communicate()

#Main loop
while True:
  print("Getting tempertaure and humidity")
  humidity, temperature = getTmpAndHumid()
  print("Getting PM10 and PM2.5")
  pm10, pm25 = getPm10AndPm25()
# turnOffUsb()

  data["tempC"] = round(float(temperature),1)
  data["humi"] = round(float(humidity),1)
  data["pm25"] = round(float(pm25),1)
  data["pm10"] = round(float(pm10),1)
  data["timestamp"] = int(time.time())

  line = "\nTemp: {} Humi:{} PM 2.5: {} μg/m^3  PM 10: {} μg/m^3".format(temperature,humidity,pm10, pm25)
  print(datetime.now().strftime("%d %b %Y %H:%M:%S.%f: ") + line)
  timestamp = int(time.time())

  print("Saving data to Firebase...")
  db.child(SENSOR_SERIAL_NUMBER).push(data)
  print("Data saved!")

  displayLCD(humidity, temperature, pm10, pm25)
  displayLCD(humidity, temperature, pm10, pm25)
  time.sleep(DATA_DELAY_TIME)
