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
import logging

logging.basicConfig(filename='smartMeteo.log', filemode='a',
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
 level=logging.INFO)
logging.info('              Application startup               ')
logging.info('################################################')
logging.info('&    **************    ****           ****     &')
logging.info('&    **************    *****         *****     &')
logging.info('&    ***               *** **       ** ***     &')
logging.info('&    ***               ***  **     **  ***     &')
logging.info('&    ***************   ***   *******   ***     &')
logging.info('&    ***************   ***     ***     ***     &')
logging.info('&                ***   ***             ***     &')
logging.info('&                ***   ***             ***     &')
logging.info('&    ***************   ***             ***     &')
logging.info('&    ***************   ***             ***     &')
logging.info('################################################')


# Constants
SENSOR_SERIAL_NUMBER = "SM-005"
DATA_DELAY_TIME = 1800
logging.info('Sensor serial number: %s ' + SENSOR_SERIAL_NUMBER)

# Firebase config
config = {
    "apiKey": "AAAATg9MbWg:APA91bGA3MdMCyBORDeeu3YKu2Tf1cxGI7YBwH8eT8FlJXJLJ25RIPq5HXs9-TLAhQZdVQW5SQtCgYeZk5la_Tf6iKEW80aCq$",
    "authDomain": "mcloud - 2a08f.firebaseio.com",
    "databaseURL": "https://mcloud-2a08f.firebaseio.com",
    "storageBucket": "mcloud-2a08f.appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
logging.info('Database connected!')

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
    logging.info("PM sensor is getting up")
    ser.port = "/dev/ttyUSB0"
    ser.baudrate = 9600
    ser.open()
    ser.flushInput()
    logging.info('PM sensor connection passed!')
  except Exception:
    print("Serial exception")
    logging.error('PM sensor connection failed!')
    isPmSensor = False


def getTmpAndHumid():
  humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
  if humidity is None:
    humidity = 0
    logging.error('Humidity wrong value!')
  if temperature is None:
    temperature = 0
    logging.error('Temperature wrong value!')
  return humidity, temperature

def getPm10AndPm25():
  print("Getting PM10 and PM2.5")
  logging.info("Getting PM10 and PM2.5 values")
  sensor_wake()
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
        sensor_sleep()
        print("Sensor sleep")
        return pm_10, pm_25
  else:
    sensor_sleep()
    print("Sensor sleep")
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
    logging.warning("LCD ERROR")
    display.lcd_clear()

# 0xAA, 0xB4, 0x06, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x06, 0xAB
def sensor_wake():
    bytes = ['\xaa', #head
    '\xb4', #command 1
    '\x06', #data byte 1
    '\x01', #data byte 2 (set mode)
    '\x01', #data byte 3 (sleep)
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
    '\x06', #checksum
    '\xab'] #tail

    for b in bytes:
        ser.write(b)
    
    # xAA, 0xB4, 0x06, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x05, 0xAB
def sensor_sleep():
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
# PM Sensor SetUp
pmSensorSetUp()

#def turnOffUsb():
#   bashCommand = "cwm --rdf test.rdf --ntriples > test.nt"
#   import subprocess
#   process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
#   output, error = process.communicate()

#Main loop
while True:
  logging.info("New measure")
  logging.info("------------------------------------------------------------------------")
  logging.info("Getting temperature and humidity")
  humidity, temperature = getTmpAndHumid()
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
  display = lcddriver.lcd()
  displayLCD(humidity, temperature, pm10, pm25)
  displayLCD(humidity, temperature, pm10, pm25)

  print("Saving data to Firebase . . . .  ")
  logging.info("Saving data to Firebase. . . ")
  db.child(SENSOR_SERIAL_NUMBER).push(data)
  
  print("Data saved!")
  logging.info("Data saved!")
 
  time.sleep(DATA_DELAY_TIME)

#EOF
