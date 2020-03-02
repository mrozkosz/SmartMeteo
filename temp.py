import os
import glob
import pyrebase
import Adafruit_DHT

#from RPLCD import CharLCD
from RPi import GPIO
import time
import lcddriver
import json

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
def get_data():
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        if  humidity is not None and temperature is not None:
                print("Temperatura={0:1f}*C Wilgotnosc={1:0.1f}%".format(temperature, humidity))
                isDeclared = 'true'
		timestamp = int(time.time())
                data["tempC"] =temperature
		data["humi"] = humidity
		#  = {"tempC": temperature, "humi": humidity}
                #db.child("SM-001").child(timestamp).set(data)
        else:
                print("Blad pobrania danych")
def displayLCD():
	try:
		#temp = json.loads(data)
		#print(data)
		display.lcd_clear()
        	display.lcd_display_string("Temperatura:"+str(round(data["tempC"], 1)), 1) # Write line of text to first line of display
        	display.lcd_display_string("Humidity: "+str(round(data["humi"],0)), 2) # Write line of text to second line of display
        	#time.sleep(2)                                     # Give time for the message to be read
        	#display.lcd_display_string("I am a display!", 1)  # Refresh the first line of display with a diffe$
        	#time.sleep(2)                                     # Give time for the message to be read
       		#display.lcd_clear()                               # Clear the display of any data
	except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and $
    		print("Cleaning up!")
    		display.lcd_clear()


while True:
    get_data()
    if isDeclared:
        #print(data)
	displayLCD()
    time.sleep(5)

